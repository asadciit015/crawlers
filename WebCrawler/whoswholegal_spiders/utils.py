# encoding:utf-8
import os 
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
# import string
# import scrapy
# from scrapy import Request
import json

"""https://whoswholegal.com/market-insight-tool?PracticeArea=49&RegionID=&CountryID=032"""


from urllib.request import urlretrieve
from urllib.parse import parse_qsl, urlsplit, urlencode


def get_url_query_dict(url):
	return dict(parse_qsl(urlsplit(url).query)) if url not in ( "", None,) else {}


def gen_url_with_query_dict(url, **qs):
	uri = urlsplit(url)
	parsed_url = '{uri.scheme}://{uri.netloc}{uri.path}'.format(uri=uri)
	parsed_url_qs = get_url_query_dict(url)
	parsed_url_qs.update(**qs)
	parsed_url_qstr = urlencode(parsed_url_qs)
	return f"{parsed_url}?{parsed_url_qstr}"

def gen_form_data(url, start=1):
	qs = get_url_query_dict(url)
	return  {	
			"sortby": '1', "designstylecode": '37', "regionid": str(qs.get("RegionID", "")),
			"countryid": str(qs.get("CountryID", "")), "start": str(qs.get("start",1)),
			"practicearea": str(qs.get("PracticeArea", "")), "accountcodeslist":''
		}


def get_next_url(url, start):
	return gen_url_with_query_dict(url, start=start)
	

def get_apac_countries():
	return ["Australia","Bangladesh","Brunei","Cambodia","China","Hong Kong","India","Indonesia","Japan","Kazakhstan","Laos", "Lao People's Democratic Republic", "Macao", "Macau","Malaysia","Mongolia","Myanmar","New Zealand","Pakistan","Philippines","Singapore","Korea", "North Korea", "Sri Lanka","Taiwan","Thailand","Vietnam"]
	

def get_countries():
	countries = json.loads(open(os.path.join(ROOT_DIR, 'country.json'), 'r').read())
	return[ {"CountryID": d[0], "CountryCode":d[1], "CountryName":d[-1]} for d in countries["QCOUNTRIES"]["DATA"]]

def get_practice_areas():
	practice_areas = json.loads(open(os.path.join(ROOT_DIR, 'practice_areas.json'), 'r').read())
	return[ {"PracticeAreaID":v, "PracticeAreaName":k  } for d in practice_areas for k,v in d.items()  ]
		
def gen_urls_by_country_practice_area():
	search_url = "https://whoswholegal.com/market-insight-tool?PracticeArea={0}&RegionID=&CountryID={1}"
	return ( [search_url.format(practice_area["PracticeAreaID"], country["CountryID"]), country["CountryName"]]
		for country in get_countries() for practice_area in get_practice_areas()
			if country["CountryName"] in get_apac_countries()		

		)

# f_data = {"sortby": 1, "designstylecode": '', "regionid": '', "countryid":'032', "practicearea":49, "accountcodeslist":'', "start": 1}
# url = "https://whoswholegal.com/AfoCustom/LBR/cfc/LBR_MIDisplay.cfc?method=getResults"
# yield FormRequest(url, formdata=f_data, method='POST', headers={'Content-Type':'application/json'})

# my_data = {'field1': 'value1', 'field2': 'value2'}
# request = scrapy.Request( url, method='POST',  body=json.dumps(f_data),  headers={'Content-Type':'application/json'} )


	# uri = urlsplit(url)
	# parsed_url = '{uri.scheme}://{uri.netloc}{uri.path}'.format(uri=uri)
	# parsed_url_qs = get_url_query_dict(url)
	# parsed_url_qs.update(**qs)
	# parsed_url_qstr = urlencode(parsed_url_qs)
	# return f"{parsed_url}?{parsed_url_qstr}"


if __name__ == '__main__':
	# print(json.dumps(get_countries(), indent=2))
	# print(json.dumps(get_practice_areas(), indent=2))
	# print(json.dumps(get_apac_countries(), indent=2))

	# urls = list(gen_urls_by_country_practice_area())
	# print(len(urls))
	# print(json.dumps(urls, indent=2))
	# for url in urls:
	# 	print(url[0],"\t",url[1])

	# url="https://whoswholegal.com/market-insight-tool?PracticeArea=51&RegionID=&CountryID=036"
	
	url="https://whoswholegal.com/market-insight-tool?PracticeArea=52&RegionID=&CountryID=036"
	next_url = get_next_url(url,151)
	print(next_url)
	print(gen_form_data(next_url))
	
	# 97 results test ===> https://whoswholegal.com/market-insight-tool?PracticeArea=56&RegionID=&CountryID=



# 2019-10-23 16:20:53 [scrapy.core.scraper] ERROR: Spider error processing <GET https://whoswholegal.com/market-insight-tool?PracticeArea=444&RegionID=&CountryID=410> (referer: None)


# 2019-10-23 16:32:25 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://whoswholegal.com/AfoCustom/LBR/cfc/LBR_MIDisplay.cfc?method=getResults&q=&sortby=1&designstylecode=37&regionid=&countryid=608&start=1&practicearea=68&accountcodeslist=> (referer: https://whoswholegal.com/market-insight-tool?PracticeArea=68&RegionID=&CountryID=608)
# 2019-10-23 16:32:25 [scrapy.core.scraper] ERROR: Spider error processing <GET https://whoswholegal.com/AfoCustom/LBR/cfc/LBR_MIDisplay.cfc?method=getResults&q=&sortby=1&designstylecode=37&regionid=&countryid=608&start=1&practicearea=68&accountcodeslist=> (referer: https://whoswholegal.com/market-insight-tool?PracticeArea=68&RegionID=&CountryID=608)
# Traceback (most recent call last):
#   File "c:\users\user\envs\crawler\lib\site-packages\scrapy\utils\defer.py", line 102, in iter_errback
#     yield next(it)
#   File "c:\users\user\envs\crawler\lib\site-packages\scrapy\core\spidermw.py", line 84, in evaluate_iterable
#     for r in iterable:
#   File "c:\users\user\envs\crawler\lib\site-packages\scrapy\spidermiddlewares\offsite.py", line 29, in process_spider_output
#     for x in result:
#   File "c:\users\user\envs\crawler\lib\site-packages\scrapy\core\spidermw.py", line 84, in evaluate_iterable
#     for r in iterable:
#   File "c:\users\user\envs\crawler\lib\site-packages\scrapy\spidermiddlewares\referer.py", line 339, in <genexpr>
#     return (_set_referer(r) for r in result or ())
#   File "c:\users\user\envs\crawler\lib\site-packages\scrapy\core\spidermw.py", line 84, in evaluate_iterable
#     for r in iterable:

# "c:\users\user\envs\crawler\lib\site-packages\scrapy\core\spidermw.py", line 84, in evaluate_iterable
#     for r in iterable:
#   File "c:\users\user\envs\crawler\lib\site-packages\scrapy\spidermiddlewares\depth.py", line 58, in <genexpr>
#     return (r for r in result or () if _filter(r))
#   File "C:\code\python_code\WebCrawler\WebCrawler\whoswholegal_spiders\__init__.py", line 106, in parse_lawyers_section
#     response_dict = json.loads(response.body_as_unicode())
#   File "C:\Program Files\Python37\Lib\json\__init__.py", line 348, in loads
#     return _default_decoder.decode(s)
#   File "C:\Program Files\Python37\Lib\json\decoder.py", line 337, in decode
#     obj, end = self.raw_decode(s, idx=_w(s, 0).end())
#   File "C:\Program Files\Python37\Lib\json\decoder.py", line 355, in raw_decode
#     raise JSONDecodeError("Expecting value", s, err.value) from None
# json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
# 2019-10-23 16:36:52 [whoswholegal_scraper] INFO:
# --------------------------------------------------------------------------