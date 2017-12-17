# Slack-Mastodon-Bot

A bot that provides Slack notifications about a Mastodon account's activity.

# Requirements
- Python 3
- [Mastodon.py](https://github.com/halcy/Mastodon.py)
- [SlackClient](https://github.com/slackapi/python-slackclient)

# Installation
1. [Create a new bot user](https://my.slack.com/services/new/bot) on your Slack team and make note of the authentication token.
2. Clone the repository to a system that has high uptime.
3. Configure the settings in `Slack-Mastodon-Bot.py`.
4. Run `Slack-Mastodon-Bot.py` manually to intiailize the bot and ensure there are no errors.
5. Using a service like crontab, add a rule to run the script every 5 minutes. If you like fast updates, then you can use 1 minute instead.
