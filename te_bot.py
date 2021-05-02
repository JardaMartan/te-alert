#!/usr/bin/env python3
"""Alert Bot for publishing ThousandEyes Alerts in Webex Space.

Copyright (c) 2021 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Jaroslav Martan"
__email__ = "jmartan@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import os
import sys
import re
import uuid
import logging
from dotenv import load_dotenv, find_dotenv

import concurrent.futures
import signal

"""
for AWS Lambda 'dev' vs. 'production' deployment:
In zappa_settings.json set the "environment_variables".

For example:
{
    "dev": {
        "environment_variables": {
            "DOT_ENV_FILE": ".env_dev"
        },
    },
    "prod": {
        "environment_variables": {
            "DOT_ENV_FILE": ".env_prod"
        }
    }
}

Each ".env_something" file can hold a different Bot configuration - identity, database, etc.
Especially identity is important because the Bot always has its own set of webhooks.
So running two AWS Lambda instances ('dev' vs. 'prod' for example) under the same identity
would result in duplicate responses.
""" 
dotenv_file = os.getenv("DOT_ENV_FILE")
if dotenv_file:
    load_dotenv(find_dotenv(dotenv_file))
else:
    load_dotenv(find_dotenv())

from webexteamssdk import WebexTeamsAPI, ApiError, AccessToken
webex_api = WebexTeamsAPI()

import json, requests
from flask import Flask, request, redirect, url_for, make_response

import bot_buttons_cards as bc

DEFAULT_AVATAR_URL= "http://bit.ly/SparkBot-512x512"

flask_app = Flask(__name__)
flask_app.config["DEBUG"] = True
requests.packages.urllib3.disable_warnings()

# threading part
thread_executor = concurrent.futures.ThreadPoolExecutor()

logger = logging.getLogger()

"""
1. initialize database table if needed
2. start event checking thread
"""
@flask_app.before_first_request
def before_first_request():
    me = get_bot_info()
    email = me.emails[0]

    if ("@sparkbot.io" not in email) and ("@webex.bot" not in email):
        flask_app.logger.error("""
You have provided access token which does not belong to a bot ({}).
Please review it and make sure it belongs to your bot account.
Do not worry if you have lost the access token.
You can always go to https://developer.ciscospark.com/apps.html 
URL and generate a new access token.""".format(email))

def get_bot_id():
    bot_id = os.getenv("BOT_ID", None)
    if bot_id is None:
        me = get_bot_info()
        bot_id = me.id
        
    # flask_app.logger.debug("Bot id: {}".format(bot_id))
    return bot_id
    
def get_bot_info():
    try:
        me = webex_api.people.me()
        if me.avatar is None:
            me.avatar = DEFAULT_AVATAR_URL
            
        # flask_app.logger.debug("Bot info: {}".format(me))
        
        return me
    except ApiError as e:
        flask_app.logger.error("Get bot info error, code: {}, {}".format(e.status_code, e.message))
        
def get_bot_name():
    me = get_bot_info()
    return me.displayName
    
@flask_app.before_request
def before_request():
    pass
    
"""
Handle Webex webhook events.
"""
@flask_app.route("/", methods=["GET", "POST"])
def spark_webhook():
    if request.method == "POST":
        webhook = request.get_json(silent=True)
        flask_app.logger.debug("Webex webhook received: {}".format(webhook))
        webex_webhook_event(webhook)        
    elif request.method == "GET":
        bot_info = get_bot_info()
        message = "<center><img src=\"{0}\" alt=\"{1}\" style=\"width:256; height:256;\"</center>" \
                  "<center><h2><b>Congratulations! Your <i style=\"color:#ff8000;\">{1}</i> bot is up and running.</b></h2></center>".format(bot_info.avatar, bot_info.displayName)
                  
        message += "<center><b>I'm hosted at: <a href=\"{0}\">{0}</a></center>".format(request.url)
        res = create_webhook(request.url)
        if res is True:
            message += "<center><b>New webhook(s) created sucessfully</center>"
        else:
            message += "<center><b>Tried to create a new webhook but failed, see application log for details.</center>"

        return message
        
    flask_app.logger.debug("Webhook handling done.")
    return "OK"

# @task
def webex_webhook_event(webhook):
    pass
    
def create_webhook(target_url):
    """create a set of webhooks for the Bot
    webhooks are defined according to the resource_events dict
    
    arguments:
    target_url -- full URL to be set for the webhook
    """    
    flask_app.logger.debug("Create new webhook to URL: {}".format(target_url))
    
    resource_events = {
        "messages": ["created"],
        "memberships": ["created", "deleted"],
        "attachmentActions": ["created"]
    }
    status = None
        
    try:
        check_webhook = webex_api.webhooks.list()
        for webhook in check_webhook:
            flask_app.logger.debug("Deleting webhook {}, '{}', App Id: {}".format(webhook.id, webhook.name, webhook.appId))
            try:
                if not flask_app.testing:
                    webex_api.webhooks.delete(webhook.id)
            except ApiError as e:
                flask_app.logger.error("Webhook {} delete failed: {}.".format(webhook.id, e))
    except ApiError as e:
        flask_app.logger.error("Webhook list failed: {}.".format(e))
        
    for resource, events in resource_events.items():
        for event in events:
            try:
                if not flask_app.testing:
                    webex_api.webhooks.create(name="Webhook for event \"{}\" on resource \"{}\"".format(event, resource), targetUrl=target_url, resource=resource, event=event)
                status = True
                flask_app.logger.debug("Webhook for {}/{} was successfully created".format(resource, event))
            except ApiError as e:
                flask_app.logger.error("Webhook create failed: {}.".format(e))
            
    return status

"""
Handle ThousandEyes webhook events.
"""
@flask_app.route("/te", methods=["POST"])
def te_webhook():
    if request.method == "POST":
        webhook = request.get_json(silent=True)
        flask_app.logger.debug("ThousandEyes webhook received: {}".format(webhook))
        te_webhook_event(webhook)
        
    return "OK"

# @task
def te_webhook_event(webhook):
    attach = None
    
    message = """
ThousandEyes Alert:  
```
{}
```
""".format(json.dumps(webhook, indent=4))

    alert_type = webhook.get("eventType")
    if alert_type == "ALERT_NOTIFICATION_TRIGGER":
        form = bc.ALERT_RAISED_TEMPLATE
    elif alert_type == "ALERT_NOTIFICATION_CLEAR":
        form = bc.ALERT_CLEARED_TEMPLATE
    else:
        form = None
        
    if form:
        form_data = get_te_alert_data(webhook.get("alert"))
        form_data.update(form_data["agents"][0])
        form = bc.nested_replace_dict(form, form_data)
        attach = [bc.wrap_form(bc.localize(form, "en_US"))]

    room_list = get_room_membership()
    for room_id in room_list:
        webex_api.messages.create(roomId = room_id, markdown = message, attachments = attach)
        
def get_te_alert_data(alert):
    result = {}
    if alert is not None:      
        result["rule_expression"] = alert.get("ruleExpression")
        result["test_name"] = alert.get("testName")
        result["permalink"] = alert.get("permalink")
        result["agents"] = []
        for agent in alert.get("agents"):
            result["agents"].append({
                "agent_name": agent.get("agentName"),
                "metrics_at_start": agent.get("metricsAtStart"),
                "metrics_at_end": agent.get("metricsAtEnd")
            })
            
    return result
    
def get_room_membership(room_type = ["direct", "group"]):
    membership_list = webex_api.memberships.list()
    room_list = []
    for membership in membership_list:
        if membership.json_data.get("roomType") in room_type:
            room_list.append(membership.roomId)
    
    flask_app.logger.debug("room membership list: {}".format(room_list))    
    
    return room_list

"""
Startup procedure used to initiate @flask_app.before_first_request
"""
@flask_app.route("/startup")
def startup():
    return "Hello World!"
    
"""
Independent thread startup, see:
https://networklore.com/start-task-with-flask/
"""
def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            logger.info('In start loop')
            try:
                r = requests.get('http://127.0.0.1:5051/startup')
                if r.status_code == 200:
                    logger.info('Server started, quiting start_loop')
                    not_started = False
                logger.debug("Status code: {}".format(r.status_code))
            except:
                logger.info('Server not yet started')
            time.sleep(2)

    logger.info('Started runner')
    thread_executor.submit(start_loop)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', help="Set logging level by number of -v's, -v=WARN, -vv=INFO, -vvv=DEBUG")
    
    args = parser.parse_args()
    if args.verbose:
        if args.verbose > 2:
            logging.basicConfig(level=logging.DEBUG)
        elif args.verbose > 1:
            logging.basicConfig(level=logging.INFO)
        if args.verbose > 0:
            logging.basicConfig(level=logging.WARN)
            
    flask_app.logger.info("Logging level: {}".format(logging.getLogger(__name__).getEffectiveLevel()))
    
    bot_identity = webex_api.people.me()
    # flask_app.logger.info("Bot \"{}\"\nUsing database: {} - {}".format(bot_identity.displayName, os.getenv("DYNAMODB_ENDPOINT_URL"), os.getenv("DYNAMODB_TABLE_NAME")))
    
    start_runner()
    flask_app.run(host="0.0.0.0", port=5051, threaded=True)
