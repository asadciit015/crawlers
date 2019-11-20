# encoding:utf-8
import os 
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
# import string
# import scrapy
# from scrapy import Request
import json

base_url = "http://www.legal500.com"


def get_country(response):
	country = response.css("h1>a::text").extract_first()
	if not country and len(response.url.split("/"))>=4:
		country = response.url.split("/")[4].title()
	return country

def parse_departments(response):
	for department in response.css(".recommended"):
		practice_area_elem = department.css("h4::text").extract_first()
		# practice_area_firm = practice_area_elem.split(": ") if practice_area_elem else practice_area_elem
		practice_area = practice_area_elem
		for li_rank in department.css("li[class^='tier rank-']"):
			rank = li_rank.css('.rank::text').extract_first()
			for firm in li_rank.css('ul>li>a, ul>li>plain'):
				firm_name = firm.css("::text").extract_first()
				_firm_link = firm.css("::attr('href')").extract_first()
				firm_link  = f"{base_url}{_firm_link}" if _firm_link else None
				yield {
						"Visited URL":response.url,
						"Ranking":rank,
						"Firm Name": firm_name,
						"Practice Area": practice_area,
						"Firm Link": firm_link,
						"Country": get_country(response)
					}


def find_department(firm_name, departments):
	for department in departments:
		if department["Firm Name"].split(": ")[0].strip().lower()==firm_name.strip().lower():
			return department
	return {}



def parse_lawyers(response):
	departments = list(parse_departments(response))
	for leading_individual in response.css("div.leading_individuals, div.next_generation_lawyers"):
		lawyer_rank = leading_individual.css("h4::text").extract_first().strip().title()
		# lawyer_rank = lawyer_rank.replace(" Individuals", " Lawyer").replace(" Partners", " Lawyer")
		for lawyer_sel in  leading_individual.css("ul>li"):
			lawyer_and_firm_a_tags = lawyer_sel.css("a")
			lawyer_and_firm_plain_tags = lawyer_sel.css("plain")

			if len(lawyer_and_firm_a_tags)==1:
				firm_name = lawyer_sel.css("a::text").extract_first().strip()
				lawyer_name = "".join(lawyer_sel.css("::text").extract_first().split("\n")).strip()
				lawyer_name = lawyer_name[:-2] if ' -' == lawyer_name[-2:] else lawyer_name
				lawyer_link = None
			elif len(lawyer_and_firm_a_tags)==2:
				lawyer_name = lawyer_and_firm_a_tags[0].css("::text").extract_first().strip()
				_lawyer_link = lawyer_and_firm_a_tags[0].css("::attr('href')").extract_first().strip()
				lawyer_link = f"{base_url}{_lawyer_link}"
				firm_name = lawyer_and_firm_a_tags[1].css("::text").extract_first().strip()
			elif len(lawyer_and_firm_plain_tags)==1:
				lawyer_name = "".join(lawyer_sel.css("::text").extract_first().split("\n")).strip()
				lawyer_name = lawyer_name[:-2] if ' -' == lawyer_name[-2:] else lawyer_name
				lawyer_link = None
				firm_name = lawyer_sel.css("plain::text").extract_first().strip()
			else:
				print("WARNING:: Cannot retireve lawyer data")
				continue

			department = find_department(firm_name, departments)
			yield { 
					"Start URL":response.url,
					"Lawyer Name":lawyer_name,
					"Lawyer Link":lawyer_link,
					"Lawyer Ranking":lawyer_rank,
					"Firm Name":department.get("Firm Name") or firm_name,
					"Practice Area":department.get("Practice Area"),
					"Firm Link":department.get("Firm Link"),
					"Country":get_country(response)
				}