# encoding:utf-8
import os 
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
import string
import scrapy
from scrapy import Request
import json


def get_location_names():
	with open(os.path.join(ROOT_DIR,"../asia_pacific_countries.txt"), "rt") as f:
            return [loc.strip() for loc in f.readlines()]

def get_location_ids():
	locations = json.loads(open(os.path.join(ROOT_DIR, 'files/locations.json'), 'r').read())
	return [ loc['id'] for loc in locations if loc["description"].lower() in 
				[l.lower().strip() for l in get_location_names() ] 
		]
		# if loc["description"].lower()==country.lower().strip():
		#     return f"locationId={loc['id']}"

def get_practiceareas_urls():
	url = "https://api.chambers.com/api/publications/8/locations/{}/practiceareas"
	return [ url.format(location_id) for location_id in get_location_ids()]


# print(get_location_ids())
# print(get_practiceareas_urls())
# '[{"subsectionTypeId":1,"id":852,"description":"General Business Law"}]'

class ChambersLinkGenSpider(scrapy.Spider):
	name = "chambers_link_gen"

	def start_requests(self):
		for url in get_practiceareas_urls():
			yield scrapy.Request(url=url, callback=self.parse)


	def parse(self, response):
		locationId = response.url.split("/")[-2]
		base = ("https://chambers.com/guide/asia-pacific?publicationTypeId=8&practiceAreaId={practiceAreaId}"
				"&subsectionTypeId={subsectionTypeId}&locationId={locationId}")

		practiceareas = json.loads(response.text)

		for practicearea in practiceareas:
			subsectionTypeId = practicearea['subsectionTypeId']
			practiceAreaId =  practicearea['id']
			yield {"url":base.format(practiceAreaId=practiceAreaId, subsectionTypeId=subsectionTypeId, locationId=locationId)}
