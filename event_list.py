#!/usr/bin/env python
"""This is part of the MEA-Calendar Webex-Teams bot functionality.
It connects to the MEA Calendar database and queries the next 6 upcoming events.

This script is called by the botkit event_list.js skill.

"""

import requests
import json
import sys
import datetime
import schedule
import time
import termios
import contextlib
import threading
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


def get_upcoming_events(host, token, date_now_string):
    """calls the metabase query on Yh Posts meta table, using Metabase question 135,
    and checks for the next 6 events based on the event start time.
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

    # to be used to compare the events modified date to:
    now_date = dt.strptime(date_now_string, "%Y-%m-%dT%H:%M:%S")

    result = []

    for event in query_result_dict:
        event_date_string = event["meta_value"].replace(' ','T')
        event_date = dt.strptime(event_date_string, "%Y-%m-%dT%H:%M:%S")
        # convert to same timezone as on running VM:
        event_date = event_date - datetime.timedelta(hours=8)

        if now_date - event_date <= datetime.timedelta(0):
                result.append(event)

        if len(result) > 5:
            break

    return result


def get_upcoming_events_details(host, token, input_event_list):
    """Returns a new list with more details about the events in the original input_event_list list.
    Using Metabase question 132 on the Yb Posts table.
    """
    # temp copy of the input list which gets processed:
    input_event_list_copy = input_event_list

    # result list to be returned after inserting new event parameters:
    result = input_event_list_copy

    yh_meta_posts_url = 'http://%s/api/card/132/query/json' % host

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
                if event['ID'] == input_event['post_id']:
                    index = result.index(input_event)
                    # merge the new event attributes with the original event dictionary
                    result[index].update(event)

    return result


def main():
    """Main executable
    """

    # First authenticate to the Metabase server. Exception handling part of the
    # function itself:
    token = metabase_get_auth_token()["token"]

    # current date in string format "%Y-%m-%dT%H:%M:%S":
    date_now_string = dt.now().isoformat().split('.')[0]

    # The list of events submitted within the last 5 minutes, requiring approvals:
    new_events_list = get_upcoming_events(METABASE_HOST,
        token, date_now_string)

    new_events_detailed_list = get_upcoming_events_details(METABASE_HOST,
        token, new_events_list)

    webex_teams_message = "Here are the next upcoming events in MEA Calendar:\n\n"

    for event in new_events_detailed_list:
        webex_teams_message += "    - %s: %s\n" % (event['meta_value'], event['post_title'])

    webex_teams_message += "\nFor more info, please visit:\n" \
        "https://mea.cisco.com/web/mea-calendar-it/"

    api = WebexTeamsAPI(access_token= TEAMS_BOT_TOKEN)

    if sys.argv[3] == 'direct_mention':
        # message was posted in a teams space, so reply in same space:
        api.messages.create(roomId=sys.argv[2], text= webex_teams_message)

    elif sys.argv[3] == 'direct_message':
        # message was sent unicast to the bot, so reply to the originator unicast:
        api.messages.create(toPersonEmail= sys.argv[1], text= webex_teams_message)

if __name__ == "__main__":
    main()
