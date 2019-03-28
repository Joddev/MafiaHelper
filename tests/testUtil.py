from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
import asyncio
import time

driver_path = '/Util/pyUtil/chromedriver'
url = 'localhost:8000'


class GameUser:
	def __init__(self, driver):
		self.name = driver.find_element_by_xpath('//span[@class="tag name"]').text.strip()
		self.driver = driver


class GameRoom:
	def __init__(self, users, status='wait'):
		'''
		Arguments:
			status {str} -- one of ['wait', 'day', 'elect', 'night'] (default: {'wait'})
		'''
		self.users = users
		self.status = status	
	
	def start(self):
		if self.status != 'wait':
			raise MafiaTestFailException(f'Cannot start room with status {self.status}')
		for user in self.users:
			user.driver.find_element_by_xpath('//div[@class="login100-form-btn" and contains(text(),"ready")]').click()
		self.status = 'day'

	def elect(self):
		if self.status != 'day':
			raise MafiaTestFailException(f'Cannot start room with status {self.status}')
		for user in self.users:
			user.driver.find_element_by_xpath('//div[@class="login100-form-btn" and contains(text(),"ELECTION")]').click()
		self.status = 'elect'

	def night(self):
		if self.status != 'day':
			raise MafiaTestFailException(f'Cannot start room with status {self.status}')
		for user in self.users:
			user.driver.find_element_by_xpath('//div[@class="login100-form-btn" and contains(text(),"NIGHT")]').click()
		self.status = 'night'
		
	def exit(self):
		for user in self.users:
			user.driver.close()


class MafiaTestFailException(Exception):
	pass

def create_connection():
	driver = webdriver.Chrome(driver_path)
	try:
		driver.get(url)
		name_div = driver.find_element_by_xpath('//span[@class="tag name"]')
		while name_div.text.strip() == 'NAME':
			pass
	except UnexpectedAlertPresentException:
		driver.close()
		raise MafiaTestFailException('Websocket lost connection!')
	return GameUser(driver)

def adjust_jobs(driver, jobs):
	more_job = driver.find_element_by_xpath('//i[@class="fas fa-plus-circle"]')
	for job in jobs:
		more_job.click()
		time.sleep(0.5)
		path = f'//div[@class="modal-job"]//span[contains(text(),"{job}")]'
		driver.execute_script(f'document.evaluate(\'{path}\', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();')
		time.sleep(0.5)
	for job_div in driver.find_elements_by_xpath('//span[@class="tag job"]'):
		job_text = job_div.text.strip()
		job_name = job_text[:job_text.find(':')]
		cur_cnt = int(job_text[job_text.find(':')+1:].strip())
		try:
			target_cnt = jobs[job_name]
		except KeyError:
			target_cnt = 0
		if cur_cnt > target_cnt:
			fas = job_div.find_element_by_xpath('.//i[@class="fas fa-caret-down"]')
		elif cur_cnt < target_cnt:
			fas = job_div.find_element_by_xpath('.//i[@class="fas fa-caret-up"]')
		for _ in range(abs(cur_cnt - target_cnt)):
			fas.click()		

def create_room(count, jobs):
	if sum(jobs.values()) != count:
		raise MafiaTestFailException('the number of total members must be equal to the number of total jobs!')
	# loop = asyncio.get_event_loop()
	# group = asyncio.gather(*[create_connection() for _ in range(count)])
	# users = loop.run_until_complete(group)
	users = [create_connection() for _ in range(count)]
	print(users)
	# create and join room
	users[0].driver.find_element_by_xpath('//div[contains(text(), "create")]').click()
	time.sleep(0.5)
	for i in range(1, count):
		users[i].driver.find_element_by_class_name('login100-form-btn').click()
	# job setting
	adjust_jobs(users[0].driver, jobs)
	return GameRoom(users)

loop = asyncio.get_event_loop()

loop.run_until_complete(asyncio.gather())
room = create_room(4, {'police':2, 'doctor':1, 'mafia':1})
room.start()
room.elect()
room.exit()
