# WordPress-based Calendar with Cisco Webex-Teams Integration

This is a Webex Teams integration for WordPress-based calendar, built using Node.js botkit and Python.  

Capabilities:
- List next 6 upcoming events in MEA Calendar
- Assist a user in a new event creation
- Provide an easy way for admins to get notified when an event is submitted
- Provide an easy way for admins to approve a submitted event via sending a message to the bot

## How to run

0) (One-time) Clone the template files:
- clone .env_template into a new file called .env
- clone env_file-template.py into a new file called env_file.py

1) Update the new files .env and env_file.py with the correct variables.

In .env file, you'll need to specify a PUBLIC_URL for your bot, and a Webex Teams API access token (either in the .env settings or via env variables).  

To update the .env file:
1. Set the PUBLIC_URL variable to the public HTTPS address where the bot is listening (has to be publicly reachable URL on port 3000).  For testing purposes, ngrok (https://ngrok.com) or Serveo (https://serveo.net) can be used.
2. Set the ACCESS_TOKEN variable to the token of the Webex Teams bot to be used. More information on how to get the bot token can be found at https://developer.webex.com

Alternatively, these variables can be passed via environment variables on the CLI.

Note that the values on the command line or in your machine env variables will prevail over .env file settings.

2) (One-time) Install NPM packages:
npm install

3) (One-time) Install the Python packages, preferably in a new virtualenv:
pip install -r requirements.txt

4) Run the node.js bot:
node bot.js

Note: To run the bot while specifying the variables of 1) as runtime variables:
ACCESS_TOKEN=0123456789abcdef PUBLIC_URL=https://abcdef.ngrok.io node bot.js

5) Run the Python monitor scripts, which include built-in schedulers, so no need for external cron schedulers:
$ python check_for_upcoming_events.py
$ python check_for_event_approvals.py


## Authors & Maintainers

Charles Youssef <cyoussef@cisco.com>

## Credits

- botkit-webex-samples from Cisco DevNet: https://github.com/CiscoDevNet/botkit-webex-samples

- MySQL Python Connector: https://dev.mysql.com/doc/connector-python/en/

- Integrating Python scripts into Node.js using child_process.spawn : https://codewithhugo.com/integrate-python-ruby-php-shell-with-node-js/


## License

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).
