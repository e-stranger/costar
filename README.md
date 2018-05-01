# Real estate directory scraper

This script creates and maintains the same Selenium webdriver instance 
to scrape data, instead of constructing a new instance each time the 
program is run. This lets us login only once and evade scraping detection systems.
It detects whether there is an existing instance and takes control of it if it does.
