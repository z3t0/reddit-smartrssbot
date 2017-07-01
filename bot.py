import praw
import feedparser
import time
from time import mktime
from datetime import datetime

reddit = praw.Reddit('rssbot', user_agent='rpi by /u/z3t0')

subscriptions = []
updated = True
last_checked = None

def getSubscriptions():
    for message in reddit.inbox.messages():
        parsed=message.body.split('\n')
        passed = True

        try:
            get_sub = reddit.subreddit(parsed[0])
        except:
            passed = False

        try:
            feed = feedparser.parse(parsed[1])
        except: passed = False

        if passed:
            subscriptions.append(parsed)


def newSubscriptions():
    global updated
    for message in reddit.inbox.unread():
        parsed=message.body.split('\n')

        passed = True
        
        try:
            get_sub = reddit.subreddit(parsed[0])
        except:
            passed = False
            message.reply("There was an error processing your request.\nPlease make sure that the first line has the sub and the second line has the RSS link")

        try:
            feed = feedparser.parse(parsed[1])
        except:
            passed = False
            message.reply("There was an error processing your request.\nPlease make sure that the first line has the sub and the second line has the RSS link")

        if passed:
            message.reply("Your request has been successfully processed!")
            subscriptions.append(parsed)
            updated = True

        message.mark_read()


def updatePosts():
    global updated
    global last_checked
    for subscription in subscriptions:
        subreddit = reddit.subreddit(subscription[0])
        feed = feedparser.parse(subscription[1])

        for entry in feed.entries:

            post = False

            if last_checked is None:
                post = True

            else:
                pub = datetime.fromtimestamp(mktime(entry.published_parsed))

                if pub > last_checked:
                    post = True

            if post == True:
                try:
                    subreddit.submit(url=entry.link, title=entry.title, resubmit=False)
                except praw.exceptions.APIException as E:
                    print("Failed to submit: sub="+subscription[0] +" rss=" + subscription[1] + " link=" +entry.link)
                    print(E.message)
    updated = False

    last_checked = datetime.now()

getSubscriptions()

timer = 0

while(True):
    newSubscriptions()

    # Only update feeds once a day, or if a new feed is added
    if timer == (60 * 60 * 24) or updated:
        updatePosts()
        updated = False
        timer = 0

    time.sleep(10)

