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
    parser.add_argument('-p', default=80, type=int,
                        help='port for requests')
    parser.add_argument('-d', default=60, type=int,
                        help='delay between requests')
    parser.add_argument('-t', required=True,
                        help='bot token')
    args = parser.parse_args()

    port = args.p
    delay = args.d

    bot = telegram.Bot(token=args.t)
    bot_users = [
        "1562163" # @stask
    ]

    serviceName = "service"

    sentryUrl = os.environ.get('SENTRY_PRIVATE_DSN')
    sentryClient = Client(sentryUrl)


    while True:
        try:
            response = urllib.request.urlopen("http://localhost:{}".format(port), timeout=2)
            code = response.getcode()
            if code != 200:
                notify_about_server_error("{} responded with not ok code {}".format(serviceName, code),
                                          sentryClient, bot, bot_users)
        except Exception as e:
            notify_about_server_error("{} is inaccessible".format(serviceName), sentryClient, bot, bot_users)
        time.sleep(delay)
