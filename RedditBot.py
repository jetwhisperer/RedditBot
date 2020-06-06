# Reddit Bot by AlterEffect
# Ensure you register your app with Reddit to get your ID & Secret for the PRAW package
# Praw Documention: https://praw.readthedocs.io/en/latest/
# Also ensure you register for Twilio if you want to use the text message
# Let's get each other some money and use this link: www.twilio.com/referral/Y2VeY0

import praw, csv
from time import sleep
from datetime import datetime
import passwords as secrets
from twilio.rest import Client


def SendTextMessage(recipient, message):
    accountSID = '<Your SID from Twilio>'
    authToken = '<Your Twilio Authentication Token>'
    twilioCli = Client(accountSID, authToken)
    myTwilioNumber = '<Your Twilio Phone NUmber>'

    twilioCli.messages.create(body=message,
                              from_=myTwilioNumber, to=recipient)


reddit = praw.Reddit(client_id='<REDDIT CLIENT ID>',
                     client_secret='<REDDIT SECRET>',
                     password='<REDDIT PASSWORD>',
                     user_agent='Some creative tagline here u/YOU',
                     username='<REDDIT USERNAME')

reddit.read_only = True

# enter the sub, then a list for the items you are looking for in the sub
# any deal in a 'swap' reddit will only look in the HAVE section of the title
deals = {
    'hardwareswap': ['SSD', 'LPX', 'DDR2']
    , 'buildapcsales': ['SSD']
    # ,'steamGameSwap':  ['Bloodstained','No Man\'s Sky']
}

csvfilepath = '<ADD FILE PATH HERE>'

try:
    with open(csvfilepath, 'r') as csvFile:
        seenList = [i.strip().split("|") for i in csvFile]
        LoggedPostIDs = set({item[1] for item in seenList})
except IOError:
    LoggedPostIDs = set()
    open(csvfilepath, 'w+').close()

print('Starting Up...')
while True:
    try:
        for k in deals:
            subreddit = reddit.subreddit(k)
            for submission in subreddit.new(limit=10):
                postID = submission.id
                if postID in LoggedPostIDs:
                    continue
                for i in deals[k]:
                    # if a subreddit that is focused on users selling/trading something (i.e. r/hardwareswap, r/steamgameswap), only looking in the [H]ave Section
                    if i not in submission.title or \
                            ('SWAP' in k.upper() and str(submission.title).find(i) > str(submission.title).find('[W]')):
                        LoggedPostIDs.add(postID)
                        continue

                    # Log the data to a file if it does not exist
                    with open(csvfilepath, 'a', newline='\n') as csvFile:
                        csvWriter = csv.writer(csvFile, delimiter='|')
                        csvWriter.writerow([submission.subreddit
                                               , submission.id
                                               , submission.author
                                               , datetime.fromtimestamp(submission.created_utc)
                                               , submission.title
                                               , submission.url])
                    # Send Text Notification
                    msgbody = str(i) + ' DEAL ALERT IN /r/' + str(submission.subreddit) + '\n' + submission.url
                    SendTextMessage('<Phone Number here i.e. +18888888888>', msgbody)
                    print('New Deal - Text Sent!')
                    LoggedPostIDs.add(postID)


    except KeyboardInterrupt:
        break
    except:
        print('Issue Connecting to reddit')
    # wait 45 seconds; rinse and repeat
    sleep(45)
