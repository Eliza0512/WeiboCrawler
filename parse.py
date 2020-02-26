## reference
## https://blog.csdn.net/weixin_39777626/article/details/80212216


import csv
import requests
import json
import urllib 
import re
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud,ImageColorGenerator
import PIL.Image as Image

search=input('请输入关键词:')
begin=input('请输入初始检索时间：')

# url='https://m.weibo.cn/api/container/getIndex?type=all&queryVal={}&featurecode=20000320&luicode=10000011&lfid=106003type%3D1&title={}&containerid=100103type%3D1%26q%3D{}'.format(search,search,search)

def setKeyWord(keyword):   
    return keyword.encode("utf-8")

def getKeyWord(keyword):  
    once = urllib.parse.urlencode({"kw":keyword})[3:]  
    return urllib.parse.urlencode({"kw":once})[3:]

url= 'https://s.weibo.com/weibo/'+getKeyWord(setKeyWord(search))+'&xsort=hot&suball=1&timescope=custom:'+begin+':&page='

def cookie():
    with open('cookie.txt','r') as f:
        cookies={}
        for line in f.read().split(';'):
            name,value=line.strip().split('=',1)
            cookies[name]=value 
        return cookies

headers = {'Host': 's.weibo.com',
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
    'Cookie': 'SINAGLOBAL=4443763326027.806.1581661223803; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhqyEu9GzNL.PD7Zbu5EgOT5JpX5K2hUgL.Fo2c1hMXSo2Xe0z2dJLoI7D8K2LIBHY7SK2E; UOR=,,cn.bing.com; login_sid_t=2b0c7355967b6829b3dea0066200b46c; cross_origin_proto=SSL; YF-V5-G0=9717632f62066ddd544bf04f733ad50a; _s_tentry=cn.bing.com; Apache=2757133860939.471.1582635983569; ULV=1582635983583:2:2:1:2757133860939.471.1582635983569:1581661223852; SCF=As4LpJgWoYzSOeNnlZi7BAi-vFrVTRYJ4cE9d7iUS_4UhDHyKoPYsTatH1YuwWNP3Anf2USEWvrfcU0CYzkH0R8.; SUB=_2A25zUWuFDeRhGedI41UV9i_IyD6IHXVQJ9pNrDV8PUNbmtAfLU_lkW9NVonb2Q9AqcVWo6y8dKF3xNFCO7gbUive; SUHB=05iLLyZ_s-H3vt; wvr=6; webim_unReadCount=%7B%22time%22%3A1582637493647%2C%22dm_pub_total%22%3A55%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A55%2C%22msgbox%22%3A0%7D'}

results=[]

links=[]
i=1
b=[1]
weibo=0
while True:
    if len(b)==0:
        break
    else:
        url_1=url+'&page='+str(i)
        print(url_1)
        r =requests.get(url_1,headers=headers).text
        print(r)
        a=json.loads(r)
        b=a['data']['cards']
        i+=1
        for j in range(len(b)):
            bb=b[j]
            try:
                for c in bb['card_group']:
                    try:
                        d=c['mblog']
                        link='https://m.weibo.cn/api/comments/show?id={}'.format(d['mid'])
                        links.append(link)
                        if d['isLongText']==False:
                            text=d['text']
                            pattern =re.compile(u"[\u4e00-\u9fa5]+")
                            text=re.findall(pattern,text)
                        else:
                            text=d['longText']['longTextContent']
                        results.append(text)
                        weibo+=1
                    except:
                        continue
            except:
                continue

print('共抓取{}条记录'.format(weibo))

pl=[]
for url_2 in links:
    r =requests.get(url_2,headers=headers,cookies=cookie()).text
    a=json.loads(r)
    try:
        num=a['data']['total_number']
        j=0
        for i in range(num//10+1):
            url_3=url_2+'&page='+str(i+1)
            r =requests.get(url_3,headers=headers,cookies=cookie()).text
            a=json.loads(r)
            b=a['data']
            try:
                c=b['hot_data']
                for i in range(len(c)):
                    d=c[i]['text']
                    pattern =re.compile(u"[\u4e00-\u9fa5]+")
                    d=re.findall(pattern,d)
                    j+=1
                    pl.append(d)
                    print(d)
            except:
                c=b['data']
                for i in range(len(c)):
                    d=c[i]['text']
                    pattern =re.compile(u"[\u4e00-\u9fa5]+")
                    d=re.findall(pattern,d)
                    j+=1
                    pl.append(d)
                    print(d)
        print('%s条评论'%j)
    except:
        print('无评论')

def word_cloud(results,search):
    siglist=[]
    for ii in results:
        try:
            signature=ii.strip().replace('http:t.cn','').replace('的','').replace('地','').replace('了','').replace('是','').replace('在','').replace('/','').replace('emoji','')
            rep=re.compile('1f\d+\w*|[<>/=]')
            signature=rep.sub('',signature)
            siglist.append(signature)
        except:
            for jj in ii:
                signature=jj.strip().replace('http:t.cn','').replace('的','').replace('地','').replace('了','').replace('是','').replace('在','').replace('/','').replace('emoji','')
                rep=re.compile('1f\d+\w*|[<>/=]')
                signature=rep.sub('',signature)
                siglist.append(signature)
    text=''.join(siglist)

    wordlist=jieba.cut(text,cut_all=True)
    word_space_split=" ".join(wordlist)

    coloring=np.array(Image.open("1.jpg"))
    my_wordcloud=WordCloud(background_color='white',width=2400,height=2400,max_words=2000,
                           mask=coloring,max_font_size=60,
                           random_state=42,scale=2,
                           font_path="simfang.ttf").generate(
                               word_space_split)
    image_colors=ImageColorGenerator(coloring)
    plt.imshow(my_wordcloud.recolor(color_func=image_colors))
    plt.imshow(my_wordcloud)
    plt.axis('off')
    plt.show
    my_wordcloud.to_file('{}.png'.format(search))

word_cloud(pl,results)
word_cloud(pl,search)