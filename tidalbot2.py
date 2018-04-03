#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tweepy, time, sys
import os
from subprocess import call, Popen, PIPE, STDOUT
import config # includes the below keys + secrets for twitter
import re
import requests
import liblo
import time
from websocket import create_connection
from pprint import pprint
import string, math, random
import html

target = liblo.Address(9162)

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_KEY, config.ACCESS_SECRET)
api = tweepy.API(auth)


def uniqid():
    m = time.time()
    uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
    return uniqid

def process_status(status):
    try:
        text = status.extended_tweet["full_text"]
    except AttributeError:
        text = status.text

    print(text)

    #call(["killall", "jackd"])
    #time.sleep(2)
    matcher = re.compile(r'@tidalbot\s*')
    code = matcher.sub('', text)
    #code = code.decode('unicode_escape').encode('ascii', 'ignore')
    code = html.unescape(code)
    code = code.translate(str.maketrans('“”','""'))
    ws = create_connection("ws://localhost:9162/")
    msg = ws.recv()
    print(msg)
    ws.send("/record " + code)
    print("code: " + code)
    msg = ws.recv();
    print("got: " + msg)
    match = re.search(r'^/record\s+(ok|nok)\s+((?:.|\n)*)', msg)
    if (match):
        (ok, path) = match.groups()
        print("got status: " + ok + " path " + path)
        if ok == "ok":
            print("ok!")
            url = "http://douglas.lurk.org/" + path
            m = ".@%s Listen: %s" % (status.user.screen_name, url)
            matcher = re.compile(r'mp3$')
            imagepath = "../tidal-websocket/" + matcher.sub('png', path)
            #api.update_status(m, in_reply_to_status_id = status.id)
            api.update_with_media(imagepath, status=m, in_reply_to_status_id = status.id)
            pdfpath = "../tidal-websocket/" + matcher.sub('pdf', path)
            call(["scp", "-P", "2222", pdfpath, "pi@localhost:pattern/display.pdf"])
            call(["scp", "-P", "2223", pdfpath, "pi@localhost:pattern/display.pdf"])
        else:
            m = "@%s Oh dear. %s" % (status.user.screen_name, path)
            print("sending: " + m)
            m  = (m[:275] + '..') if len(m) > 273 else m
            api.update_status(m, in_reply_to_status_id = status.id)

class TidalbotListener(tweepy.StreamListener):

    def on_status(self, status):
        process_status(status)

if len(sys.argv) > 1:
    for id in sys.argv[1:]:
      status = api.get_status(id, tweet_mode='extended')
      process_status(status)
else:
    tidalbotListener = TidalbotListener()
    stream = tweepy.Stream(auth = api.auth, listener=tidalbotListener)
    print(stream)
    stream.filter(track=['@tidalbot'])
