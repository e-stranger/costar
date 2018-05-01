from selenium import webdriver
from bs4 import BeautifulSoup
from numpy.random import normal
import pandas, time, sys, subprocess, format

# tries to take control of existing webdriver. If details don't exist, 
# new webdriver is created and returned.

def get_existing_session(filename):
	try:
		info = pandas.read_csv(filename)
	except FileNotFoundError:
		print("file not found! creating new session...")
		subprocess.call(['python3', 'persist_webdriver.py'])
		info = pandas.read_csv(filename)
	try:
		return create_driver_session(info['session_id'][0], info['executor_url'][0])
	except Exception as e:
		print('Unknown exception ({}) occurred. Exiting...'.format(str(e)))
		exit(1)

def create_driver_session(session_id, executor_url):
	from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
	
	# Save existing RemoteWebDriver.execute method

	org_command_execute = RemoteWebDriver.execute
	def new_command_execute(self, command, params=None):

		# if we're creating a new session, mock success and return with existing session details
		if command == "newSession":
			return {'success': 0, 'value': None, 
'sessionId': session_id}
		# else return results of existing RemoteWebDriver method
		else:
			return org_command_execute(self, command, params)

	# override execute method with our new function, and return existing session

	RemoteWebDriver.execute = new_command_execute
	new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
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
			# Don't get banned! Sleep for a random amount of time...			
			sleeptime = 3 + normal(5, 3)
			print('sleeping {} seconds...'.format(sleeptime))
			time.sleep(sleeptime)

			# Make sure we're not in an embedded iframe
			self.driver.switch_to.default_content()
	
			# Switch to iframe with HTML table
			self.driver.switch_to.frame(self.driver.find_element_by_id('oGridFrame'))
	
			# Select rows by id of form `row[0-9]{1,2}`, where X is a number between 1 and 49
			items = self.driver.find_elements_by_css_selector('tr[id*="row"]')
			for item in items:
				try:
					subitems = [subitem.text for subitem in item.find_elements_by_css_selector('td')]

				# a bit hacky, but we're not interested in anything that throws an exception.
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
				# We've run out of pages. Now, to process the data
				print('No more pages. Processing data...') 
				break

		# Save listings data, call format's main method with filename 
		# Ensures file actually exists

		filename = "{}.csv".format(self.state.lower())
		print("Saved data frame. Calling format.main({})".format(filename))
		pandas.DataFrame(listings).to_csv(filename)

		format.main(filename)

if __name__ == "__main__":
	state = sys.argv[1]
	driver2 = get_existing_session('selenium_details.csv')
	costar = CostarProcessor(driver=driver2, state=state)
	costar.process_pages()
	subse
	
