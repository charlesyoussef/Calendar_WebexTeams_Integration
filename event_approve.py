#!/usr/bin/env python
"""This is part of the MEA-Calendar Webex-Teams bot functionality.
It connects to the MEA Calendar database and approves a pending submitted event.

This script is called by the botkit event_approve.js skill. It gets 3 arguments in sys.argv:
# [1] First arg is the event ID
# [2] Second arg is the email address of the user who sent the message
# [3] Third arg is the room/person ID
# [4] 'direct_mention' or 'direct_message'

"""

import requests
import json
import sys
import datetime
import time
import mysql.connector
from mysql.connector import Error
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
    MYSQL_HOST = env_file.MYSQL_HOST
    MYSQL_DATABASE = env_file.MYSQL_DATABASE
    MYSQL_USER = env_file.MYSQL_USER
    MYSQL_PASSWORD = env_file.MYSQL_PASSWORD
    ADMIN_LIST = env_file.ADMIN_LIST

except (NameError, KeyError):
    print("Invalid input in env_file.py; Please complete the required fields in the proper format.")
    sys.exit(1)

api = WebexTeamsAPI(access_token= TEAMS_BOT_TOKEN)

# sys.argv[2] is the email of the user who sent "event approve" to the bot:
if sys.argv[2].split('@')[0] not in ADMIN_LIST:
    webex_teams_message = "%s is not an admin. Ignoring the 'event approve' request." % sys.argv[2]
    api.messages.create(toPersonEmail= sys.argv[2], text= webex_teams_message)
    sys.exit(1)

if sys.argv[3] != TEAMS_SPACE_ID:
    webex_teams_message = "'event approve' is only supported from within the admins Teams space. " \
        "Ignoring the 'event approve' request."

    if sys.argv[4] == 'direct_mention':
        # message was posted in a teams space, so reply in same space:
        api.messages.create(roomId=sys.argv[3], text= webex_teams_message)

    elif sys.argv[4] == 'direct_message':
        # message was sent unicast to the bot, so reply to the originator unicast:
        api.messages.create(toPersonEmail= sys.argv[2], text= webex_teams_message)

    sys.exit(1)

try:
    conn = mysql.connector.connect(host=MYSQL_HOST, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASSWORD)
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchall()
        print ("Your connected to - ", record)

        # First check if the input event needs to be approved:
        query_get_status = ("SELECT `yh_posts`.`post_status` AS `post_status` FROM `yh_posts` WHERE `yh_posts`.`ID` = %s" % sys.argv[1])

        cursor.execute(query_get_status)

        for status in cursor:
            #print(status)
            if status[0] in ["publish", "draft", "trash"]: # event does not require approval
                webex_teams_message = "Event %s does not require approval. " \
                    "Ignoring the 'event approve' request." % sys.argv[1]

                if sys.argv[4] == 'direct_mention':
                    # message was posted in a teams space, so reply in same space:
                    api.messages.create(roomId=sys.argv[3], text= webex_teams_message)

                elif sys.argv[4] == 'direct_message':
                    # message was sent unicast to the bot, so reply to the originator unicast:
                    api.messages.create(toPersonEmail= sys.argv[2], text= webex_teams_message)

                sys.exit(1)

            elif status[0] in ["pending", "future"]: #event requires approval
                query_update_status = ("UPDATE `yh_posts` SET `yh_posts`.`post_status`='publish' WHERE `yh_posts`.`ID`= %s" % sys.argv[1])

                cursor.execute(query_update_status)
                conn.commit()

                # then repeat the get query to verify the status change:

                query_get_status = ("SELECT `yh_posts`.`post_status` AS `post_status` FROM `yh_posts` WHERE `yh_posts`.`ID` = %s" % sys.argv[1])

                cursor.execute(query_get_status)

                for status in cursor:
                    #print(status)
                    if status[0] == 'publish':
                        api.messages.create(roomId=TEAMS_SPACE_ID, text= "Approved Event ID %s" % sys.argv[1])

            else:
                print("No event found, 2nd else.")
        else:
            api.messages.create(roomId=TEAMS_SPACE_ID, text= "Invalid event ID %s. " \
            "Ignoring the 'event approve' request." % sys.argv[1])


except Error as e :
    print ("Unable to connect to the MySQL Database. ", e)

finally:
    #closing database connection.
    if(conn.is_connected()):
       cursor.close()
       conn.close()
