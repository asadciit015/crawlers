# encoding:utf-8
import os 
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
import json
base_url = "https://chambers.com"

# def get_script_json(path):
# 	with open(os.path.join(ROOT_DIR, path), "rt", encoding="utf-8") as f:
# 		js = f.read()
# 		js_d = js.replace("&q;",'"').replace("a;", "")
# 		return json.loads(js_d)

def get_script_json(response):
	js = response.xpath("//script[@id='serverApp-state']/text()").extract_first() or "{}"
	js_d = js.replace("&q;",'"').replace("a;", "")
	return json.loads(js_d)


def get_ranked_departments(d):
	r = [d[k] for k,v in d.items() if "/ranked-departments" in k ]
	r = r[0] if len(r) >0 else {}
	return r.get("body", {}).get("locations", [])

def get_ranked_lawyers(d):
	r = [d[k] for k,v in d.items() if "/ranked-lawyers" in k ]
	r = r[0] if len(r) >=1 else {}
	r = r.get("body", {}).get("groups", [])
	r = r[0] if len(r)>0 else {}
	return r.get("practiceAreas", [])

def get_ranked_firm(d):
	r = [d[k] for k,v in d.items() if "profile-basics?" in k ]
	r = r[0] if len(r) >0 else {}
	organisation =  r.get("body", {}).get("organisation", {})
	canonicalPath = r.get("body", {}).get("canonicalPath", {})
	contact = r.get("body", {}).get("contact", {})
	address = contact.get("address",{})
	return {
		"Firm Name":organisation.get("organisationName"),
		"Firm Parent Name":organisation.get("parentOrganisationName"),
		"Firm Location":organisation.get("location",{}).get("description"),
		"Firm Link": canonicalPath,
		"Firm Contact Website":contact.get("web"),
		"Firm Contact Email":contact.get("email"),
		"Firm Contact Phone":contact.get("phone"),
		"Firm Contact Fax":contact.get("fax"),
		"Firm Address":address.get("addressLines"),
		"Firm PostalCode":address.get("postcode"),
		"Firm Town":address.get("town"),
		"Firm Region":address.get("region"),
		"Firm Country":address.get("country")
	}



def parse_ranked_lawyers(response):
	js_dict = get_script_json(response)
	ranked_departments = get_ranked_departments(js_dict)
	ranked_lawyers = get_ranked_lawyers(js_dict)
	ranked_firm = get_ranked_firm(js_dict)
	for r in ranked_lawyers:
		department = r.get("description", "")
		for loc in r.get("individualsInLocations", []):
			country = loc.get("description")
			country_addon = f" in {country}" if country else ""
			for r_entity in loc.get("rankedEntities", []):
				rank = r_entity.get("rankings", [])[0]
				practice_area = f"{department.replace('Department','')}{country_addon}"
				l = {
					"Lawyer Name":r_entity.get("displayName"),
					"Lawyer Link": f'{base_url}{"/".join( r_entity.get("routerLink", []) )}' ,
					"Department":department,
					"Rank":rank.get("rankingDescription"),
					"Practice Area":practice_area,
					"Country":country,
					"Start URL":response.url
				}
				l.update(ranked_firm)
				yield l


def get_elem_text_safe(css_finder, response, extract_index=0):
	elem = response.css(css_finder)
	if elem:
		if extract_index <=0:
			elem_extracted = elem.extract_first()
			if elem_extracted:
				return elem_extracted.strip()
		elif extract_index ==1:
			try:
				elem_extracted = elem[extract_index].extract()
				return elem_extracted.strip()
			except:
				return
		else:
			return [e.strip() for e in elem.extract()]


def get_department(response):
	return {
			"Department":get_elem_text_safe("h1[class='mb-3 department']>b::text", response, extract_index=0),
			"Department Link":response.url,
			"Department Logo":get_elem_text_safe(".logo-img::attr('src')", response, extract_index=0),
			"Country":get_elem_text_safe("h6>i::text", response, extract_index=0),
			# "Department Current View": get_elem_text_safe("a[href^='/department/']::text", response, extract_index=0),
			"Department Overview": "\n".join(response.css("div.py-3>p::text").extract())
			}


# d = parse_ranked_lawyers("test_script_json.txt")

# for i in d:
# 	print(json.dumps(i,indent=2)) 
# 	print("\n\n")