#!/bin/env python
# Jarvis structure cloned
# Davis - DArkweb Very Intelligent Scraper with a DB backend.
# Copyright (c) 2021 Afovos <afovos at afovos.com.au>

import os # Libraries needed
import csv
import sys
import time
import socks
import socket
import getopt
import sqlite3
import requests
import subprocess
import configparser
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
from datetime import datetime, date, timedelta
from selenium.webdriver.chrome.options import Options

config = configparser.ConfigParser() # Config settings
config.read('dark_web_sites.conf')
sections = config.sections()

tor_proxy = "127.0.0.1:9050" # Selenium settings
chrome_options = Options()
torexe = os.popen('/root/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US/Browser/TorBrowser/Tor/tor')
chrome_options.add_argument("--test-type")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")
chrome_options.add_argument('--proxy-server=socks5://%s' % tor_proxy)
try:
	driver = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)
except Exception as e:
	print(e)
	driver = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)
	pass

socks.set_default_proxy(socks.SOCKS5, "localhost", 9050) # Request settings
socket.socket = socks.socksocket
def getaddrinfo(*args):
	return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
socket.getaddrinfo = getaddrinfo

VERSION = "20210601" # Variables Needed
# DEFAULT_DATABASE = config['Ako']['db']
DEFAULT_DATABASE = "dark_web.db"
vflag = False
test_flag = False
db_file = DEFAULT_DATABASE
freq_flag = False
nodb_flag = False
cursor = None
scan_name = None
scan_result = None
scan_output = None
sql_script = ""

conn = sqlite3.connect(db_file) # Sql settings
conn.execute('''CREATE TABLE IF NOT EXISTS dark_web_monitoring2
			(id INT PRIMARY KEY,
			date_time TEXT,
			dark_web_name TEXT,
			dark_web_site TEXT,
			client_dark_web_site TEXT,
			client_name TEXT,
			client_site TEXT,
			client_address TEXT,
			client_entity TEXT,
			client_individuals_affected TEXT,
			client_breach_date TEXT,
			client_type_of_breach TEXT,
			client_location_of_breach TEXT,
			client_details TEXT,
			client_other_details TEXT);''')

def verbose(values): # Verbose
	global vflag
	if vflag:
		print(values)

def usage(name): # Usages
	print("usage: %s [options] <Davis - DArkweb Very Intelligent Scraper with a DB backend>" % name)
	print("options:")
	print("     (-?) --help\tthis message")	
	print("     (-S) --scrape\tscrape dark web sites")
	print("     (-a) --all\t\toutput all scrape")
	print("     (-v) --verbose\tverbose output")
	print("     (-c) --custom\tspecify custom SQL command")
	print("     (-d) --delete\tspecify scrape name to delete")
	print("     (-D) --delete_all\tdelete all scrape data on DB")
	print("     (-f) --frequency\tlist most frequent hit Client name")
	print("     (-l) --list\tlist scrape")
	print("     (-F) --first\toutput first scrape")
	print("     (-L) --last\toutput last scrape")
	print("     (-s) --search\tsearch for Client name")
	print("     (-V) --version\toutput version number and exit")

def output_all(rows): # Output all queries
	print("+------------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------+")
	print("| Dark Web         | Date/Time                  | Names                           | Urls                                                                                              |")
	print("+------------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------+")
	if rows:
		for row in rows:
			dark_web = row[2]
			time_stamp = row[1]
			client = row[5]
			url = row[8]
			print("| %-16s | %-19s | %-31s | %-97s |" % (dark_web, time_stamp, client, url))
	else:
		print("0 Results.")
	print("+------------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------+")

def output_one(rows): # Output only one queries
	print("+------------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------+")
	print("| Dark Web         | Date/Time                  | Names                           | Urls                                                                                              |")
	print("+------------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------+")
	if rows:
		dark_web = rows[0][2]
		time_stamp = rows[0][1]
		client = rows[0][5]
		url = rows[0][8]
		print("| %-16s | %-19s | %-31s | %-97s |" % (dark_web, time_stamp, client, url))
	else:
		print("0 Results.")
	print("+------------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------+")

def output_all_scans(db_file_): # Output all scraped
	conn = sqlite3.connect(db_file_)
	cursor = conn.cursor()
	print('Displaying all scrapes.')
	cursor.execute("SELECT * from dark_web_monitoring2 ORDER BY date_time DESC")
	rows = cursor.fetchall()
	output_all(rows)
	cursor.close()

def output_last_scan(db_file_): # Output last scraped
	conn = sqlite3.connect(db_file_)
	cursor = conn.cursor()
	print('Displaying last scan.')
	cursor.execute("SELECT * from dark_web_monitoring2 ORDER BY date_time DESC")
	rows = cursor.fetchall()
	output_one(rows)
	cursor.close()

def output_first_scan(db_file_): # Output first scraped
	conn = sqlite3.connect(db_file_)
	cursor = conn.cursor()
	print('Displaying last scan.')
	cursor.execute("SELECT * from dark_web_monitoring2 ORDER BY date_time")
	rows = cursor.fetchall()
	output_one(rows)
	cursor.close()

def query_db_service_scan(db_file_, search_param): # Output searched Client name
	conn = sqlite3.connect(db_file_)
	cursor = conn.cursor()
	cursor.execute("SELECT * from dark_web_monitoring2 WHERE client_name LIKE '%" + search_param + "%' OR dark_web_name LIKE '%" + search_param + "%' OR client_name LIKE '%" + search_param + "%' OR dark_web_site LIKE '%" + search_param + "%' OR client_link LIKE '%" + search_param + "%' ORDER BY date_time")
	rows = cursor.fetchall()
	output_all(rows)
	cursor.close()

def delete_scan_name(db_file_, scan_name): # Delete searched Client name
	conn = sqlite3.connect(db_file_)
	cursor = conn.cursor()

	if scan_name:
		cursor.execute("DELETE FROM dark_web_monitoring2 WHERE client_name LIKE '%s'" % scan_name)
		cursor.connection.commit()
		print('Deleting %s Client name.' % scan_name)
		output_all_scans(db_file_)

	cursor.close()

def delete_all_scan_name(db_file_): # Delete all data on table
	conn = sqlite3.connect(db_file_)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM dark_web_monitoring2")
	cursor.connection.commit()
	print('Deleted all scrape data on DB.')
	cursor.close()

def custom_sql(db_file_, sql): # Run custom sql queries
	conn = sqlite3.connect(db_file_)
	cursor = conn.cursor()
	try:
		cursor.execute(sql)
		cursor.connection.commit()
		rows = cursor.fetchall()
		output_all(rows)
	except sqlite3.ProgrammingError as msg:
		print("%s: error: %s\n" % (sys.argv[0], msg))
		exit(1)
	print('Connected to DB: %s and execute sql command.' % db_file_)
	cursor.close()

def scrape(db_file_): # Scrape Dark Web sites
	conn = sqlite3.connect(db_file_)
	cursor = conn.cursor()
	def scrape_data(links, url, dark_web): # Scrape Dark Web datas
		try:
			if no_link == "Yes":
				name = links.get_attribute("innerText")
				name = name.split("\t")
				names = name[1]
				address = name[2]
				entity = name[3]
				individuals_affected = name[4]
				breach_date = name[5]
				type_of_breach = name[6]
				location_of_breach = name[7]
			else:
				names = links.text
				address = entity = individuals_affected = breach_date = type_of_breach = location_of_breach = ""
		except:
			names = address = entity = individuals_affected = breach_date = type_of_breach = location_of_breach = ""
		try: # Get Client Dark Web site link
			if selenium == "Yes":
				if "http" not in links.get_attribute('href') or "www" not in links.get_attribute('href'):
					if "/" not in links.get_attribute('href'):
						name_links = url + "/" + links.get_attribute('href')
					else:
						name_links = url + links.get_attribute('href')
				else:
					name_links = links.get_attribute('href')
			else:
				if "http" not in links.get('href') or "www" not in links.get('href'):
					if "/" not in links.get('href'):
						name_links = url + "/" + links.get('href')
					else:
						name_links = url + links.get('href')
				else:
					name_links = links.get('href')
		except:
			name_links = ""
		if names == name_links or "read more" in names.lower() or "rss feed" in names.lower() or "home" in names.lower() or "about" in names.lower() or "download" in names.lower() or "continue reading" in names.lower() or "press release" in names.lower() or "rules" in names.lower() or "contact us" in names.lower():
			pass # Pass after filter unwated datas
		else:
			print(dark_web, names, address, entity, individuals_affected, breach_date, type_of_breach, location_of_breach, name_links) # Save scraped data on DB
			cursor.execute("INSERT INTO dark_web_monitoring2 (date_time, dark_web_site, dark_web_name, client_dark_web_site, client_name, client_address, client_entity, client_individuals_affected, client_breach_date, client_type_of_breach, client_location_of_breach) \
				VALUES (?,?,?,?,?,?,?,?,?,?,?)",(datetime.now(), url, dark_web, name_links, names, address, entity, individuals_affected, breach_date, type_of_breach, location_of_breach))
			cursor.connection.commit()

	for s in sections: # Iterate on all config settings
		url = config[s]['url']
		dark_web = config[s]['name']
		pagination = config[s]['pagination']
		global selenium
		selenium = config[s]['selenium']
		global no_link
		no_link = config[s]['no_link']
		try:
			if selenium == "Yes": # Scrape Dark Web site selenium needed
				time.sleep(3)
				driver.get(url)
				time.sleep(3)
				links = driver.execute_script("return document.getElementsByTagName('a');")
				links = list(set(filter(None, links)))
				for l in range(len(links)):
					scrape_data(links[l], url, dark_web)

			elif no_link == "Yes": # Scrape Clear Web site without link on data
				time.sleep(3)
				driver.get(url)
				time.sleep(3)
				pages = driver.execute_script("return document.getElementsByClassName('ui-paginator-page');")
				for p in range(1, len(pages)):
					driver.execute_script("document.getElementsByClassName('ui-paginator-page')[arguments[0]].click();", p)
					time.sleep(3)
					rows = driver.execute_script("return document.getElementsByTagName('tr');")
					for r in range(4, len(rows)):
						scrape_data(rows[r], url, dark_web)

			else: # Scrape Dark Web using request
				res = requests.get(url)
				time.sleep(3)
				soup = BeautifulSoup(res.content, 'lxml')
				if pagination == "Yes": # Get all pages link of site
					if soup.find_all("a", {"class": "page-link"}):
						links = [link for link in soup.find_all("a", {"class": "page-link"})]
					elif soup.find_all("a", {"class": "pagination-link"}):
						links = [link for link in soup.find_all("a", {"class": "pagination-link"})]
				else: # If no paginations get all links
					links = [link for link in soup.find_all("a")]
				links = list(set(filter(None, links)))

				for l in range(len(links)): # Iterate on all links
					if pagination == "Yes":
						sub_url = url + links[l].get('href')
						try:
							res = requests.get(sub_url)
							time.sleep(5)
							soup = BeautifulSoup(res.content, 'lxml')
							sub_links = [sub_link for sub_link in soup.find_all("a")]
							sub_links = list(set(filter(None, sub_links)))
							for sl in range(len(sub_links)):
								try:
									if "page-link" in sub_links[sl]['class'] or "pagination-link" in sub_links[sl]['class']:
										pass
								except:
									scrape_data(sub_links[sl], url, dark_web)
						except:
							pass
					else:
						scrape_data(links[l], url, dark_web)
		except Exception as e:
			print(e)
			pass
	cursor.close()

def options(): # Davis options
	global vflag, test_flag, db_path, cursor, freq_flag, nodb_flag, scan_name

	try:
		alist, args = getopt.getopt(sys.argv[1:], "?Savd:Ds:f:VlLFc:", ["help", "scrape", "all", "verbose", "delete=", "delete_all", "search=", "frequency=", "version", "list", "last", "first", "custom="])
	except getopt.GetoptError as msg:
		print("%s: %s\n" % (sys.argv[0], msg))
		usage(sys.argv[0])
		sys.exit(1)

	for (field, val) in alist:
		if field in ("-?", "--help"):
			usage(sys.argv[0])
			sys.exit(0)		
		if field in ("-S", "--scrape"):
			scrape(db_file)
			sys.exit(0)
		if field in ("-v", "--verbose"):
			vflag = True
		if field in ("-f", "--frequency"):
			freq_flag = True
			db_path = val
		if field in ("-a", "--all"):
			output_all_scans(db_file)
			sys.exit(0)
		if field in ("-L", "--last"):
			output_last_scan(db_file)
			sys.exit(0)
		if field in ("-F", "--first"):
			output_first_scan(db_file)
			sys.exit(0)
		if field in ("-V", "--version"):
			print("Davis v%s by Fovos <afovos at afovos.com.au>" % VERSION)
			print("Davis - DArkweb Very Intelligent Scraper with a DB backend.")
			sys.exit(0)
		if field in ("-l", "--list"):
			output_all_scans(db_file)
			sys.exit(0)
		if field in ("-s", "--search"):
			query_db_service_scan(db_file, val)
			sys.exit(0)
		if field in ("-d", "--delete"):
			delete_scan_name(db_file, scan_name=val)
			exit(0)
		if field in ("-D", "--delete_all"):
			delete_all_scan_name(db_file)
			exit(0)
		if field in ("-c", "--custom"):
			custom_sql(db_file, sql=val)
			exit(0)

if __name__ == "__main__": # Main
	vflag = True
	if len(sys.argv) < 2:
		try:
			with open("TEST.txt",'w',encoding = 'utf-8') as f:
				f.write("cron started\n")
			# scrape(db_file)
			# output_last_scan(db_file)
		except:
			usage(sys.argv[0])
		exit(0)
	else:
		options()
	try:
		driver.quit()
	except Exception as e:
		print(e)
		subprocess.run(["pkill", "chrome"])
		subprocess.run(["pkill", "firefox"])