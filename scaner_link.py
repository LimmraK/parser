from lxml import html

from db_kit import *

import requests
import json
import lxml



class scaner():


    def __init__(self):
        with open('config.json') as f:
            self.templates = json.load(f)
        self.database = db_kit(self.templates["data_connect_to_database"]["host"], 
                               self.templates["data_connect_to_database"]["login"],
                               self.templates["data_connect_to_database"]["password"],
                               self.templates["data_connect_to_database"]["name_database"],
                               self.templates["data_connect_to_database"]["charset"])    

    def get_page_men(self): 
        result = requests.get(self.templates["url"]["url_belbazar_page_men"])
        tree = html.fromstring(result.content)
        number_page_men = tree.xpath(self.templates["xpath"]["number_page_xpath"])[0]
        return number_page_men
        
    def get_page_women(self): 
        result = requests.get(self.templates["url"]["url_belbazar_page_women"])
        tree = html.fromstring(result.content)
        number_page_women = tree.xpath(self.templates["xpath"]["number_page_xpath"])[0]
        return number_page_women

    def getter_link_men_belbazar(self, number_page_men):
        mass_link_men_belbazar = []
        for page in range(int(number_page_men)):
            page_info_men = requests.get(self.templates["url"]["url_belbazar_page_men"] + "?page=" + str(page + 1))
            tree = html.fromstring(page_info_men.content, parser = lxml.html.HTMLParser(encoding='utf-8'))
            box_dress = tree.xpath(self.templates["xpath"]["box_dress_xpath"])
            for bypassing in box_dress:
                mass_temp = []
                link = bypassing.xpath(self.templates["xpath"]["link_dress_xpath"])
                price = bypassing.xpath(self.templates["xpath"]["price"])
                mass_temp.append(link[0])
                mass_temp.append(price[0])
                mass_link_men_belbazar.append(mass_temp)     
        return mass_link_men_belbazar

    '''def getter_link_women_belbazar(self, number_page_women):
        mass_link_women_belbazar = []
        for page in range(int(number_page_women)):
            page_info_men = requests.get(self.templates["url"]["url_belbazar_page_women"] + "?page=" + str(page + 1))
            tree = html.fromstring(page_info_men.content, parser = lxml.html.HTMLParser(encoding='utf-8'))
            box_dress = tree.xpath(self.templates["xpath"]["box_dress_xpath"])
            for bypassing in box_dress:
                mass_link_women_belbazar.append(bypassing[0])      
        return mass_link_women_belbazar'''

    def getter_link_women_belbazar(self, number_page_women):
        mass_link_women_belbazar = []
        number_page_women = 1
        #for page in range(int(number_page_women)):
        page_info_women = requests.get(self.templates["url"]["url_belbazar_page_women"] + "?page=" + str(number_page_women + 1))
        tree = html.fromstring(page_info_women.content, parser = lxml.html.HTMLParser(encoding='utf-8'))
        box_dress = tree.xpath(self.templates["xpath"]["box_dress_xpath"])
        for bypassing in box_dress:
            mass_temp = []
            link = bypassing.xpath(self.templates["xpath"]["link_dress_xpath"])
            price = bypassing.xpath(self.templates["xpath"]["price"])
            mass_temp.append(link[0])
            mass_temp.append(str(price[0]))
            mass_link_women_belbazar.append(mass_temp)     
        return mass_link_women_belbazar
    

    def generator_full_link_belbazar(self, mass_link_women_belbazar: list(), mass_link_men_belbazar: list()):
        mass_link_belbazar = mass_link_men_belbazar + mass_link_women_belbazar
        return mass_link_belbazar

    def getter_link_odeta_u_nas(self):
        mass_link_odeta_u_nas = []
        links = self.database.sql_zapros("SELECT belbazar_url, sebes_vb FROM " + self.templates["database_table_name"]["osd_tovar"])
        for link in range(len(links)):
            mass_temp = []
            mass_temp.append(links[link][0])
            mass_temp.append(str(links[link][1])[:-3])
            mass_link_odeta_u_nas.append(mass_temp) 
        return mass_link_odeta_u_nas

    def update_all_models(self, full_link_belbazar: list(), mass_link_odeta_u_nas: list()):
        mass_temp_url_belbazar = []
        mass_temp_url_odeta_u_nas = []
        mass_temp_price_belbazar = []
        mass_temp_price_odeta_u_nas = []

        for i in full_link_belbazar:
            mass_temp_url_belbazar.append(i[0])
            mass_temp_price_belbazar.append(i[1])

        for i in mass_link_odeta_u_nas:
            mass_temp_url_odeta_u_nas.append(i[0])
            mass_temp_price_odeta_u_nas.append(i[1])

        set_link_belbazar = frozenset(mass_temp_url_belbazar)
        mass_link_find = [link for link in set_link_belbazar if link in mass_temp_url_odeta_u_nas]

        a = mass_temp_url_odeta_u_nas.index(mass_link_find[0])
        b = mass_temp_price_odeta_u_nas[mass_temp_url_odeta_u_nas.index(mass_link_find[0])]
        e = mass_temp_url_odeta_u_nas[mass_temp_url_odeta_u_nas.index(mass_link_find[0])]
        print(a,b,e)

        c = mass_temp_url_belbazar.index(mass_link_find[0])
        d = mass_temp_price_belbazar[mass_temp_url_belbazar.index(mass_link_find[0])]
        e = mass_temp_url_belbazar[mass_temp_url_belbazar.index(mass_link_find[0])]

        mass_update = []
        if d != b:
            mass_update.append([e, d])

        print(mass_update, len(mass_update))    

        
        print(c,d,e)
        input()      
        
        

        return mass_link_update

    def delete_excess_models(self, full_link_belbazar: list(), mass_link_odeta_u_nas: list()):  
        set_link_belbazar = frozenset(full_link_belbazar)  
        mass_link_delete = [link for link in set_link_belbazar if link not in mass_link_odeta_u_nas]
        print(mass_link_delete)
        return mass_link_delete
        
    def insert_models(self, full_link_belbazar: list(), mass_link_odeta_u_nas: list()):
        set_link_odeta_u_nas = frozenset(mass_link_odeta_u_nas)
        mass_link_insert = [link for link in set_link_odeta_u_nas if link not in full_link_belbazar]
        print(len(mass_link_insert))
        

