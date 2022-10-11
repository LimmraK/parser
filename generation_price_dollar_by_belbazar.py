from lxml import html

import requests
import lxml
import json

class generation_price_dollar_by_belbazar():

    
    def __init__(self):
        with open('config.json') as f:
            self.templates = json.load(f)

    def generation_cost_dollar(self):

        result = requests.post(self.templates["url"]["url_women_new"], data = self.templates["blank_for_dollars"],
                               headers = self.templates["headers"], proxies = self.templates["proxies"], timeout = 60)
        tree = html.fromstring(result.content, parser = lxml.html.HTMLParser(encoding = 'utf-8'))                     
        usd =  tree.xpath(self.templates["xpath"]["price"])

        result = requests.post(self.templates["url"]["url_women_new"], data = self.templates["blank_for_rub"], 
                               headers = self.templates["headers"], proxies = self.templates["proxies"], timeout = 60)
        tree = html.fromstring(result.content, parser = lxml.html.HTMLParser(encoding = 'utf-8'))                     
        rub =  tree.xpath(self.templates["xpath"]["price"])


        self.cost_dollars_on_belbazar_old = float(rub[0]) / float(usd[0]) + 1.5
        print(self.cost_dollars_on_belbazar_old)
        