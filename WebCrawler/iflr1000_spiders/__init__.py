# encoding:utf-8
import os, sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
import string
import scrapy
import json
from scrapy import Request, FormRequest, Selector
from .utils import base_url, get_apac_countries_links, get_paging_info, get_next_url, get_following_text


class IFLR1000Scraper(scrapy.Spider):
	name = "iflr1000_lawyers_scraper"

	def start_requests(self):
		for url in [base_url]:
			yield scrapy.Request(url,  callback = self.parse)  
			

	def parse(self, response):
		links_dict = get_apac_countries_links(response)
		t = len(links_dict.keys())
		i=1
		for country,url in (links_dict.items()):
			self.logger.info(f'\n{">"*50}\n[in parse] {i+1}/{t}:{url}\n{"<"*50}\n')
			i+=1
			yield scrapy.Request(url, callback = self.parse_country_link,
								 meta={"country": country}, headers={"x-requested-with":"XMLHttpRequest"}
								 ) 

	def parse_country_link(self, response):
		paging_info= get_paging_info(response)
		paging_info["country"] = response.meta.get("country")
		current_page = int(paging_info["data-current-page"])
		total_pages = int(paging_info["data-total-pages"])
		rows = response.css("div.lawyersList>div.row>div")
		current_results = len(rows)
		next_page = current_page+1 if current_page<total_pages else None

		for r in rows:
			yield {
				"Start Link": response.url,
				"Lawyer Name": r.css("a div h4::text").extract_first().strip(),
				"Lawyer Link": base_url + r.css("a::attr('href')").extract_first(),
				"Lawyer Jurisdiction": get_following_text(p=r, text="Jurisdiction:"),
				"Lawyer Practice Area": get_following_text(p=r, text="Practice area:"),
				"Lawyer Rating": get_following_text(p=r, text="Rating:"),
				"Lawyer Industry": get_following_text(p=r, text="Industry sector:"),
				"Lawyer Bar Admission": get_following_text(p=r, text="Bar admission:"),
				"Current Results": current_results,
				"Current Page": current_page,
				"Total Pages": total_pages
			} 

		if next_page:
			next_url = get_next_url(response.url, pageNumber=next_page)
			self.logger.info(f'NEXT PAGE >>> {next_page}/{total_pages}')
			yield scrapy.Request(
				next_url, callback = self.parse_country_link,
				headers={"x-requested-with":"XMLHttpRequest"}
			)
		
		self.logger.info(f'\n{"."*150}')
		self.logger.info(f'\nNextPage:{next_page}\nCurrentPage:{current_page}\nTotalPages:{total_pages}\nCurrentResults:{current_results}\n')
		self.logger.info(f'\n{"."*150}\n')



class IFLR1000Scraper(scrapy.Spider):
	name = "iflr1000_firms_scraper"

	def start_requests(self):
		for url in [base_url]:
			yield scrapy.Request(url,  callback = self.parse)  
			

	def parse(self, response):
		links_dict = get_apac_countries_links(response, for_firm_link=True) 
		t = len(links_dict.keys())
		i=1
		for country,url in (links_dict.items()):
			self.logger.info(f'\n{">"*50}\n[in parse] {i+1}/{t}:{url}\n{"<"*50}\n')
			i+=1
			yield scrapy.Request(url, callback = self.parse_country_link,
								 meta={"country": country}, headers={"x-requested-with":"XMLHttpRequest"}
								 ) 

	def parse_country_link(self, response):
		
		country = response.meta.get("country")
		rankings = response.css("div[class='panel panel-default rankings']")
		
		for r in rankings:
			practice_area = r.css("h5::text").extract_first()
			tierList = r.css("div[class='tierList'] div")
			for tier in tierList:
				rank = tier.css("::attr('class')").extract_first()
				if rank == "collapse":
					continue
				firm_list = tier.css("ul[class='list-group'] li a")
				for firm in firm_list:
					yield {
						"Start Link": response.url,
						"Firm Name": firm.css("::text").extract_first(),
						"Firm Link": base_url+firm.css("::attr('href')").extract_first() if firm.css("::attr('href')") else "",
						"Practice Area": practice_area,
						"Rank": rank,
						"Country": country
					} 