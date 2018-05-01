from selenium import webdriver
from bs4 import BeautifulSoup
from numpy.random import normal
import pandas, time, sys


def get_existing_session(filename):
	try:
		info = pandas.read_csv(filename)
	except FileNotFoundError:
		print("file not found!")
		exit(1)
	return create_driver_session(info['session_id'][0], 
info['executor_url'][0])
	
def create_driver_session(session_id, executor_url):
	from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
	org_command_execute = RemoteWebDriver.execute
	def new_command_execute(self, command, params=None):
		if command == "newSession":
			return {'success': 0, 'value': None, 
'sessionId': session_id}
		else:
			return org_command_execute(self, command, 
params)

	RemoteWebDriver.execute = new_command_execute
	new_driver = webdriver.Remote(command_executor=executor_url, 
desired_capabilities={})
	new_driver.session_id = session_id
	RemoteWebDriver.execute = org_command_execute

	return new_driver

class CostarProcessor:
	def __init__(self, state, driver):
		self.state = state	
		self.driver = driver

	def process_pages(self):
		listings = []
		while True:
			
			sleeptime = 3 + normal(5, 3)
			print('sleeping {} seconds...'.format(sleeptime))
			time.sleep(sleeptime)
			self.driver.switch_to.default_content()
			self.driver.switch_to.frame(self.driver.find_element_by_id('oGridFrame'))
			items = self.driver.find_elements_by_css_selector('tr[id*="row"]')
			for item in items:
				try:
					subitems = [subitem.text for subitem in item.find_elements_by_css_selector('td')]
				except Exception as e:
					print(str(e))
					print(len(listings))
					time.sleep(5)
					break
				try:
					listing = {'company': subitems[1], 'listing_agent': subitems[2], 'ou_or_inv': subitems[3], 
'property_type': subitems[4], 'state': self.state}	
				except Exception as e:
					print(str(e))
					continue
				print(listing)
				listings.append(listing)
			
			self.driver.switch_to.default_content()
			try:
				self.driver.find_element_by_css_selector('div.nextGridControlButton').click()		
			except:
				print('how dis happen') 
				break
		print("saved")
		pandas.DataFrame(listings).to_csv("{}.csv".format(self.state.lower()))

if __name__ == "__main__":
	state = sys.argv[1]
	driver2 = get_existing_session('selenium_details.csv')
	costar = CostarProcessor(driver=driver2, state=state)
	costar.process_pages()
	
