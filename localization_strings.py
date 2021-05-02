from unidecode import unidecode

# language list which is presented in settings
LANGUAGES = {
    "en_US": "English"
}

def lang_list_for_card():
    lan_list = []
    for (key, value) in LANGUAGES.items():
        lan_list.append({"title": value, "value": key})
        
    lan_list.sort(key=lambda x: unidecode(x["title"]).lower())
    
    return lan_list

EN_US = {
    "loc_default_form_msg": "This is a form. It can be displayed in a Webex app or web client.",
}

# add the previously defined language constant to make it available for the Bot
LOCALES = {
    "en_US": EN_US
}
