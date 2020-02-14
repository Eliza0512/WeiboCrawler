import requests
import rsa
import time
import re
import random
import urllib3
import base64
from urllib.parse import quote
from binascii import b2a_hex
import sys  
import urllib  
import json  
import hashlib  
import os  
import time  
from datetime import datetime  
from datetime import timedelta  
from lxml import etree   
import xlrd
import argparse


## leanring form site http://c.biancheng.net/view/2011.html  Thanks!
## Use http://oa.corp-ci.com/admin.php as example
## this site is company's LAN site, which means 403 when you try it by yourself
## we are going to analyze our daily attendence record

parser = argparse.ArgumentParser()
parser.add_argument('--cookie', required=True, type=str)
parser.add_argument('--begin', required=True, type=str)
parser.add_argument('--keyword', required=True, type=str)


def getResponse(cookie,url,page_limit=51):
    header = {'Host': 's.weibo.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
    'Sec-Fetch-Dest': 'document',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cookie': cookie}
    for i in range(1,page_limit):
        source_url=url + str(i)
        response = requests.get(source_url, headers=header)
        data = response.text
        f= open("hanhong/"+str(i)+".html","w")
        f.write(data)
        f.close()

def setKeyWord(keyword):   
    return keyword.encode("utf-8")

def getKeyWord(keyword):  
    once = urllib.parse.urlencode({"kw":keyword})[3:]  
    return urllib.parse.urlencode({"kw":once})[3:]

cookie = parser.parse_args().cookie
begin = parser.parse_args().begin
keyword = setKeyWord(parser.parse_args().keyword)

url= 'https://s.weibo.com/weibo/'+getKeyWord(keyword)+'&xsort=hot&suball=1&timescope=custom:'+begin+':&page='

getResponse(cookie,url,51)
    
