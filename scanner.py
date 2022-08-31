#!usr/bin/env python

from urllib import response
import requests
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class Scanner:
    def __init__(self, url, ignore_links):
        self.session = requests.Session()
        self.target_url = url
        self.target_links = []
        self.links_to_ignore = ignore_links

    def extract_links_from(self, url):
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"', response.content.decode(errors="ignore"))

    def crawl(self, url=None):
        if url == None:
            url = self.target_url
        href_links = self.extract_links_from(url)
        for link in href_links:
            link = urljoin(url, link)

            if "#" in link:
                link = link.split("#")[0]

            if self.target_url in link and link not in self.target_links and link not in self.links_to_ignore:
                self.target_links.append(link)
                print(link)
                self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.content, 'html.parser')
        return parsed_html.findAll("form")

    def submit_form(self, form, value, url):
        action = form.get("action")
        post_url = urljoin(url, action)
        method = form.get("method")

        inputs_list = form.findAll("input")
        post_data = {} 
        for input in inputs_list:
            input_name = input.get("name")
            input_type = input.get("type")
            input_value = input.get("value")
            if input_type == "text":
                input_value = value
            post_data[input_name] = input_value
        if method == "post":
            return self.session.post(post_url, data=post_data)
        return self.session.get(post_url, params=post_data)

    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                print("\n\n[+] Testing form in " + link)
                is_vuln_to_xss = self.test_xss_in_form(form, link)
                if is_vuln_to_xss:
                    print("\n[***] XSS vuln in " + link + " in the form")
                    print(form)

            if "=" in link:
                print("\n\n[+] Testing " + link)
                is_vuln_to_xss = self.test_xss_in_link(link)
                if is_vuln_to_xss:
                    print("\n[***] XSS vuln in " + link)

    def test_xss_in_link(self, url):
        xss_test_script = "<scRipt>alert('lol')</scriPt>".encode()
        url = url.replace("=", "=" + xss_test_script.decode())
        response = self.session.get(url)
        return xss_test_script in response.content
            
    
    def test_xss_in_form(self, form, url):
        xss_test_script = "<scRipt>alert('lol')</scriPt>".encode()
        response = self.submit_form(form, xss_test_script, url)
        return xss_test_script in response.content