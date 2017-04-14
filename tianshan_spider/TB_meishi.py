# -*-coding:UTF-8-*-
import re
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException   # 引入超时异常
from selenium.webdriver.common.by import By  # 支持定位策略集
from selenium.webdriver.support.ui import WebDriverWait  # 等待功能
from selenium.webdriver.support import expected_conditions as EC  # 预期条件判断
from pyquery import PyQuery as pq
import pymysql

# 若直接写上路径(executable_path = 'C:\Python27\phantomjs\bin\phantomjs.exe')
browser = webdriver.PhantomJS(service_args=["--load-images=false"])   # 启动浏览器,设置不加载图片  #Chrome()
wait = WebDriverWait(browser, 10)  # 超时10秒时间，直到......
lst = []
browser.set_window_size(1366, 768)  # 设置浏览器大小，phantomJS需要设置浏览器大小，方便操作


def search():
	print("正在搜索...")
	try:
		browser.get("https://www.taobao.com/")  # 进入淘宝网页
		input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))   # 等到输入框出现以后
		submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button")))
		# 搜索按钮
		input.send_keys('四川美食')   # 键入关键字"美食"
		submit.click()		# 开始搜索
		total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.total")))
		# 直到出现总页数
		get_products()
		return total.text  # 返回总页数100
	except TimeoutException:
		return search()


def next_page(page_number):
	print("正在翻页...", page_number)
	try:   		# 直到出现页码的搜索框
		input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
		# 出现"确定"按钮
		submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
		input.clear()  # 清空页码数字
		input.send_keys(page_number)  # 输入需要的页码
		submit.click()  # 点击确定
		wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span")
		, str(page_number)))  # 确认是否出现所需的页码
		get_products()
	except TimeoutException:
		return next_page(page_number)


def get_products():
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item")))  # 直到出现所需商品信息
	html = browser.page_source  # 获得网页源代码
	doc = pq(html)	 # 解析网页
	items = doc("#mainsrp-itemlist .items .item").items()

	for item in items:
		product = {
			'image': item.find('.pic .img').attr('src'),
			'price': item.find('.price').text(),
			'deal': item.find('.deal-cnt').text()[:-3],  # 与例子不一样   1714人付款-》1714
			'title': item.find('.title').text(),
			'shop': item.find('.shop').text(),  # 与例子不一样
			'location': item.find('.location').text()
		}
		print(product)
		lst.append(product)


def save_to_mysql(lst):
	db = pymysql.connect(host="localhost", user="root", password="*******", db="taobaoshop", charset="utf8")
	start_time2 = time.time()
	cursor = db.cursor()
	cursor.execute("DROP TABLE IF EXISTS shops20170328_2")
	createTab = '''CREATE TABLE shops20170328_2(
	shops_id INT NOT NULL AUTO_INCREMENT,
	title VARCHAR(200) NOT NULL,
	price VARCHAR(10) NOT NULL,
	image_url VARCHAR(150) NOT NULL,   # 部分url位置修改,改用data-src属性,因此可以把image_url不设置为非NULL
	deal VARCHAR(10) NOT NULL,
	shop VARCHAR(100) NOT NULL,
	location VARCHAR(20) NOT NULL,
	PRIMARY KEY(shops_id))'''
	cursor.execute(createTab)
	for product in lst:
		sql = "INSERT INTO shops20170328_2(title, price, image_url, deal, shop, location) VALUES (%s,%s,%s,%s,%s,%s)"
		try:
			cursor.execute(sql, (product['title'], product['price'], product['image'], product['deal'], product['shop'],product['location']))
			db.commit()
			print("shop", product['title'], " insert success!")
		except Exception as e:
			print("shop", product['title'], " error,rollback!", e)
			db.rollback()
	end_time2 = time.time()
	print("存到mysql数据库一共花费了 %s S" % (end_time2 - start_time2))
	cursor.close()
	db.close()


def main():
	start_time = time.time()
	try:
		total = search()
		total = int(re.compile('(\d+)').search(total).group(0))  # 提取出数字
		print(total)
		for i in range(2, total + 1):  # 循环获取网页内容 total + 1
			print("正在分析第%s 页..." % i)
			next_page(i)
	except Exception:
		print(Exception)
	finally:
		browser.close()
	print("开始存入mysql数据库......")
	save_to_mysql(lst)
	print("存入数据库完毕")
	end_time = time.time()
	print("此次爬取一共花费 %s S" % (end_time - start_time))


if __name__ == "__main__":
	main()
