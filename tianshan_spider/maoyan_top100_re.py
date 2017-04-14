# -*-coding:UTF-8-*-
# -*-coding:UTF-8-*-
import json
import requests
import re
from bs4 import BeautifulSoup
import random
import csv
from multiprocessing.dummy import Pool   # 多线程
from multiprocessing import Pool
import time


def get_response(url):
	try:
		r = requests.get(url)
		r.raise_for_status()
		r.encoding = 'utf-8'
		return r.text
	except Exception as e:
		print(e)


def parse(html):
	pattern = re.compile(r'<dd>.*?board-index.*?">(\d+)</i>.*?<img data-src="(.*?)".*?name"><a'
	+ r'.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>'
	+ r'.*?fraction">(\d+)</i></p>.*?</dd>', re.S)
	items = re.findall(pattern, html)
	# print(items)
	for item in items:
		yield{
			'index': item[0],
			'image': item[1],
			'title': item[2],
			'actor': item[3].strip()[3:],
			'time': item[4][5:],
			'score': item[5] + item[6]
		}


def write_to_file(content):
	with open(r"H:/image/result.txt", 'a', encoding='utf-8') as f:
		f.write(json.dumps(content, ensure_ascii=False) + '\n')
		f.close()


def main(offset):
	url = "http://maoyan.com/board/4?offset=" + str(offset)
	html = get_response(url)
	for item in parse(html):
		print(item)
		write_to_file(item)


if __name__ == "__main__":
	start_time = time.time()
	for i in range(0, 100, 10):
		main(i)
	end_time = time.time()
	print(" 此次总共花费了%s S" % (end_time - start_time))
	# groups = [i for i in range(0, 100, 10)]
	# start_time = time.time()
	# pool = Pool(processes=3)
	# pool.map(main, groups)
	# pool.close()
	# pool.join()
	# end_time = time.time()
	# print(" 此次总共花费了%s S" % (end_time - start_time))

	#  3进程花费1.5s，6线程花费0.5s，单进程花费1.5s
