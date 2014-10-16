#!/usr/bin/python2.7
# -*- coding:utf-8 -*-
from sdk.weibo import APIClient
import urllib, os, sys
import webbrowser
import urllib2

reload(sys);

sys.setdefaultencoding('utf-8')
USERID = 15656593129
PASSWD = '15298373016'
APP_KEY = '2056098547'
APP_SECRET = '31c8bbaec399d2e2c1d203f7bff7a102'
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
client = APIClient(app_key = APP_KEY,
        app_secret = APP_SECRET, redirect_uri = CALLBACK_URL)
referer_url = client.get_authorize_url()
print 'referer_url is:%s ' %referer_url

#webbrowser.open(url)
#code = 'e11aff4510d64c47642ad8ee18a5bae6'
cookies = urllib2.HTTPCookieProcessor()
opener = urllib2.build_opener(cookies)
urllib2.install_opener(opener)
postdata = {
    "client_id": APP_KEY,
    "redirect_uri": CALLBACK_URL,
    "userId": USERID,
    "passwd": PASSWD,
    "isLoginSina": "",
    "action": "submit",
    "response_type": "code"
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0",
    "Host": "api.weibo.com",
    "Referer": referer_url
}

req = urllib2.Request(url = AUTH_URL, data=urllib.urlencode(postdata), headers=headers)
try:
    resp = urllib2.urlopen(req)
   # print resp.read()
   # print resp.info()
    print 'the callback_url is :%s' % resp.geturl()
    code = resp.geturl()[-32:]
    print 'code is : %s' % code
except Exception, e:
    print e

client = APIClient(app_key = APP_KEY,
        app_secret = APP_SECRET, redirect_uri = CALLBACK_URL)
r = client.request_access_token(code)

access_token = r.access_token
expires_in = r.expires_in
print 'access_token is: %s' % access_token
print 'expiers_in is : %s' % expires_in

client.set_access_token(access_token, expires_in)

uid=5285991999

friendId = []

friendId.append(uid)

db = open('friend.txt', 'w')
c = 0
while len(friendId) > 0 and c < 10:
    c = c+1
    userId = friendId.pop()
    if c == 1:
        friendList = client.friendships.friends.get(uid=userId)
        for r in friendList.users:
            friendId.append(r.id)
  #  content = client.statuses.home_timeline.get(sinceid = 1,count = 100)
    count = client.users.counts.get(uids=userId)
    for i in count:
        userstatus = client.users.show.get(uid = i.id)
        screen_name = userstatus.screen_name
        #print screen_name
        db.write(screen_name+':'+'followers:'+str(i.followers_count)+'friends :'+str(i.friends_count) +'status:'+str(i.statuses_count) )
    
db.close()

print 'end'