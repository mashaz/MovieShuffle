# -*- coding:utf-8 -*-
#!/usr/bin/env python

__auther__ = 'xiaohuahu94@gmail.com'

'''
todos:
自己想看的电影 和 关注的人看过的电影
自动下载 aria2
自动标记
'''

import requests
from bs4 import BeautifulSoup
import urllib,urllib2
import re
import os
import sys
import time
import random
import sqlite3

reload(sys)
sys.setdefaultencoding('utf-8')   # note
requests.adapters.DEFAULT_RETRIES = 5 

STYLE = {
        'fore':
        {   # 前景色
            'black'    : 30,   #  黑色
            'red'      : 31,   #  红色
            'green'    : 32,   #  绿色
            'yellow'   : 33,   #  黄色
            'blue'     : 34,   #  蓝色
            'purple'   : 35,   #  紫红色
            'cyan'     : 36,   #  青蓝色
            'white'    : 37,   #  白色
        },

        'back' :
        {   # 背景
            'black'     : 40,  #  黑色
            'red'       : 41,  #  红色
            'green'     : 42,  #  绿色
            'yellow'    : 43,  #  黄色
            'blue'      : 44,  #  蓝色
            'purple'    : 45,  #  紫红色
            'cyan'      : 46,  #  青蓝色
            'white'     : 47,  #  白色
        },

        'mode' :
        {   # 显示模式
            'mormal'    : 0,   #  终端默认设置
            'bold'      : 1,   #  高亮显示
            'underline' : 4,   #  使用下划线
            'blink'     : 5,   #  闪烁
            'invert'    : 7,   #  反白显示
            'hide'      : 8,   #  不可见
        },

        'default' :
        {
            'end' : 0,
        },
}


def UseStyle(string, mode = '', fore = '', back = ''):

    mode  = '%s' % STYLE['mode'][mode] if STYLE['mode'].has_key(mode) else ''

    fore  = '%s' % STYLE['fore'][fore] if STYLE['fore'].has_key(fore) else ''

    back  = '%s' % STYLE['back'][back] if STYLE['back'].has_key(back) else ''

    style = ';'.join([s for s in [mode, fore, back] if s])

    style = '\033[%sm' % style if style else ''

    end   = '\033[%sm' % STYLE['default']['end'] if style else ''

    return '%s%s%s' % (style, string, end)



def Login():  
	f = open('cookies.txt','r')
	cookies = {}
	for line in f.read().split(','):
		name,value = line.strip().split('=',1)
		cookies[name] = value
	return cookies

def GetWishList(uid):
	start_item = 0
	wish_url = 'https://movie.douban.com/people/'+str(uid)+'/wish?sort=rating&start='+str(start_item)+'&mode=list&tags_sort=count'
	#按评分排序 30条 start=?
	respo = requests.get(wish_url)
	soup = BeautifulSoup(respo.content)

	summary = soup.findAll('span',attrs={'class','subject-num'})[0].contents[0].strip()
	re_summary = re.compile(r'[0-9]{1,4}')
	summary = re_summary.findall(summary).pop()

	page_max_list = soup.findAll('span',attrs={'class','thispage'})
	page_max = page_max_list.pop()
	page_soup = BeautifulSoup(str(page_max))
	pages = page_soup.span['data-total-page']              #共pages页
	print '想看的电影列表共%s条记录'%(summary)
	wish_list_all = []
	star_list_all = []
	for i in range(0,int(pages)):
		wish_url = 'https://movie.douban.com/people/' + str(uid) + '/wish?sort=rating&start='+str(start_item)+'&mode=list&tags_sort=count'
		start_item += 30
		respo = requests.get(wish_url)
		soup = BeautifulSoup(respo.content)

		re_star = re.compile(r'rating[0-6]{1,2}')
		star_list = re_star.findall(respo.content)
		star_list_all.extend(star_list)

		wish_list = soup.findAll('div',attrs={'class','title'})
		for title in wish_list:
			title = title.contents[1].contents[0].strip().lstrip().rstrip()
			wish_list_all.append(title) #电影列表
	return wish_list_all,star_list_all

def GetWatchedList(uid):
	start_item = 0
	#https://movie.douban.com/people/54005301/collect?sort=rating&start=30&mode=list&tags_sort=count
	watched_url = 'https://movie.douban.com/people/'+str(uid)+'/collect?sort=rating&start='+str(start_item)+'&mode=list&tags_sort=count'
	#按评分排序 30条 start=?
	respo = requests.get(watched_url)
	soup = BeautifulSoup(respo.content)
	summary = soup.findAll('span',attrs={'class','subject-num'})[0].contents[0].strip()
	re_summary = re.compile(r'[0-9]{1,4}')
	summary = re_summary.findall(summary).pop()
	page_max_list = soup.findAll('span',attrs={'class','thispage'})
	page_max = page_max_list.pop()
	page_soup = BeautifulSoup(str(page_max))
	pages = page_soup.span['data-total-page']              #共pages页
	print '已看的电影列表共%s条记录'%(summary)
	watched_list_all = []
	for i in range(0,int(pages)):
		watched_url = 'https://movie.douban.com/people/'+str(uid)+'/collect?sort=rating&start='+str(start_item)+'&mode=list&tags_sort=count'
		start_item += 30
		respo = requests.get(watched_url)
		soup = BeautifulSoup(respo.content)
		watched_list = soup.findAll('div',attrs={'class','title'})
		for title in watched_list:
			title = title.contents[1].contents[0].strip().lstrip().rstrip()
			watched_list_all.append(title) #电影列表
	return watched_list_all

def Shuffle(uid):
	wish_list , star_list = GetWishList(uid)
	index = random.randint(0,len(wish_list))
	star = int(star_list[index].lstrip('rating'))
	print wish_list[index],
	print '/ 评分:',  #todo 通过api获取精确评分
	if star<10:
		star *= 10
	a = star/10
	b = star%10

	for i in range(0,a):
		print '★' ,

	if b!=0:
		print '☆'
	else :
		print
	return wish_list[index]
def GetAverageScore(mid):
	url = 'https://api.douban.com/v2/movie/subject/'+str(mid)
	res = requests.get(url)
	re_s = re.compile(r'average": [0-9]{1}\.[0-9]{1}')
	score = re_s.findall(res.content)[0].lstrip('average": ')
	return score 

def Compare():
	pass

def GetMagnet(mname):
	url = 'https://www.nimasou.info/l/'+str(mname)+'-hot-desc-1'
	headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
	response = requests.get(url,headers=headers)
	soup = BeautifulSoup(response.content)
	item_list = soup.findAll('td',attrs={'class','x-item'})
	title_list = []
	mag_list = []
	detail_list = []
	for item in item_list:
		str_title = ''
		title = item.contents[1].contents[1].contents
		for i in title:
			i = str(i).lstrip('<span class="highlight">').rstrip('</span>')
			str_title += i
		
		detail = item.contents[5].contents[0].strip()
		
		magnet = item.contents[5].contents[1]
		soup = BeautifulSoup(str(magnet))
		magnet = soup.a['href']

		title_list.append(str_title)
		mag_list.append(magnet)
		detail_list.append(detail)
	if len(mag_list) == 0:
		print 'Ooops,No Record...'
	for i in range(0,len(mag_list)):
		print UseStyle('---------------------------------------------------------------------------------',fore='black')
		print 'Title:' + title_list[i]
		print 'Detail:' + detail_list[i]
		print 'Magnet:',
		print UseStyle(mag_list[i],fore='cyan')
		print 

def Download(magnet):
	pass
def main():
	if len(sys.argv) == 1:          
 		m_name = Shuffle('54005301')
 		names = m_name.split('/')
 		m_name = names[0]
 		print m_name
		print UseStyle('输入y查询magnet,任意按键退出',fore='cyan')
		x = raw_input()
		if x == 'y' or x == 'Y' :
			GetMagnet(m_name)

		#GetMagnet('让子弹飞')
	else:  
	#长度不为1
		if sys.argv[1].startswith('--'):     
			option = sys.argv[1][2:]     
			if (option == 'help'):
				print '*******************操作指南*********************'
				print 
				print UseStyle('1. python shuffle.py',fore='cyan')
				print 
				print UseStyle('1. python shuffle.py UID',fore='cyan')
				print
			    
		else:
			m_name = Shuffle('54005301')
			print UseStyle('输入y查询magnet,任意按键退出',fore='cyan')
			x = raw_input()
			if x == 'y':
				GetMagnet(m_name)
			#GetMagnet('让子弹飞')
if __name__ == '__main__':
	main()
	