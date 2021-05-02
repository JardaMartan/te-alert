from unittest import TestCase
from flask.testing import FlaskClient
import te_bot as te
import os
import json

RAISED_ALERT = {
    "eventId": "205646496-76947300",
    "alert": {
        "apiLinks": [
            {
                "rel": "related",
                "href": "https://api.thousandeyes.com/v4/tests/2032597"
            },
            {
                "rel": "data",
                "href": "https://api.thousandeyes.com/v4/web/http-server/2032597"
            }
        ],
        "testLabels": [],
        "active": 1,
        "ruleExpression": "Error Type is \"Connect\" or Response Code is client error (4xx)",
        "type": "HTTP Server",
        "ruleAid": 0,
        "agents": [
            {
                "dateStart": "2021-05-02 10:15:20",
                "active": 1,
                "metricsAtStart": "Response Code: 401",
                "metricsAtEnd": "",
                "permalink": "https://app.thousandeyes.com/alerts/list/?__a=236091&alertId=76947300&agentId=55416",
                "agentId": 55416,
                "agentName": "San Jose, CA (Verizon)"
            }
        ],
        "testTargetsDescription": [
            "https://calliope-a.wbx2.com"
        ],
        "violationCount": 1,
        "dateStart": "2021-05-02 10:15:20",
        "ruleName": "Caliope Connect Error",
        "testId": 2032597,
        "alertId": 76947300,
        "ruleId": 1422847,
        "permalink": "https://app.thousandeyes.com/alerts/list/?__a=236091&alertId=76947300",
        "testName": "https://calliope-a.wbx2.com Cloud"
    },
    "eventType": "ALERT_NOTIFICATION_TRIGGER"
}

CLEARED_ALERT = {
    "eventId": "205647251-76947300",
    "alert": {
        "apiLinks": [
            {
                "rel": "related",
                "href": "https://api.thousandeyes.com/v4/tests/2032597"
            },
            {
                "rel": "data",
                "href": "https://api.thousandeyes.com/v4/web/http-server/2032597"
            }
        ],
        "testLabels": [],
        "active": 2,
        "ruleExpression": "Error Type is \"Connect\" or Response Code is client error (4xx)",
        "dateEnd": "2021-05-02 10:19:17",
        "type": "HTTP Server",
        "ruleAid": 0,
        "agents": [
            {
                "dateStart": "2021-05-02 10:15:20",
                "dateEnd": "2021-05-02 10:19:17",
                "active": 2,
                "metricsAtStart": "Response Code: 401",
                "metricsAtEnd": "N/A (rule modified or removed from test)",
                "permalink": "https://app.thousandeyes.com/alerts/list/?__a=236091&alertId=76947300&agentId=55416",
                "agentId": 55416,
                "agentName": "San Jose, CA (Verizon)"
            }
        ],
        "testTargetsDescription": [
            "https://calliope-a.wbx2.com"
        ],
        "violationCount": 1,
        "dateStart": "2021-05-02 10:15:20",
        "ruleName": "Caliope Connect Error",
        "testId": 2032597,
        "alertId": 76947300,
        "ruleId": 1422847,
        "permalink": "https://app.thousandeyes.com/alerts/list/?__a=236091&alertId=76947300",
        "testName": "https://calliope-a.wbx2.com Cloud"
    },
    "eventType": "ALERT_NOTIFICATION_CLEAR"
}

class BotTest(TestCase):
    
    def setUp(self):
        print("\nsetup {}".format(self.__class__.__name__))
        te.flask_app.testing = True
        self.client = te.flask_app.test_client()
                
    def tearDown(self):
        print("tear down {}".format(self.__class__.__name__))
        
    def test_te_alert_raised(self):
        res = te.get_te_alert_data(RAISED_ALERT.get("alert"))
        print(res)

if __name__ == "__main__":
    unittest.main()
