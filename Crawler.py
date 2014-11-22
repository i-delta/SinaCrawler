#!/usr/bin/python2.7
# -*- coding:utf-8 -*-
from sdk.weibo import APIClient
import urllib, os, sys
import webbrowser
import urllib2
from pymongo import MongoClient


CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'

mongo_addr = 'localhost'
mongo_port = 27017
dbname = 'sinaWeibo'

USERID = 15656593129
PASSWD = '15298373016'
APP_KEY = '2056098547'
APP_SECRET ='31c8bbaec399d2e2c1d203f7bff7a102'



class crawler:
    """crawler implementation"""
    def makePostdata(self, app_key, userid, passwd, callback_url):
        """make postdata"""
        self.postdata = {}
        self.postdata['client_id'] = app_key
        self.postdata['redirect_uri'] = callback_url
        self.postdata['userId'] = userid
        self.postdata['passwd'] = passwd
        self.postdata['isLogingSina'] = ""
        self.postdata['action'] = "submit"
        self.postdata['response_type'] = "code"
        
    def makeHeader(self, referer_url):
        """make header """
        self.header = {}
        self.header['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0"
        self.header['Host'] = "api.weibo.com"
        self.header['Referer'] = referer_url
        
    def __init__(self, app_key, app_secret, userid, passwd):
        """construction function"""
        db_client = MongoClient(mongo_addr, mongo_port)
        self.db = db_client[dbname]
        
        self.collection_user_profile = self.db['userprofile']
        self.collection_user_weibo = self.db['weibo']
       # self.postdata = {}
        #self.header = {}
        self.client = APIClient(app_key = app_key,
                   app_secret = app_secret, redirect_uri = CALLBACK_URL)
                   
        self.referer_url = self.client.get_authorize_url()
        # FOR test
        print "the referer_url", self.referer_url
        self.makePostdata(app_key, userid,passwd, CALLBACK_URL)
        self.makeHeader(self.referer_url) 
       
        cookies = urllib2.HTTPCookieProcessor()
        opener = urllib2.build_opener(cookies)
        urllib2.install_opener(opener)        
        req = urllib2.Request(url = AUTH_URL, data=urllib.urlencode(self.postdata), headers=self.header)
        try:
            #webbrowser.open(self.referer_url)
            resp = urllib2.urlopen(req)
            print 'the callback_url is :%s' % resp.geturl()
            self.code = resp.geturl()[-32:]
            print 'code is : %s' % self.code
        except Exception, e:
            print e  
        
    def setAccessToken(self, app_key, app_secret):
        self.client =  APIClient(app_key = app_key,
                   app_secret = app_secret, redirect_uri = CALLBACK_URL)        
        self.r = self.client.request_access_token(self.code)
        # for test
        print "access_token", self.r.access_token
        self.client.set_access_token(self.r.access_token, self.r.expires_in)
      
    def getUserProfile(self, id):
        """get usr profile by user id uid"""
        try:
            userprofile = {}
            userprofile['id'] = id
            profile = self.client.users.show.get(uid=id)
            userprofile['idstr'] = profile['idstr']
            userprofile['screen_name'] = profile['screen_name']
            userprofile['name'] = profile['name']
            userprofile['province'] = profile['province']
            userprofile['city'] = profile['city']
            userprofile['location'] = profile['location']
            userprofile['description'] = profile['description']
            userprofile['url'] = profile['url']
            userprofile['profile_image_url'] = profile['profile_image_url']
            userprofile['profile_url'] = profile['profile_url']
            userprofile['domain'] = profile['domain']
            userprofile['weihao'] = profile['weihao']
            userprofile['gender'] = profile['gender']
            userprofile['followers_count'] = profile['followers_count']
            userprofile['friends_count'] = profile['friends_count']
            userprofile['statuses_count'] = profile['statuses_count']
            userprofile['favourites_count'] = profile['favourites_count']
            userprofile['created_at'] = profile['created_at']
            userprofile['allow_all_act_msg'] = profile['allow_all_act_msg']
            userprofile['geo_enabled'] = profile['geo_enabled']
            userprofile['verified'] = profile['verified']
            userprofile['remark'] = profile['remark']
            userprofile['allow_all_comment'] = profile['allow_all_comment']
            userprofile['avatar_large'] = profile['avatar_large']
            userprofile['avatar_hd'] = profile['avatar_hd']
            userprofile['verified_reason'] = profile['verified_reason']
            userprofile['online_status'] = profile['online_status']
            userprofile['bi_followers_count'] = profile['bi_followers_count']
            userprofile['lang'] = profile['lang']
        except Exception ,e:
            print "get profile exception", e
            
        return userprofile
      
    def getWeibo(self, id):
        """get the weibo content by weibo's id"""
        try:
            weibo = {}
            weibo = self.client.status.show.get(id)
        except Exception, e:
            print "exception in getWeibo", e
        return weibo
    def getWeiboList(self, uid):
        """get uid users' weibo list,
        接口升级后：uid与screen_name只能为当前授权用户，第三方微博类客户端不受影响； """
        try:
            weiboList = {}
            weiboList = self.client.statuses.user_timeline.get(uid)
        except Exception, e:
            print "except in getWeiboList", e
        return weiboList
    def getUidList(self, uid):
        """get the userid list that uid follwos
        接口升级后：uid与screen_name只能为当前授权用户，第三方微博类客户端不受影响；
        最多可获得总关注量30%的用户，上限为500。"""
        try:
            uidlist = {}
            ul = self.client.friendships.friends.ids.get(uid = uid)
            uidlist['ids'] = ul['ids']
            uidlist['next_cursor'] = ul['next_cursor']
            uidlist['previous_cursor'] = ul['previous_cursor']
            uidlist['total_number'] = ul['total_number']
        except Exception , e:
            print "exception raised in getUidlist", e
        return uidlist['ids']
    
    def saveData(self, data):
        self.collection_user_weibo.insert(data)
    
    
def reptile(sina_reptile,userid):
    id_num = 1
    ids = [userid]
    new_ids = [userid]
    ret_ids = []    
    while id_num < 10000:
        next_ids = []
        for uid in new_ids:
            profile = sina_reptile.getUserProfile(uid)
            sina_reptile.saveData(profile)
            ret_ids = sina_reptile.getUidList(uid)
            next_ids.extend(ret_ids)
            id_num = id_num+1
            if(id_num > 10000):
                break
        next_ids, new_ids = new_ids, next_ids




if __name__ == "__main__":
    sinaCrawler = crawler(APP_KEY, APP_SECRET, USERID, PASSWD)
    sinaCrawler.setAccessToken(APP_KEY, APP_SECRET)
    #profile = sinaCrawler.getUserProfile(5285991999)    
    reptile(sinaCrawler, 5285991999)