import getopt
import json
import sys
import requests
import time
from datetime import datetime, timedelta

def usage():
    print(__doc__)

def generate_epoch(delta):
    """Generates the current epoch timestamp."""
    return int((time.time()- delta) * 1000)

def use_oauth_token(token, api_endpoint):
    """Makes a request to an API using an OAuth token."""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")


def retrieve_token(client_id, client_secret, controller_url):
    payload = 'grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret
    tokenResponse = requests.post(controller_url + "/controller/api/oauth/access_token", data=payload)

    token = ''
    if tokenResponse.status_code == 200:
        token = json.loads(tokenResponse.content.decode('utf-8'))['access_token']
        return token
    else:
        raise Exception(f"API request failed with status code {tokenResponse.status_code}")

def create_app_policy(token, controller_url, appid, actionName):
    #get servers id for controller

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json" 
    }
    
    policy_payload = {
                      "name":"SNOW GreenField Alert Policy",
                      "enabled":True,
                      "executeActionsInBatch":True,
                      "frequency": None,
                      "actions":[{"actionName": actionName,"actionType":"HTTP_REQUEST"}],
                      "events":{"healthRuleEvents":{"healthRuleEventTypes":["HEALTH_RULE_OPEN_WARNING","HEALTH_RULE_OPEN_CRITICAL","HEALTH_RULE_UPGRADED","HEALTH_RULE_DOWNGRADED","HEALTH_RULE_CONTINUES_CRITICAL","HEALTH_RULE_CONTINUES_WARNING","HEALTH_RULE_CLOSE_CRITICAL","HEALTH_RULE_CLOSE_WARNING","HEALTH_RULE_CANCELED_CRITICAL","HEALTH_RULE_CANCELED_WARNING"],
                      "healthRuleScope":{"healthRuleScopeType":"ALL_HEALTH_RULES"}}},"selectedEntities":{"selectedEntityType":"ANY_ENTITY"}}

    
    response = requests.post(controller_url + "/controller/alerting/rest/v1/applications/" + str(appid) + "/policies", json=policy_payload, headers=headers)
    
    if (response.ok):
        print("Policy created for application id: " + str(appid))
    else:
        print("Error Occured in creating Policy. Error Code" + str(response.status_code) + ". Error Response" + response.text)


def create_http_action(token, controller_url, appId, templateName, actionName):
    print("Creating HTTP Action")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json" 
    }

    payload = {
        "actionType": "HTTP_REQUEST",
        "name": actionName,
        "httpRequestTemplateName": templateName,
        "customTemplateVariables": []
    }

    response = requests.post(controller_url + "/controller/alerting/rest/v1/applications/" + str(appId) + "/actions", json=payload, headers=headers)
    
    if (response.ok):
        print("HttpAction created for application id: " + str(appId))
    else:
        print("Error Occured in creating Http Action. Error Code" + str(response.status_code) + ". Error Response" + response.text)



def create_http_template(token, controller_url, templateFile):
    print("Creating http template")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # with open(templateFile, 'r') as f:
    #     template_json = json.load(f)

    files = {'file': open('snow_template.json', 'rb')}

    response = requests.post(controller_url + "/controller/actiontemplate/httprequest", files=files, headers=headers)
    
    if (response.ok):
        print("Http Template successfully created ...")
        print(response.text)
    else:
        print("Error Occured in creating Http Template. Error Code: " + str(response.status_code) + ". Error Response" + response.text)

def main(argv):
    controller_url = ''
    client_id = ''
    client_secret = ""


    # retrieve api token
    token = retrieve_token(client_id, client_secret, controller_url)

    # create snow http template
    create_http_template(token, controller_url, "snow_template.json")
    # create snow http action
    create_http_action(token, controller_url, 22, "ServiceNowGreenFieldTemplate", "ServiceNow_GreenField_HTTPAction")
    
    # create snow http policy
    create_app_policy(token, controller_url, 22, "ServiceNow_GreenField_HTTPAction")

if __name__ == "__main__":
    main(sys.argv[1:])
