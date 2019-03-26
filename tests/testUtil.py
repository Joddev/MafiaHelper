from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
import time

driver_path = '/Util/pyUtil/chromedriver'
url = 'localhost:8000'

class GameUser:
	def __init__(self, driver):
		self.name = driver.find_element_by_xpath('//span[@class="tag name"]').text.strip()
		self.driver = driver

def create_connect():
	driver = webdriver.Chrome(driver_path)
	try:
		driver.get(url)
		name_div = driver.find_element_by_xpath('//span[@class="tag name"]')
		while name_div.text.strip() == 'NAME':
			pass
	except UnexpectedAlertPresentException:
		driver.close()
		raise Exception('websocket lost connection!')
	return GameUser(driver)

def adjust_jobs(driver, jobs):
	more_job = driver.find_element_by_xpath('//i[@class="fas fa-plus-circle"]')
	for job in jobs:
		more_job.click()
		driver.find_element_by_xpath(f'//span[contains(text(),"{job}")]').click()
	for job_div in driver.find_elements_by_xpath('//span[@class="tag job"]'):
		job_text = job_div.text.strip()
		job_name = job_text[:job_text.find(':')]
		cur_cnt = int(job_text[job_text.find(':'):].strip())
		try:
			target_cnt = jobs[job_name]
		except KeyError:
			target_cnt = 0
		if cur_cnt > target_cnt:
			fas = job_div.find_element_by_xpath('//i[@class="fas fa-caret-down"]')
		elif cur_cnt < target_cnt:
			fas = job_div.find_element_by_xpath('//i[@class="fas fa-caret-down"]')
		for _ in range(abs(cur_cnt - target_cnt)):
			fas.click()		

def start_game(users, jobs):
	pass
