import os
import time
from time import strptime
import datetime
from datetime import timedelta
import smtplib, ssl # send email notification
from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def send_text(msg, now_string, btc_price):
    # setup email for crypto notification
    port = 465
    email_sender = os.getenv('TEXT_USER')
    email_password = os.getenv('TEXT_PASS')
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL('smtp.gmail.com', port, context=context)

    # where to send text (options == [<phone>@txt.att.net, <phone>@vtext.com, <phone>@tmomail.net, <phone>@messaging.sprintpcs.com])
    savs = ['Tristan', 'Cam', 'Austin', 'Thomas', 'Gspot', 'Matt', 'Alex']
    phone_receivers = ['4097813577@vtext.com', '2819796657@vtext.com', '7138172368@vtext.com', '2817264706@vtext.com', 'aarongisser@gmail.com', 'digoy10@gmail.com']

    # try logging in to email server
    try:
        server.login(email_sender, email_password)
    except:
        print('could not sign in to email')

    # try to send text to each person on mail list
    for i, phone_num in enumerate(phone_receivers):
        try:
            server.sendmail(email_sender, phone_num, msg)
            print('Successfully sent text to {}!'.format(savs[i]))
        except Exception as e:
            print('Could not send text to {}...'.format(savs[i]))

    # print message, append log, cleanly exit server
    print(msg)
    with open('text_log.txt', 'a') as f:
        f.write('{} - BTC price: ${}\n'.format(now_string, btc_price))
    server.quit()

# disable requests warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# get current datetime
now = datetime.datetime.now()
now_string = now.strftime("%Y-%m-%d %H:%M:%S")
now_datetime = datetime.datetime.strptime(now_string, "%Y-%m-%d %H:%M:%S")

# input url to find BTC info, get response from page, and find necessary info
url = 'https://cryptowat.ch'
response = requests.get(url, verify=False)
soup = BeautifulSoup(response.text, 'lxml')
btc = soup.find(title = 'Coinbase Pro BTC/USD')
# account for dynamic HTML changes
try:
    btc_price = btc.find(class_ = 'price').text.replace(',', '')
except:
    btc_price = btc.find(class_ = 'price color-short').text.replace(',', '')

try:
    btc_percent_change = btc.find(class_ = 'color-long').text
except:
    btc_percent_change = btc.find(class_ = 'color-short').text

# create notification flags
percent_float = float(btc_percent_change.replace('-', '').replace('%', ''))
target_price = 35000

# create message to send if price is right
msg = '\r\n\r\nBTC price: ${} \r\nBTC 24 Hr Change: {} \r\nBTFD'.format(btc_price, btc_percent_change)

# create log file for first time
with open('text_log.txt', 'a') as f:
    pass

# open and read the last line of file to see when last text was sent, write first line if file was just created
with open('text_log.txt', 'r') as f:
    try:
        last_line = f.readlines()[-1]
    except:
        with open('text_log.txt', 'a') as f:
            f.write('{} - BTC price: ${}\n'.format(now_string, btc_price))
        with open('text_log.txt', 'r') as f:
            last_line = f.readlines()[-1]

# convert str to datetime and find difference in hours if price is still below threshold
last_text_timestamp = datetime.datetime.strptime(last_line.split(' - ')[0], "%Y-%m-%d %H:%M:%S")
difference = now_datetime - last_text_timestamp

# if time threshold hasn't passed yet, do not send text
if timedelta(hours=12) <= difference and float(btc_price) < target_price:
    send_text(msg, now_string, btc_price)
