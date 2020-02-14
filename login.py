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


## Reference https://www.cnblogs.com/woaixuexi9999/p/9404745.html

urllib3.disable_warnings() # 取消警告

def get_timestamp():
    return int(time.time()*1000)  # 获取13位时间戳

class WeiBo():
    def __init__(self,username,password, keyword, startTime, interval='50', flag=True, begin_url_per = "http://s.weibo.com/weibo/"):
        self.username = username
        self.password = password
        self.session = requests.session() #登录用session
        self.session.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        self.session.verify = False  # 取消证书验证
        self.begin_url_per = begin_url_per  #设置固定地址部分  
        self.setKeyword(keyword)    #设置关键字  
        self.setStartTimescope(startTime)   #设置搜索的开始时间  
        #self.setRegion(region)  #设置搜索区域  
        self.setInterval(interval)  #设置邻近网页请求之间的基础时间间隔（注意：过于频繁会被认为是机器人）  
        self.setFlag(flag)    
        # self.logger = logging.getLogger('main.CollectData') #初始化日志  

    def prelogin(self):
        '''预登录，获取一些必须的参数'''
        self.su = base64.b64encode(self.username.encode())  #阅读js得知用户名进行base64转码
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'.format(quote(self.su),get_timestamp()) #注意su要进行quote转码
        response = self.session.get(url).content.decode()
        # print(response)
        self.nonce = re.findall(r'"nonce":"(.*?)"',response)[0]
        self.pubkey = re.findall(r'"pubkey":"(.*?)"',response)[0]
        self.rsakv = re.findall(r'"rsakv":"(.*?)"',response)[0]
        self.servertime = re.findall(r'"servertime":(.*?),',response)[0]
        return self.nonce,self.pubkey,self.rsakv,self.servertime

    def get_sp(self):
        '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(self.pubkey,16),int('10001',16))
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.password)
        self.sp = rsa.encrypt(message.encode(),publickey)
        return b2a_hex(self.sp)

    def login(self):
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
        'entry': 'weibo',
        'gateway': '1',
        'from':'',
        'savestate': '7',
        'qrcode_flag': 'false',
        'useticket': '1',
        'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
        'vsnf': '1',
        'su': self.su,
        'service': 'miniblog',
        'servertime': str(int(self.servertime)+random.randint(1,20)),
        'nonce': self.nonce,
        'pwencode': 'rsa2',
        'rsakv': self.rsakv,
        'sp': self.get_sp(),
        'sr': '1536 * 864',
        'encoding': 'UTF - 8',
        'prelt': '35',
        'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META',
        }
        response = self.session.post(url,data=data,allow_redirects=False).text # 提交账号密码等参数
        redirect_url = re.findall(r'location.replace\("(.*?)"\);',response)[0] # 微博在提交数据后会跳转，此处获取跳转的url
        result = self.session.get(redirect_url,allow_redirects=False).text  # 请求跳转页面
        ticket,ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"',result)[0] #获取ticket和ssosavestate参数
        uid_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(ticket,ssosavestate,get_timestamp())
        data = self.session.get(uid_url).text #请求获取uid
        uid = re.findall(r'"uniqueid":"(.*?)"',data)[0]
        sprint(uid)
        #home_url = 'https://weibo.com/u/{}/home?wvr=5&lf=reg'.format(uid) #请求首页
        #html = self.session.get(home_url)
        #html.encoding = 'utf-8'
        #print(html.text)
        print(" Login Success! ")
  
    ##设置关键字  
    ##关键字需解码后编码为utf-8  
    def setKeyword(self, keyword):  
        #self.keyword = keyword.decode('GBK','ignore').encode("utf-8")  
        self.keyword = keyword.encode("utf-8")
        print('twice encode:',self.getKeyWord())
  
    ##关键字需要进行两次urlencode  
    def getKeyWord(self):  
        once = urllib.parse.urlencode({"kw":self.keyword})[3:]  
        return urllib.parse.urlencode({"kw":once})[3:]          
          
    ##设置起始范围，间隔为1天  
    ##格式为：yyyy-mm-dd  
    def setStartTimescope(self, startTime):  
        if not (startTime == '-'):  
            self.timescope = startTime+":" 
        else:  
            self.timescope = '-'  
  
    ##设置搜索地区  
    #def setRegion(self, region):  
    #    self.region = region  
  
    ##设置邻近网页请求之间的基础时间间隔  
    def setInterval(self, interval):  
        self.interval = int(interval)  
  
    ##设置是否被认为机器人的标志。若为False，需要进入页面，手动输入验证码  
    def setFlag(self, flag):  
        self.flag = flag  
  
    ##构建URL  
    def getURL(self):  
        # return self.begin_url_per+self.getKeyWord()+"&typeall=1&suball=1×cope=custom:"+self.timescope+"&page="  
        # return self.begin_url_per+self.getKeyWord()+"?topnav=1&wvr=6&b=1"+"&page="
        return self.begin_url_per+self.getKeyWord()+"&xsort=hot&suball=1&timescope=custom:"+self.timescope+":&page="
    ##爬取一次请求中的所有网页，最多返回50页  
    def download(self, url, maxTryNum=4):  
        hasMore = True  #某次请求可能少于50页，设置标记，判断是否还有下一页  
        # isCaught = False    #某次请求被认为是机器人，设置标记，判断是否被抓住。抓住后，需要，进入页面，输入验证码  
        # name_filter = set([])    #过滤重复的微博ID  
          
        i = 1   #记录本次请求所返回的页数  
        while hasMore and i < 51:    #最多返回50页，对每页进行解析，并写入结果文件  
            source_url = url + str(i)   #构建某页的URL  
            print(source_url)
            data = ''   #存储该页的网页数据  
            goon = True #网络中断标记  
            ##网络不好的情况，试着尝试请求三次  
            for tryNum in range(maxTryNum):  
                try:  
                    html = urllib.request.urlopen(source_url, timeout=12)  
                    data = html.read()  
                    break  
                except:  
                    if tryNum < (maxTryNum-1):  
                        time.sleep(10)  
                    else:  
                        print( 'Internet Connect Error!'  ) 
            if goon:
                # print(isinstance(data,bytes))  
                data = str(data, encoding = "utf8")
                print(data)
                lines = data.splitlines()   
                f_query1 = open("html/"+str(i)+".html","w")
                f_query1.write(data)
                f_query1.close()
                lines = None  
                ## 没有更多结果，结束该次请求，跳到下一个请求  
                if not hasMore:  
                    print ('No More Results!'  )
                    if i == 1:  
                        time.sleep(random.randint(3,8))  
                    else:  
                        time.sleep(10)  
                    data = None  
                    break  
                i += 1  
                ## 设置两个邻近URL请求之间的随机休眠时间，防止Be Caught  
                sleeptime_one = random.randint(self.interval-25,self.interval-15)  
                sleeptime_two = random.randint(self.interval-15,self.interval)  
                if i%2 == 0:  
                    sleeptime = sleeptime_two  
                else:  
                    sleeptime = sleeptime_one  
                print ('sleeping ' + str(sleeptime) + ' seconds...' ) 
                time.sleep(sleeptime)  
            else:  
                break  
  
    ##改变搜索的时间范围，有利于获取最多的数据     
    def getTimescope(self, perTimescope):  
        if not (perTimescope=='-'):  
            times_list = perTimescope.split(':')  
            start_date =  datetime(int(times_list[-1][0:4]),  int(times_list[-1][5:7]), int(times_list[-1][8:10]) )   
            start_new_date = start_date + timedelta(days = 1)  
            start_str = start_new_date.strftime("%Y-%m-%d")  
            return start_str + ":" + start_str  
        else:  
            return '-' 
    def main(self):
        self.prelogin()
        self.get_sp()
        self.login() 
        while True:  
            ## 接受键盘输入  
            ##实例化收集类，收集指定关键字和起始时间的微博   
            while self.flag:  
                url = self.getURL()  
                self.download(url)   
            else:  
                cd = None  
                print ('-----------------------------------------------------'  )
                print ('-----------------------------------------------------'  )

if __name__ == '__main__':
    username = '594323227@qq.com' # 微博账号
    password = '0512weiboWYJ' # 微博密码
    keyword = input('Enter the keyword(type \'quit\' to exit ):')  
    if keyword == 'quit':  
        sys.exit()  
    startTime = input('Enter the start time(Format:YYYY-mm-dd):')  
    #region = input('Enter the region([BJ]11:1000,[SH]31:1000,[GZ]44:1,[CD]51:1):')  
    interval = input('Enter the time interval( >30 and deafult:50):') 
    weibo = WeiBo(username,password,keyword,startTime, interval)
    weibo.main()
