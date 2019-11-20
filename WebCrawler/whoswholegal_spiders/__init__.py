# encoding:utf-8
import os, sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
import string
import scrapy
import json
from scrapy import Request, FormRequest, Selector
from .utils import gen_urls_by_country_practice_area, gen_form_data, get_next_url


class LawyerScraper(scrapy.Spider):
	name = "whoswholegal_scraper"

	def start_requests(self):

		# urls = ["https://whoswholegal.com/market-insight-tool?PracticeArea=49&RegionID=&CountryID=032"]
		# urls = [["https://whoswholegal.com/market-insight-tool?PracticeArea=46&RegionID=&CountryID=036"], ["https://whoswholegal.com/market-insight-tool?PracticeArea=56&RegionID=&CountryID="]]
		# urls = [["https://whoswholegal.com/market-insight-tool?PracticeArea=68&RegionID=&CountryID=608"]]
		urls = list(gen_urls_by_country_practice_area())
		for i,url in enumerate(urls):
			self.logger.info(f'\n{">"*50}\n[in start_requests] {i+1}/{len(urls)}\n{"<"*50}\n')
			yield scrapy.Request(url=url[0], callback=self.parse)
			

	def parse(self, response):

		next_url = response.meta.get("next_url")

		if next_url:
			get_request_url = next_url
			form_data = gen_form_data(next_url)
			# self.logger.info(f'\n{"-"*50}\n[in parse] next_url:{next_url}\n{"-"*50}\n')
			
		else:
			get_request_url = response.url
			form_data = gen_form_data(response.url)
			# self.logger.info(f'\n{">"*50}\n[in parse] get_request_url:{get_request_url}\n{"<"*50}\n')
			
		yield FormRequest.from_response(response,
					url="https://whoswholegal.com/AfoCustom/LBR/cfc/LBR_MIDisplay.cfc?method=getResults",
					formdata=form_data, callback=self.parse_lawyers_section,
					headers={'Content-Type':'application/x-www-form-urlencoded'},
					meta={"get_request_url": get_request_url},
				)
  

	def parse_lawyers_section(self, response):

		get_request_url = response.meta["get_request_url"]

		try:
		  try: #try parsing to dict
		  	dataform = str(response.body_as_unicode()).strip("'<>() ").replace('\'', '\"')
		  	response_dict = json.loads(dataform)
		  except Exception as e:
		  	self.logger.error(f"in [json.loads(dataform) strip replace way] {sys.exc_info()}")
		  	dataform = response.body_as_unicode()
		  	response_dict = json.loads(dataform)
		except Exception as e:
			self.logger.error(f"in [json.loads(dataform)] {sys.exc_info()}")
			response_dict = {}

		if response_dict:
		
			content = response_dict["CONTENT"]
			more_results = response_dict["MORE"]
			total_resutls = response_dict["TOTAL"]
			last_results = response_dict["LAST"]
			total_member_types = response_dict["TOTALMEMBERTYPES"]

			self.logger.info(
				f'\n{"-"*150}\n[in parse_lawyers_section] TOTAL:{total_resutls}, '
				f'TOTALMEMBERTYPES:{total_member_types}, MORE:{more_results}\n{"-"*150}\n')

			selector = Selector(text=json.loads(response.body_as_unicode())["CONTENT"], type="html")

			results = selector.css(".aos-PB20px")
			
			for r in results:

				loc = r.css(".aos-ML5px+ .aos-ML5px::text").extract_first() or r.css(".aos-PT10px div+ .aos-DS37-N .aos-NM::text").extract_first()
				yield {
					"Start URL": get_request_url,
					"Lawyer Name": r.css("h2>a::text").extract_first(),
					"Lawyer Link": r.css("h2>a::attr('href')").extract_first(),
					"Firm Name": r.css(".aos-NM.aos-FWB::text").extract_first(),
					"Location": loc,
					"Country": (loc or "").split(", ")[-1],
					"Practice Area": r.css(".aos-MR20px .aos-FWB::text").extract_first(),
					"Lawyer Overview": r.css("p::text").extract_first(),
					"Lawyer Ranking": r.css(".aos-MT4px > .aos-NM .aos-FWB::text").extract_first()
				}
			
			if more_results:
				next_url = get_next_url(get_request_url,last_results+1)
				yield scrapy.Request(
					url=next_url,
					callback=self.parse, meta={"next_url": next_url},
				)
