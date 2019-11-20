from urllib.request import urlretrieve
from urllib.parse import parse_qsl, urlsplit, urlencode

base_url = "https://www.iflr1000.com"

def get_url_query_dict(url):
	return dict(parse_qsl(urlsplit(url).query)) if url not in ( "", None,) else {}


def gen_url_with_query_dict(url, **qs):
	uri = urlsplit(url)
	parsed_url = '{uri.scheme}://{uri.netloc}{uri.path}'.format(uri=uri)
	parsed_url_qs = get_url_query_dict(url)
	parsed_url_qs.update(**qs)
	parsed_url_qstr = urlencode(parsed_url_qs)
	return f"{parsed_url}?{parsed_url_qstr}"


def get_url(url, pageNumber=1, pageSize=25):
	if "/Search/" not in url:
		url_parts = url.split("/")
		country = url_parts[2]
		JurisdictionIds = url_parts[-1].split("#rankings")[0]
		return (f"{base_url}/Search/JurisdictionLawyers/"
					f"{country}/{JurisdictionIds}?pageNumber={pageNumber}"
					f"&pageSize={pageSize}&JurisdictionIds={JurisdictionIds}")

def get_next_url(url, pageNumber):
	return gen_url_with_query_dict(url, pageNumber=pageNumber)



def get_links(response, for_firm_link=False):
	# to get links from main page
	return {
		r.css("::text").extract_first(): base_url+r.css("::attr('href')").extract_first() if for_firm_link
			else get_url(r.css("::attr('href')").extract_first())
		for r in response.css(".columnList a") if r.css("::text").extract_first()
	}
		

def get_apac_countries():
	return ["Australia","Bangladesh","Brunei","Cambodia","China","Hong Kong","India","Indonesia","Japan","Kazakhstan","Laos", "Lao People's Democratic Republic", "Macao", "Macau","Malaysia","Mongolia","Myanmar","New Zealand","Pakistan","Philippines","Singapore","Korea", "North Korea", "Sri Lanka","Taiwan","Thailand","Vietnam"]


def get_apac_countries_links(response, for_firm_link=False):
	return {c:l for c,l in get_links(response, for_firm_link).items() if c in get_apac_countries()}


def get_paging_info(response):
	elem = response.css("input[type='hidden']")
	return {
		"data-total-items": elem.css("::attr('data-total-items')").extract_first(),
		"data-first-item": elem.css("::attr('data-first-item')").extract_first(),
		"data-last-item": elem.css("::attr('data-last-item')").extract_first(),
		"data-current-page": elem.css("::attr('data-current-page')").extract_first(),
		"data-total-pages": elem.css("::attr('data-total-pages')").extract_first(),
	}


def get_following_text(p, text):
	t = p.xpath(f".//label[contains(text(),'{text}')]/../following-sibling::div[1]/text()").extract_first()
	return t.strip() if t else ""
	
# if __name__ == '__main__':
# 	u = "/Jurisdiction/Bangladesh/Rankings/663#rankings"
# 	url = get_url(u)
# 	print(url)
# 	next_url = get_next_url(url, pageNumber=2)
# 	print(next_url)