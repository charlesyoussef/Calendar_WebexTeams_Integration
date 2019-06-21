#!/usr/bin/env python
"""
This is part of the MEA-Calendar Webex-Teams bot functionality.
It creates a new event in the MEA-Calendar based on user input passed from the botkit bot.
The link to event_create.js is not done yet. It will be added in a next version.

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

"""
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
"""
try:
    conn = mysql.connector.connect(host=MYSQL_HOST, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASSWORD)
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchall()
        print ("Your connected to - ", record)

        # Get the user (author) id from users table, in variable author_id:
        get_author_query = ("SELECT `ID` FROM `yh_users` WHERE `user_email` = '%s'" % "abc@cisco.com")

        cursor.execute(get_author_query)

        for user in cursor:
            print(user)
            author_id = user[0]
            break

        else:
            print("User not found. Please register at mea.cisco.com")
            sys.exit(1)

        # Then insert the event in yh_posts table:
        update_query = ("INSERT INTO `yh_posts` "
        "(`post_title`, `post_name`, `post_type`,  `menu_order`, `post_author`, `post_content`,   `post_parent`, `post_status`, `post_modified_gmt`, `post_date_gmt`, `post_modified`, `post_date`)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        date_now = dt.now().isoformat()
        date_now_gmt = dt.utcnow().isoformat()
        data_new_event = ('', '', 'events', 0, author_id, '', 0, 'pending', date_now_gmt, date_now_gmt, date_now, date_now)

        cursor.execute(update_query, data_new_event)
        conn.commit()

        # Then get the event ID of the inserted event:
        # old query:
        # new_event_query = ("SELECT `ID` FROM `yh_posts` WHERE (`post_author` = %s and `post_title` = %s and `post_modified` = %s)" % (author_id, 'TestPYEV2', date_now.split('.')[0].replace('T', ' ')))

        new_event_query = ("SELECT `ID` FROM `yh_posts` WHERE (`post_author` = %s and `post_title` = %s)" % (author_id, ''))

        cursor.execute(new_event_query)

        for id in cursor:
            print(id)
            new_event_id = id[0]

        # Then insert the event in the posts meta table:

        # for testing: posts_meta_query = ("SELECT `meta_id`, `meta_key`, `meta_value`, `post_id` FROM `yh_postmeta` WHERE `yh_postmeta`.`post_id` = ")
        update_query_meta = ("INSERT INTO `yh_postmeta` "
        "(`meta_key`, `meta_value`, `post_id`)"
        "VALUES (%s, %s, %s)")

        new_event_meta1 = ('fc_end_datetime', '2019-06-26 00:00:00', )
        cursor.execute(update_query_meta, new_event_meta1)

        new_event_meta2 = ('fc_start_datetime', '2019-06-25 00:00:00', )
        cursor.execute(update_query_meta, new_event_meta2)

        new_event_meta3 = ('audience', 'sales, technical', )
        cursor.execute(update_query_meta, new_event_meta3)

        new_event_meta4 = ('enable_postinfo', 1, )
        cursor.execute(update_query_meta, new_event_meta4)

        new_event_meta5 = ('fc_start_time', "00:00", )
        cursor.execute(update_query_meta, new_event_meta5)

        new_event_meta6 = ('fc_start', "2019-06-25", )
        cursor.execute(update_query_meta, new_event_meta6)

        new_event_meta7 = ('fc_end', "2019-06-26", )
        cursor.execute(update_query_meta, new_event_meta7)

        new_event_meta8 = ('fc_range_start', "2019-06-25 00:00:00", )
        cursor.execute(update_query_meta, new_event_meta8)

        new_event_meta9 = ('fc_range_end', "2019-06-26 00:00:00", )
        cursor.execute(update_query_meta, new_event_meta9)

        new_event_meta10 = ('fc_color', '#', )
        cursor.execute(update_query_meta, new_event_meta10)

        new_event_meta11 = ('fc_text_color', '#', )
        cursor.execute(update_query_meta, new_event_meta11)

        new_event_meta12 = ('fc_allday', 0, )
        cursor.execute(update_query_meta, new_event_meta12)

        new_event_meta13 = ('enable_featuredimage', 1, )
        cursor.execute(update_query_meta, new_event_meta13)

        new_event_meta14 = ('enable_postinfo_image', 1, )
        cursor.execute(update_query_meta, new_event_meta14)

        new_event_meta15 = ('enable_venuebox', 1, )
        cursor.execute(update_query_meta, new_event_meta15)

        new_event_meta16 = ('enable_venuebox_gmap', 1, )
        cursor.execute(update_query_meta, new_event_meta16)

        conn.commit()


        for (a,b,c,d) in cursor:
            print(a, b, c, d)


        query_get_status = ("SELECT `yh_posts`.`post_status` AS `post_status` FROM `yh_posts` WHERE `yh_posts`.`post_author` = %s" % )

        cursor.execute(query_get_status)

        for ev in cursor:
            print(ev)

        else:
            print("Invalid event ID")

except Error as e :
    print ("Unable to connect to the MySQL Database. ", e)

finally:
    #closing database connection.
    if(conn.is_connected()):
       cursor.close()
       conn.close()
