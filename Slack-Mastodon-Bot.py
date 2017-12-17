# Slack-Mastodon-Bot - A bot that provides Slack notifications about a Mastodon account's activity.
# Copyright (C) 2017 Logan Fick

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Begin Settings
slack_token = "xoxb-example-token"
slack_channel = "general"

mastodon_email = "example@example.com"
mastodon_password = "supersecurepassword"
mastodon_instance = "https://mstdn.io"
# End Settings

from slackclient import SlackClient
from mastodon import Mastodon
from time import sleep
from os.path import exists

if not exists('client_credentials.secret'):
	print("This appears to be a first run as no Mastodon client credentials were detected. Grabbing...")
	Mastodon.create_app(client_name = 'Slack-Mastodon-Bot', api_base_url = mastodon_instance, to_file = 'client_credentials.secret', scopes = ['read'])
	print("Mastodon client credentials grabbed. This shouldn't need to happen again.")

print("Attempting authentication with Slack...")

slack = SlackClient(slack_token)
authentication_check = slack.api_call('auth.test')
if not authentication_check['ok'] == True:
	if authentication_check['error'] == 'not_authed':
		print("Unable to authenticate with Slack because a token was not provided. Exiting.")
	elif authentication_check['error'] == 'invalid_auth':
		print("Unable to authenticate with Slack because an invalid token was provided. Exiting.")
	else:
		print("Unable to authenticate with Slack. The API error reason was '" + authentication_check['error'] + "'. Exiting.")
	exit()

print("Successfully authenticated with Slack as user '" + authentication_check['user'] + "'. Attempting authentication with Mastodon...")
del authentication_check

mastodon = Mastodon(client_id = 'client_credentials.secret', api_base_url = mastodon_instance)
mastodon.log_in(mastodon_email, mastodon_password, to_file = 'session.secret', scopes = ['read'])
try:
	authentication_check = mastodon.account_verify_credentials()
except:
	print("Unable to authenticate with Mastodon. Exiting.")
	exit()

username = authentication_check['username']
del authentication_check
print("Successfully authenticated with Mastodon as user '" + username + "'. Reading known toots file...")

known_toots = []
if exists('known_toots.txt'):
	with open('known_toots.txt', 'r') as known_toots_file:
		for line in known_toots_file:
			known_toots.append(line[:-1])
	print("Known toots file read. Checking for notifications...")
else:
	known_toots_file = open('known_toots.txt', 'w')
	known_toots_file.close()
	print("Known toots file was not detected, so a new one was created. Checking for notifications...")
del known_toots_file

try:
	notifications = mastodon.notifications()
	skip = False
except:
	print("There appears to be no notifications to handle. Skipping.")
	skip = True

if skip == False:
	print("There is " + str(len(notifications)) + " notification(s) to handle.")
	for number, notification in enumerate(notifications):
		if notification['type'] == 'mention':
			if str(notification['status']['id']) not in known_toots:
				print("Notification #" + str(number) + " is a mention. Posting to Slack...")
				slack.api_call('chat.postMessage', channel='#' + slack_channel, as_user=True, text=notification['status']['url'])
				print("Posted to Slack.")
				known_toots.append(str(notification['status']['id']))
				sleep(1)
			else:
				print("Notification #" + str(number) + " has already been posted in Slack. Skipping.")
		else:
			print("Notification #" + str(number) + " is not a mention. Skipping.")

print("All notifications have been handled. Checking for outgoing messages...")

try:
	timeline = mastodon.timeline_home()
except:
	print("There appears to be no timeline items. Exiting.")
	exit()

print("There is " + str(len(timeline)) + " timeline item(s) to handle.")
for number, toot in enumerate(timeline):
	if toot['account']['username'] == username:
		if str(toot['id']) not in known_toots:
			print("Timeline item #" + str(number) + " is an outgoing message. Posting to Slack...")
			slack.api_call('chat.postMessage', channel='#' + slack_channel, as_user=True, text=toot['url'])
			print("Posted to Slack.")
			known_toots.append(str(toot['id']))
			sleep(1)
		else:
			print("Timeline item #" + str(number) + " has already been posted in Slack. Skipping.")
	else:
		print("Timeline item #" + str(number) + " is not an outgoing message. Skipping.")

print("All timeline items have been handled. Saving known toots file...")
known_toots_file = open('known_toots.txt', 'w')
known_toots_file.seek(0, 0)
for number, toot_id in enumerate(known_toots):
	known_toots_file.write(str(toot_id) + '\n')
known_toots_file.close()

print("All tasks have been completed.")
