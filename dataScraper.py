"""A script used to download all of Donald Trump's public tweets.
"""

#libraries
import csv
import json
from bs4 import BeautifulSoup
from time import sleep
import sys
import requests
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pandas
import sys
import inspect





def scrape():
	header = []
	#sets up Driver

	options = webdriver.ChromeOptions()
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--incognito')
	options.add_argument('--headless')
	options.add_argument('--no-sandbox') 


	#goes to webpage and collects data

	driver = webdriver.Chrome('/Users/Aditya/Desktop/chromedriver', options=options)
	driver.get("https://www.realclearpolitics.com/coronavirus/")
	element = driver.find_element_by_xpath('//*[@id="covid_totals_table"]/div/div/table/tfoot/tr/td/button')
	actions = ActionChains(driver)
	actions.move_to_element(element).click().perform()
	html = driver.page_source
	soup = BeautifulSoup(html, "lxml")

	#print(soup)

	#finds table and extracts data

	table = soup.find('table')
	tableHeader = table.find_all('th')
	information = table.find_all('td')

	#gets header info
	for head in tableHeader:
		header.append(head.text)

	#gets global info

	globalTable = information[:10]
	globalinfo = []
	temp = []
	for gInfo in globalTable:
		if gInfo.text != 'Deaths':
			temp.append(gInfo.text)
	globalinfo.append(temp)

	#gets country info

	local = []
	countryInfo = []
	countryTable = information[11:]
	count = 0


	for x in countryTable:
		if (count < 10):
			local.append(x.text)
			count +=1

		if (count == 10):
			count = 0 
			countryInfo.append(local)
			local = []
	driver.quit()
	return countryInfo,globalinfo,header


def dataParser(data):
	count = 0
	final = []
	for x in data:
		if count == 0:
			count += 1
			if 'China*' in x:
				final.append("China")
			elif "United States" in x:
				final.append("United States of America")
			elif "Iran**" in x:
				final.append("Iran")
			elif "United Kingdom" in x:
				final.append("United Kingdom")
			else:
				final.append(x)
		elif "%" in x:
			final.append(float(x.replace('%',""))/100.0)
		elif "," in x:
			final.append(float(x.replace(',',"")))
		elif "+" in x:
			final.append(float(x.replace('+',"")))
		elif x == '-':
			final.append(None)
		elif '.' in x:
			final.append(float(x))
		elif x.replace(" ", "").isalpha() == False:
			final.append(int(x))
		else:
			final.append(x)
	return final
		

def writeToDest(dest,arr):
	for x in arr:
		dest.append(x)
	return dest



if __name__== "__main__":

	countryInfo,globalinfo,header = scrape()

	parsedGlobalinfo = []	
	parsedCountryinfo = []
	final = []

	for gInfo in globalinfo:
		parsedGlobalinfo.append(dataParser(gInfo))

	for cInfo in countryInfo:
		parsedCountryinfo.append(dataParser(cInfo))

	final.append(header)
	final  = writeToDest(final,parsedGlobalinfo)
	final  = writeToDest(final,parsedCountryinfo)

	write_file = "output.csv"
	with open(write_file, "w") as output:
		writer = csv.writer(output)
		writer.writerows(final)
	output.close()












	