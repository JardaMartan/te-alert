import localization_strings as ls

def wrap_form(form):
    card = EMPTY_CARD
    card["content"] = form
    
    return card

def nested_replace(structure, original, new):
    """replace {{original}} wrapped strings with new value
    use recursion to walk the whole sructure
    
    arguments:
    structure -- input dict / list / string
    original -- string to search for
    new -- will replace every occurence of {{original}}
    """
    if type(structure) == list:
        return [nested_replace( item, original, new) for item in structure]

    if type(structure) == dict:
        return {key : nested_replace(value, original, new)
                     for key, value in structure.items() }

    if type(structure) == str:
        return structure.replace("{{"+original+"}}", str(new))
    else:
        return structure
        
def nested_replace_dict(structure, replace_dict):
    """replace multiple {{original}} wrapped strings with new value
    use recursion to walk the whole sructure
    
    arguments:
    structure -- input dict / list / string
    replace_dict -- dict where key matches the {{original}} and value provides the replacement
    """
    for (key, value) in replace_dict.items():
        structure = nested_replace(structure, key, value)
        
    return structure
    
def localize(structure, language):
    """localize structure using {{original}} wrapped strings with new value
    use recursion to walk the whole sructure
    
    arguments:
    structure -- input dict / list / string
    language -- language code which is used to match key in ls.LOCALES dict
    """
    if not language in ls.LOCALES.keys():
        return structure
        
    lang_dict = ls.LOCALES[language]
    return nested_replace_dict(structure, lang_dict)

# wrapper structure for Webex attachments list        
EMPTY_CARD = {
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": None,
}

# default text message attached to a buttons & cards form
DEFAULT_FORM_MSG = "{{loc_default_form_msg}}"

ALERT_RAISED_TEMPLATE = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "Image",
                            "size": "Small",
                            "url": "https://img.icons8.com/fluent/96/000000/error.png"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "ALERT RAISED",
                            "horizontalAlignment": "Right",
                            "spacing": "None",
                            "size": "Large",
                            "color": "Attention"
                        }
                    ]
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "{{rule_expression}}",
            "wrap": True,
            "color": "Attention",
            "weight": "Bolder"
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Test name",
                            "wrap": True,
                            "weight": "Bolder"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "{{test_name}}",
                            "wrap": True,
                            "horizontalAlignment": "Right",
                            "weight": "Bolder"
                        }
                    ],
                    "horizontalAlignment": "Right"
                }
            ]
        },
        {
            "type": "ColumnSet",
            "separator": True,
            "spacing": "Medium",
            "columns": [
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Agent",
                            "isSubtle": True,
                            "weight": "Bolder"
                        },
                        {
                            "type": "TextBlock",
                            "text": "{{agent_name}}",
                            "spacing": "Small"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Status",
                            "isSubtle": True,
                            "weight": "Bolder",
                            "horizontalAlignment": "Right"
                        },
                        {
                            "type": "TextBlock",
                            "text": "{{metrics_at_start}}",
                            "horizontalAlignment": "Right",
                            "spacing": "Small"
                        }
                    ],
                    "horizontalAlignment": "Right"
                }
            ]
        },
        {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "Alert Details",
                    "url": "{{permalink}}"
                }
            ],
            "horizontalAlignment": "Right"
        }
    ]
}

ALERT_CLEARED_TEMPLATE = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "Image",
                            "size": "Small",
                            "url": "https://img.icons8.com/fluent/96/000000/ok.png"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "ALERT CLEARED",
                            "horizontalAlignment": "Right",
                            "spacing": "None",
                            "size": "Large",
                            "color": "Good"
                        }
                    ]
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "{{rule_expression}}",
            "wrap": True,
            "color": "Good",
            "weight": "Bolder"
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Test name",
                            "wrap": True,
                            "weight": "Bolder"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "{{test_name}}",
                            "wrap": True,
                            "horizontalAlignment": "Right",
                            "weight": "Bolder"
                        }
                    ],
                    "horizontalAlignment": "Right"
                }
            ]
        },
        {
            "type": "ColumnSet",
            "separator": True,
            "spacing": "Medium",
            "columns": [
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Agent",
                            "isSubtle": True,
                            "weight": "Bolder"
                        },
                        {
                            "type": "TextBlock",
                            "text": "{{agent_name}}",
                            "spacing": "Small"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Status",
                            "isSubtle": True,
                            "weight": "Bolder",
                            "horizontalAlignment": "Right"
                        },
                        {
                            "type": "TextBlock",
                            "text": "{{metrics_at_start}}",
                            "horizontalAlignment": "Right",
                            "spacing": "Small"
                        }
                    ],
                    "horizontalAlignment": "Right"
                }
            ]
        },
        {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "Alert Details",
                    "url": "{{permalink}}"
                }
            ],
            "horizontalAlignment": "Right"
        }
    ]
}
