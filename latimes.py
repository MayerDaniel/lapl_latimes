'''
Read the LA Times every day on your ereader with just a library card
For educational purposes only.
'''
import re
import requests
import datetime
from pprint import pprint
from playwright.sync_api import sync_playwright, expect

USER = "REPLACEME"
PASS = "REPLACEME"

def get_date():
	now = datetime.datetime.now()
	return now.strftime("%B-%d-%Y").split("-")

def dedup(seq):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (x in seen or seen_add(x))]

def run(playwright, articles, index=0):
	print("Logging in...")
	chrome = playwright.chromium
	browser = chrome.launch(headless=False)
	context = browser.new_context()
	page = context.new_page()
	page.goto('https://ezproxy.lapl.org/login?url=https://www.proquest.com/latimes?accountid=6749')
	page.locator("[name=user]").fill(USER)
	page.locator("[name=pass]").fill(PASS)
	page.get_by_role("button").click()
	page.wait_for_url("**latimes*")
	page.goto("https://www.proquest.com/latimes/advanced?accountid=6749")

	print("Searching for today's articles...")
	d = get_date()
	page.get_by_text("Accept all").click()
	page.get_by_label("Full text").check()
	page.get_by_text("Newspapers").check()
	page.locator("[name=select_multiDateRange]").select_option('ON')
	page.locator("[id=month2]").select_option(d[0].lstrip("0"))
	page.locator("[id=day2]").select_option(d[1].lstrip("0"))
	page.locator("[id=year2]").fill(d[2])
	page.get_by_text("Result page options").click()
	page.get_by_label("Exclude duplicate documents", exact=True).check()
	page.get_by_label("Items per page:", exact=True).select_option('100')
	page.locator("#searchToResultPage").click()
	page.wait_for_url("**results*")

	print("Grabbing articles...")
	articles = {}
	links = page.locator(".previewTitle").all()
	hrefs_full = [link.get_attribute('href') for link in links]
	hrefs = dedup(hrefs_full)
	cursor = index
	for href in hrefs[index:]:
		try:
			page.goto(href)
			header = page.query_selector('h1').inner_html()
			text = page.query_selector('text').inner_html()

			page.get_by_role("link", name="Details").click()
			raw_section = 'Sectionless'
			page.wait_for_url("**citation*")
			for tr in page.locator(".display_record_indexing_row").all():
				if tr.text_content().strip().startswith("Section "):
					raw_section = tr.text_content().strip().replace("Section ", "")
					break
			sections = raw_section.split("; ")
			section = sections[0]
			subsection = sections[-1]

			if section not in articles:
				articles[section] = {}
			if subsection not in articles[section]:
				articles[section][subsection] = {}
			articles[section][subsection][header] = text
			cursor += 1
		except AttributeError:
			run(playwright, articles, index=cursor)
			break

	i = 0
	with open('latimes/head.html', 'r') as file:
		head = file.read()

	for section,subsections in articles.items():
		body = head
		body += f'\n<h1>SECTION: {section.upper()}</h1>\n</body></html>'
		with open(f'latimes/news{i}.html', 'w') as out:
			out.write(body)
		i += 1
		for subsection_title, subsection_articles in subsections.items():
			body = head
			body += f'\n<h1>SUBSECTION: {subsection_title.upper()}</h1>\n'
			for article_title, article_text in subsection_articles.items():
				article_title = article_title.replace("&amp;", "and")
				article_text = article_text.replace("&amp;", "and")
				article_text = article_text.replace('<meta content="http://www.w3.org/2002/08/xhtml/xhtml1-strict.xsd" name="ValidationSchema"><title></title>', '')
				body += f'\n<h2>{article_title}</h2>\n'
				body += article_text
				body += '\n'
			body += '\n</body></html>'
			with open(f'latimes/news{i}.html', 'w') as out:
				out.write(body)
			i += 1


with sync_playwright() as playwright:
	articles = {}
	run(playwright, articles)
