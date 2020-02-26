from bs4 import BeautifulSoup
import re
import sys
import os

def rewrite(file_path,contents):
    f = open(file_path,'a')
    for c in contents:
        f.write(c.text.strip())
        f.write('\n')
    f.close()
        

def getTargetDiv(f,myAttrs):
    htmlfile = open(f, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(htmlhandle, 'lxml')
    cards = soup.find_all(name='div',attrs=myAttrs)
    results=[]
    for c in cards:
        text = c.find_all(name='div',attrs={"class":"content", "node-type":"like"})[0].find_all(name='p',attrs={"class":"txt", "node-type":"feed_list_content"})
        results.append(text[0])
    return results

def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False
 
def is_number(uchar):
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False
 
def is_alphabet(uchar):
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

def format_str(content):
    content_str = ''
    for i in content:
        if (is_chinese(i) or is_number(i)):
            content_str = content_str+i
    return content_str

if __name__=="__main__":
    myAttrs={"class":"card-wrap","action-type":"feed_list_item"}
    root_path = 'wuhan'
    file_path='result.txt'
    for i in os.walk(root_path):
        for j in i[2]:
            #i[0]是当前文件夹的绝对路径，j是文件名
            path = os.path.join(i[0],j)
            rewrite(file_path,getTargetDiv(path,myAttrs))