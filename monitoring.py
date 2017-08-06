import sys
import os
from raven import Client
import urllib.request
import argparse
import telegram
import time


def notify_about_server_error(msg, sentryClient, bot, bot_users):
    sentryClient.captureMessage(msg)
    for user in bot_users:
        bot.send_message(user, msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bot monitoring')
    parser.add_argument('-port', default=80, type=int,
                        help='port for requests')
    parser.add_argument('-host', default="http://localhost",
                        help='port for requests')
    parser.add_argument('-d', default=60, type=int,
                        help='delay between requests')
    parser.add_argument('-t', required=True,
                        help='bot token')
    parser.add_argument('-u', required=True, nargs='+',
                        help='telegram developer ids')
    args = parser.parse_args()

    port = args.port
    host = args.host
    delay = args.d

    bot = telegram.Bot(token=args.t)
    bot_users = args.u
    serviceName = "service"

    sentryUrl = os.environ.get('SENTRY_MONITORING_PRIVATE_DSN')
    sentryClient = Client(sentryUrl)


    while True:
        try:
            response = urllib.request.urlopen("{}:{}".format(host, port), timeout=2)
            code = response.getcode()
            if code != 200:
                notify_about_server_error("{} responded with not ok code {}".format(serviceName, code),
                                          sentryClient, bot, bot_users)
        except Exception as e:
            notify_about_server_error("{} is inaccessible".format(serviceName), sentryClient, bot, bot_users)
        time.sleep(delay)
