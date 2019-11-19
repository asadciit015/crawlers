# encoding:utf-8
import os 
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
import string
import scrapy
import json
from scrapy import Request
from .utils import get_department, get_elem_text_safe, parse_ranked_lawyers



class FirmScraper(scrapy.Spider):
	name = "chamber_firm_scraper"

	def start_requests(self):
		" PICK all asia-pacific link URLS SCRAPED BY chambers_link_gen.py"
		# start_urls_asiapacific_firms
		with open(os.path.join(ROOT_DIR,"start_urls.txt"), "rt") as f:
			for url in f.readlines():
				yield scrapy.Request(url=url, callback=self.parse_rankings)


	def parse_rankings(self, response):
		pacific_area = response.css("h2::text").extract_first().strip()
		country = pacific_area.split("in ")[-1].strip() if "in" in pacific_area else None
		for band_sel in response.css(".col-lg-3"):
			if band_sel.css("a.text-dark::text").extract_first():
				for rank in band_sel.css("a.text-dark"):
					department_url = rank.css("::attr('href')").extract_first().strip() 
					_rank = {
						"Ranking":band_sel.css("::text").extract_first().strip(),
						"Start URL":response.url,
						# "Rank Department": rank.css("::text").extract_first().strip(),
						"Practice Area": pacific_area,
						"Country": country
					}
					yield scrapy.Request(response.urljoin(department_url),
										meta={"rank": _rank}, dont_filter = True,
										callback=self.parse_department)


	def parse_department(self, response):
		rank = response.meta.get('rank')
		firm_url = response.css("a[href^='/law-firm/']::attr('href')").extract_first()
		department = get_department(response)
		department.update(rank)
		return scrapy.Request(response.urljoin(firm_url),dont_filter = True,
							 meta={"department": department},
							 callback=self.parse_firm)


	def parse_firm(self, response):
		department = response.meta.get('department')
		firm  = {
			"Firm Name": get_elem_text_safe("h1>b::text", response, extract_index=0),
			"Firm Link":response.url,
			"Firm Logo": get_elem_text_safe(".logo-img::attr('src')", response, extract_index=0),
			"Firm Current View": get_elem_text_safe("[class='col pl-0']>a::text", response, extract_index=0),
			# "Firm Also Ranked In":  ", ".join(response.css("a[href^='/law-firm/']::text").extract()[1:]) if len(response.css("a[href^='/law-firm/']::text"))>=1 else None,
			"Firm Overview": "\n".join(response.css("div.py-3>p::text").extract())
		}
		firm.update(department)
		return firm


class LawyerScraper(scrapy.Spider):
	name = "chamber_lawyer_scraper"

	def start_requests(self):
		" PICK all firm links from chamber_firm_scraper spider"
		# start_urls_asiapacific_firms
		with open(os.path.join(ROOT_DIR,"start_urls_firms.txt"), "rt") as f:
			for url in f.readlines():
				yield scrapy.Request(url=url, callback=self.parse_ranked_lawyers_section)

	def parse_ranked_lawyers_section(self, response):
		for l in parse_ranked_lawyers(response):
			yield l
