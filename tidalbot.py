#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tweepy, time, sys
sys.path.append("/home/tidalbot/tidalbot")
import os
from subprocess import call, Popen, PIPE, STDOUT
import config # includes the below keys + secrets for twitter
import re
import requests
import time
from pprint import pprint

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_KEY, config.ACCESS_SECRET)
api = tweepy.API(auth)

import string, time, math, random

def uniqid():
    m = time.time()
    uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
    return uniqid

def process_status(status):
    print(status.text)
    call(["killall", "jackd"])
    time.sleep(2)
    matcher = re.compile(r'@tidalbot\s*')
    code = matcher.sub('', status.text)
    #code = code.decode('unicode_escape').encode('ascii', 'ignore')
    print("code: " + code)
    fnid = uniqid()
    fn = "/var/www/alex/slab.org/patterns/" + fnid + ".mp3"
    url = "http://slab.org/patterns/" + fnid + ".mp3"
    p = Popen(['./runpattern', fn], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    tidalout = p.communicate(input=code)[0]
    print(tidalout.decode())
    print("return code: " + str(p.returncode))
    if p.returncode == 0:
        m = ".@%s Listen: %s" % (status.user.screen_name, url)
        api.update_status(m, in_reply_to_status_id = status.id)
    else:
        m = "@%s Sorry there's something wrong with that pattern" % (status.user.screen_name)
        api.update_status(m, in_reply_to_status_id = status.id)

class TidalbotListener(tweepy.StreamListener):

    def on_status(self, status):
        process_status(status)

if len(sys.argv) > 1:
    for id in sys.argv[1:]:
      status = api.get_status(id)
      process_status(status)
else:
    tidalbotListener = TidalbotListener()
    stream = tweepy.Stream(auth = api.auth, listener=tidalbotListener)

    stream.filter(track=['@tidalbot'])
