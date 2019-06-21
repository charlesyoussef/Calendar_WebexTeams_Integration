#!/usr/bin/env python
"""This is part of the MEA-Calendar Webex-Teams bot functionality.
It checks the approved events in MEA Calendar, and sends a notification reminder
message on Webex Teams to the organizer, for the event(s) that start(s) the next day.

The script is scheduled to run the task once per day at 9AM.

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
    try:
        result = requests.post(url=metabase_auth_url, headers=headers, data=json.dumps(payload),
            verify=False)
        result.raise_for_status()
    except:
        print("Unable to authenticate to Metabase server. Please verify " \
            "settings and reachability.")
        sys.exit(1)

    token = result.json()["id"]
    return {
        "metabase_host": host,
        "token": token
    }

def get_events_meta_starting_tomorrow(host, token, date_now_string):
    """calls the metabase query on Yh Post Meta table, using Metabase question 135,
    and returns a list of events that start tomorrow.
    """
    yh_post_meta_url = 'http://%s/api/card/135/query/json' % host

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

    # to be used to compare the events starting date to:
    today_date = dt.strptime(date_now_string, "%Y-%m-%d")

    result = []

    for event in query_result_dict:
        event_date_string = event["meta_value"].split()[0]
        event_date = dt.strptime(event_date_string, "%Y-%m-%d")

        # This is a timedelta of 1 day:
        if event_date - today_date == datetime.timedelta(1):
            result.append(event)

    return result


def get_event_details_starting_tomorrow(host, token, tomorrows_event_meta_list):
    """Lookup the event ID in the event_meta_list and return the event details
    using another metabase query on Yh Posts table (question 132).
    The function returns the original list loaded with additional properties for
    each event dictioanry that it contains.
    """
    # temp copy of the input list which gets processed:
    tomorrow_events = tomorrows_event_meta_list

    # result list to be returned after inserting new event parameters:
    result = tomorrows_event_meta_list

    yh_posts_url = 'http://%s/api/card/132/query/json' % host

    headers = {
        "Content-Type": "application/json",
        "X-Metabase-Session": token
    }
    try:
        query_result = requests.post(url=yh_posts_url, headers=headers, verify=False)
    except ConnectionError as error:
        print("Error processing API request to Metabase: %s" % error)
        sys.exit(1)

    query_result_dict = query_result.json()

    for event in query_result_dict:
        # Check first that the event is published:
        if event['post_status'] == 'publish':
            for tomorrow_event in tomorrow_events:
                if event['ID'] == tomorrow_event['post_id']:
                    index = result.index(tomorrow_event)
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
    print("Running the notification script for MEA calendar events...\n" \
        "- It checks every day at 9AM for events starting the next day\n" \
        "- and sends a reminder via Webex Teams to the corresponding event owner.\n")

    # First authenticate to the Metabase server. Exception handling part of the
    # function itself:
    token = metabase_get_auth_token()["token"]

    # current date in string format YYYY-MM-DD:
    date_now_string = dt.now().isoformat().split('T')[0]

    # The list of events that start tomorrow, having the first subset of the event properties:
    tomorrows_event_meta_list = get_events_meta_starting_tomorrow(METABASE_HOST, token, date_now_string)

    if tomorrows_event_meta_list == []:
        print("%s: No events starting tomorrow were found" % date_now_string)

    # The list of dictionaries is loaded with additional event attributes in each dictionary:
    tomorrows_event_detail_list = get_event_details_starting_tomorrow(METABASE_HOST, token,
        tomorrows_event_meta_list)

    # A tuned version of the event dictionary list, containing only required attributes
    # for an event notification on Webex Teams:
    tomorrow_events_summary_list = []

    for event in tomorrows_event_detail_list:
        tomorrow_events_summary_list.append({"event_title": event['post_title'],
            "event_start_time": event['meta_value'],
            "event_author_email": get_author_email_from_author_id(METABASE_HOST, token,
                event['post_author'])
            })

    """Sample list for testing only:
    tomorrow_events_summary_list = [{'event_title': 'Test1',
    'event_start_time': '2019-06-04 15:00:00', 'event_author_email': 'abc@cisco.com'},
    {'event_title': 'Test2', 'event_start_time': '2019-06-04 10:30:00',
    'event_author_email': 'abc@cisco.com'}]
    """

    # Initiate the webex teams api:
    api = WebexTeamsAPI(access_token= TEAMS_BOT_TOKEN)

    for event in tomorrow_events_summary_list:
        teams_message = "Reminder about your upcoming event in Cisco MEA Calendar:"
        teams_message += "\n- Event name: %s" % event['event_title']
        teams_message += "\n- Event start time: %s" % event['event_start_time']
        try:
            print("Posted reminder message to Webex Teams to %s about %s event scheduled for %s" % (
                event['event_author_email'], event['event_title'], event['event_start_time']))
            api.messages.create(toPersonEmail= event['event_author_email'],
                text= teams_message)
        except ApiError as e:
            print(e)
            sys.exit(1)

if __name__ == "__main__":
    # Run the program now then repeatedly every day at 9AM.
    main()
    schedule.every().day.at("09:00").do(main)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except (KeyboardInterrupt, EOFError):
            sys.exit(1)
