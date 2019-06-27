#!/usr/bin/env python
"""This is part of the MEA-Calendar Webex-Teams bot functionality.
It checks for submitted events that require approvals, and sends a notification to the admins on Webex Teams.

The logic is scheduled to run every 5 minutes.

"""

import requests
import json
import sys
import datetime
import schedule
import time
from datetime import datetime as dt
from webexteamssdk import WebexTeamsAPI, ApiError

try:
    import env_file
except (SyntaxError, ModuleNotFoundError):
    print("Invalid input in env_file.py; Please complete the required fields in the proper format.")
    sys.exit(1)

__author__ = "Charles Youssef"
__copyright__ = "Copyright 2019 Cisco and/or its affiliates"
__license__ = "CISCO SAMPLE CODE LICENSE"
__version__ = "1.1"
__email__ = "cyoussef@cisco.com"

try:
    TEAMS_SPACE_ID = env_file.TEAMS_SPACE_ID
    TEAMS_BOT_TOKEN = env_file.BOT_ACCESS_TOKEN
    METABASE_HOST = env_file.METABASE_HOST
    METABASE_USERNAME = env_file.METABASE_USERNAME
    METABASE_PASSWORD = env_file.METABASE_PASSWORD
except (NameError, KeyError):
    print("Invalid input in env_file.py; Please complete the required fields in the proper format.")
    sys.exit(1)


def metabase_get_auth_token(host=METABASE_HOST, username=METABASE_USERNAME,
    password=METABASE_PASSWORD):
    """Helper function to connect to the metabase server and returns the Token
    that will be used in subsequent API calls.
    """
    metabase_auth_url = 'http://%s/api/session' % host
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }

    # get the saved token from the token-file:
    try:
        with open('.metabase_token.txt', 'r', encoding='utf-8') as f:
            saved_token = f.read()
        #print("saved_token is: %s" % saved_token)
    except FileNotFoundError:
        # there is no existing token file.
        # Authenticate using username&password & create a token file
        with open('.metabase_token.txt', 'w+', encoding='utf-8') as f:
            f.write("token_string_will_go_here")
    # Run a test API call to verify if we can authenticate using this token:
    yh_post_meta_url = 'http://%s/api/card/132/query/json' % host
    test_api = requests.post(url=yh_post_meta_url, )
    headers = {
        "Content-Type": "application/json",
        "X-Metabase-Session": saved_token
    }
    test_query_result = requests.post(url=yh_post_meta_url, headers=headers, verify=False)
    if test_query_result.status_code == 401:
        #print("invalid saved token, authenticating with saved user/pass")
        # token is invalid, authenticate using username/password
        try:
            result = requests.post(url=metabase_auth_url, headers=headers, data=json.dumps(payload),
                verify=False)
            result.raise_for_status()
        except:
            print("Unable to authenticate to Metabase server. Please verify " \
                "settings and reachability.")
            sys.exit(1)
        token = result.json()["id"]
        with open('.metabase_token.txt', 'w+', encoding='utf-8') as f:
            f.write(token)
        return {
            "metabase_host": host,
            "token": token
        }
    elif test_query_result.status_code == 200:
        #print("auth using saved token is successful")
        # saved_token is valid, just return it:
        return {
            "metabase_host": host,
            "token": saved_token
        }


def get_new_events_requiring_approvals(host, token, date_now_string):
    """calls the metabase query on Yh Posts table, using Metabase question 132,
    and checks for events that have "post_status" = "future"
    and which were modified within the last 5 minutes.
    """
    yh_post_meta_url = 'http://%s/api/card/132/query/json' % host

    headers = {
        "Content-Type": "application/json",
        "X-Metabase-Session": token
    }
    try:
        query_result = requests.post(url=yh_post_meta_url, headers=headers, verify=False)
    except ConnectionError as error:
        print("Error processing API request to Metabase: %s" % error)
        sys.exit(1)

    query_result_dict = query_result.json()

    # to be used to compare the events modified date to:
    now_date = dt.strptime(date_now_string, "%Y-%m-%dT%H:%M:%S")
    print(now_date)
    result = []

    for event in query_result_dict:
        event_modified_date_string = event["post_modified"].split('.')[0]
        event_modified_date = dt.strptime(event_modified_date_string, "%Y-%m-%dT%H:%M:%S")
        # convert to same timezone as on running VM:
        event_modified_date = event_modified_date - datetime.timedelta(hours=8)
        if event["post_status"] in ["future", "pending"]:
            print(event["post_title"])
            print(event_modified_date)
            print(now_date - event_modified_date)
            # We check if the timedelta is < 5 minutes:
            # Format: class datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes]]]]])
            #if now_date - event_modified_date <= datetime.timedelta(0, 0, 0, 0, 5):
            if now_date - event_modified_date <= datetime.timedelta(0, 0, 0, 0, 60):
                result.append(event)

    return result


def get_event_meta_details(host, token, input_event_list):
    """Lookup the event ID in the input_event_list and return the event details
    using another metabase query on Yh Meta Posts table (question 135).
    The function returns the original list loaded with additional properties for
    each event dictioanry that it contains.
    """
    # temp copy of the input list which gets processed:
    input_event_list_copy = input_event_list

    # result list to be returned after inserting new event parameters:
    result = input_event_list_copy

    yh_meta_posts_url = 'http://%s/api/card/135/query/json' % host

    headers = {
        "Content-Type": "application/json",
        "X-Metabase-Session": token
    }
    try:
        query_result = requests.post(url=yh_meta_posts_url, headers=headers, verify=False)
    except ConnectionError as error:
        print("Error processing API request to Metabase: %s" % error)
        sys.exit(1)

    query_result_dict = query_result.json()

    for event in query_result_dict:
        for input_event in input_event_list_copy:
                if event['post_id'] == input_event['ID']:
                    index = result.index(input_event)
                    # merge the new event attributes with the original event dictionary
                    result[index].update(event)

    return result


def get_author_email_from_author_id(host, token, author_id):
    """lookup the author ID in the Yh Users and return the author email
    string. This uses Metabase question 133:
    """

    yh_users_url = 'http://%s/api/card/133/query/json' % host

    headers = {
        "Content-Type": "application/json",
        "X-Metabase-Session": token
    }
    try:
        query_result = requests.post(url=yh_users_url, headers=headers, verify=False)
    except ConnectionError as error:
        print("Error processing API request to Metabase: %s" % error)
        sys.exit(1)

    query_result_dict = query_result.json()

    result = ''

    for user in query_result_dict:
        if user['ID'] == author_id:
            result = user['user_email']
            break

    return result

def main():
    """Main executable
    """

    print("\nRunning the checker for new events submitted on MEA calendar...\n" \
        "- Checks every 5 minutes for new events submitted which require admin approval\n" \
        "- Sends a notification to the admins on Webex teams space.\n" \
        "- To exit, type 'Ctrl-c'...\n")

    # First authenticate to the Metabase server. Exception handling part of the
    # function itself:
    token = metabase_get_auth_token()["token"]

    # current date in string format "%Y-%m-%dT%H:%M:%S":
    date_now_string = dt.now().isoformat().split('.')[0]

    # The list of events submitted within the last 5 minutes, requiring approvals:
    new_events_requiring_approval_list = get_new_events_requiring_approvals(METABASE_HOST,
        token, date_now_string)
    print(new_events_requiring_approval_list)
    if new_events_requiring_approval_list != []:
         # check for more attributes of the new event
        new_events_requiring_approval_list_plusmeta = get_event_meta_details(METABASE_HOST, token,
            new_events_requiring_approval_list)

        # A tuned version of the new-event dictionary list, containing only required attributes
        # for an event notification on Webex Teams:
        new_events_summary_list = []

        for event in new_events_requiring_approval_list_plusmeta:
            new_events_summary_list.append({
                "event_id": event['ID'],
                "event_title": event['post_title'],
                "event_start_time": event['meta_value'],
                "event_author_email": get_author_email_from_author_id(METABASE_HOST, token,
                    event['post_author'])
                })

        """Sample list for testing only:
        tomorrow_events_summary_list = [{'event_title': 'PIW - The Future of Firewall - Network Security Product Launch Details',
            'event_start_time': '2019-06-04 15:00:00', 'event_author_email': 'cyoussef@cisco.com'},
            {'event_title': 'PIW - Cisco Incident Response Service Overview', 'event_start_time': '2019-06-04 10:30:00',
            'event_author_email': 'cyoussef@cisco.com'}]
        """

        # Initiate the webex teams api:
        api = WebexTeamsAPI(access_token= TEAMS_BOT_TOKEN)

        for event in new_events_summary_list:
            teams_message = """
                New event was submitted to Cisco MEA Calendar:
                - Event ID: %s
                - Event name: %s
                - Event start time: %s
                - Event organizer: %s

                To approve, reply back to the bot with 'event approve' """ % (
                    event['event_id'], event['event_title'], event['event_start_time'], event['event_author_email'])
            try:
                print("Posted to Webex Teams Space a new event: %s" % event['event_title'])
                api.messages.create(roomId=TEAMS_SPACE_ID, text= teams_message)
            except ApiError as e:
                print("Could not post to Webex Teams space.")
                print(e)

    else:
        print("%s: No new submitted or modified-pending events were found in this round." % date_now_string)

    print("%s: Waiting for 5 minutes then re-checking for new approval-pending events. " \
        "To exit, type 'Ctrl-c'..." % date_now_string)

if __name__ == "__main__":
    # Run the program now then repeatedly every 5 minutes
    main()
    schedule.every(5).minutes.do(main)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except (KeyboardInterrupt, EOFError):
            sys.exit(1)
