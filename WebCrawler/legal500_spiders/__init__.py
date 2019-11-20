# encoding:utf-8
import os 
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
import string
import scrapy
import json
from scrapy import Request
from .utils import  parse_departments, parse_lawyers


class LawyerScraper(scrapy.Spider):
	name = "legal500_lawyer_scraper"

	def start_requests(self):
		" PICK all firm links"
		with open(os.path.join(ROOT_DIR,"start_urls_departments.txt"), "rt") as f:
			for url in f.readlines():
				yield scrapy.Request(url=url, callback=self.parse_lawyers_section
							# dont_filter = True
					)

	def parse_lawyers_section(self, response):
		return parse_lawyers(response)



class FirmsSpider(scrapy.Spider):
	name = 'legal500_firms_scraper'
	allowed_domains = ['legal500.com']

	def start_requests(self):
		with open(os.path.join(ROOT_DIR,"start_urls_apac_list.txt"), "rt") as f:
			start_urls = [url.strip() for url in f.readlines()]
		for url in start_urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		return parse_departments(response)