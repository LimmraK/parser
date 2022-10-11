from lxml import html
from datetime import timedelta

from db_kit import *
from requests import Session

import random
import pymysql
import codecs
import re
import lxml
import time
import copy
import requests
import json
import datetime
import time
import urllib.request
import ftplib

class test_parser():

    ' code rewiew scan.py, parser belbazar24 for odetaunas.ru ' 
         
    def __init__(self):
        with open('config.json') as f:
            self.templates = json.load(f)
        self.database = db_kit(self.templates["data_connect_to_database"]["host"], self.templates["data_connect_to_database"]["login"],
                               self.templates["data_connect_to_database"]["password"],
                               self.templates["data_connect_to_database"]["name_database"],
                               self.templates["data_connect_to_database"]["charset"])

    def getter_url_photo(self, number_page, counter_default):
        http = Session()
        mass_data = []
        if counter_default % 2 == 0:
            result = http.post(self.templates["url"]["url_women_new"], data = self.templates["blank_for_dollars"],
                            headers = self.templates["headers"], proxies = self.templates["proxies"], timeout = 60)
            page_info = http.get(self.templates["url"]["url_women_new"] + "?page=" + str(number_page))
            tree = html.fromstring(page_info.content, parser = lxml.html.HTMLParser(encoding='utf-8'))
            box_dress = tree.xpath(self.templates["xpath"]["box_dress_xpath"])    
        else:
            result = http.post(self.templates["url"]["url_men_new"], data = self.templates["blank_for_dollars"],
                            headers = self.templates["headers"], proxies = self.templates["proxies"], timeout = 60)
            page_info = http.get(self.templates["url"]["url_men_new"] + "?page=" + str(number_page))
            tree = html.fromstring(page_info.content, parser = lxml.html.HTMLParser(encoding='utf-8'))
            box_dress = tree.xpath(self.templates["xpath"]["box_dress_xpath"])    
        for bypassing in box_dress:
            link = bypassing.xpath(self.templates["xpath"]["link_dress_xpath"])
            mass_data.append(link[0])         
        return mass_data, http


    def selector_models(self, url_belazar_search):
        duplicate = (self.database.sql_zapros("SELECT id FROM " + self.templates["database_table_name"]["osd_tovar"] 
                                              + " WHERE belbazar_url = " + "'" + url_belazar_search + "'"))

        if len(duplicate) == 0:
             return True
        else:
            return duplicate     

    def update_cost_old_models(self, product_property, cost_dollars_on_belbazar_old, url_belazar_search, id_max):
        self.database.sql_zapros('UPDATE ' + self.templates["database_table_name"]["osd_tovar"] + ' SET sebes_vb =' + str(product_property[10]) +
                                 ' WHERE belbazar_url = ' + "'" + url_belazar_search + "'")
        self.generation_the_final_price(cost_dollars_on_belbazar_old, id_max[0][0])


    def selector_manufacturer(self, product_property, entry_create): 
        id_manufacturer = (self.database.sql_zapros("SELECT id FROM " + self.templates["database_table_name"]["osd_proizv"] +
                                                    " WHERE name = " + "'" + product_property + "'"))
        if len(id_manufacturer) == 0:
            id_new_manufacturer = self.database.sql_zapros("SELECT id FROM" + self.templates["database_table_name"]["osd_proizv"] + 
                                                           "ORDER BY id DESC LIMIT 1")

            update_manufacturer = self.database.sql_zapros("INSERT IGNORE INTO" + self.templates["database_table_name"]["osd_proizv"] + 
                                                          ("id, name, namei, status, por, kart, opisanie," + 
                                                           "kol_t, data_add, data_modifi, fon) VALUES + (" + 
                                                           str(id_new_manufacturer[0][0] + 1) + ",'" + 
                                                           product_property + "','" + product_property + 
                                                           "',1," + str(id_new_manufacturer[0][0] + 1) + ",'','',0,'" + 
                                                           str(entry_create) + "','" + str(entry_create) + "','')"))
            return id_new_manufacturer[0][0]
        return id_manufacturer[0][0] 

    def selector_product_type(self, product_property, entry_create):
        id_product_type = (self.database.sql_zapros("SELECT id FROM " + self.templates["database_table_name"]["osd_tov_vid"] +
                                                    " WHERE naim = " + "'" + product_property + "'"))

        if len(id_product_type) == 0:
            id_new_product_type = self.database.sql_zapros("SELECT id FROM SELECT id FROM" + self.templates["database_table_name"]["osd_tov_vid"] + 
                                                           "ORDER BY id DESC LIMIT 1")

            update_product_type = self.database.sql_zapros("INSERT IGNORE INTO " + self.templates["database_table_name"]["osd_tov_vid"] +
                                                          "(id, id_tip, id_kat, naim, status, fon, kart, opisanie," + 
                                                           "kol_t, data_add, data_modifi, heshteg) VALUES (" + 
                                                           str(id_new_product_type[0][0] + 1) + ",1,1,'" + product_property + 
                                                           "',1, '', '" + product_property + "','', 0,'" + str(entry_create) +
                                                            "','" + str(entry_create) + "','');")                                                           
            return id_new_product_type[0][0] 
        return id_product_type[0][0]

    def verification_database(self, url_belazar_search, product_property):   
        nal = "2"
        foto_transfer = ''
        path_transfer = ''
        link = ''   
        entry_create = datetime.datetime.now().strftime("%Y-%m-%d %H:") + str(random.randint(10,59)) + ":" + str(random.randint(10,59))
        id_product_type = self.selector_product_type(product_property[3], entry_create)
        id_manufacturer = self.selector_manufacturer(product_property[0], entry_create)
        id_max = self.database.sql_zapros("SELECT id FROM " + self.templates["database_table_name"]["osd_tovar"] + " ORDER BY id DESC LIMIT 1")
        id_max = id_max[0][0] + 1

        if product_property[9] == "0.00":
            nal = "1"
        if product_property[9] == product_property[10]:
            product_property[10] = "0.00"
        if str(id_max) == '':
            path_transfer = '1000/'
        else :
            path_transfer = str(int(str(id_max)[:-3]) + 1) + "000/"

        path_foto = "foto/" + path_transfer

        for _ in range(len(product_property)-11):
            foto_transfer = foto_transfer + path_foto + str(id_max) + "_" + str(_) + product_property[_ + 11][-4:].lower() + ';' 

        for _ in range(11, len(product_property)):
            link = link + str(product_property[_]) + ";"

        photo_download = self.downloader_photo(product_property, id_max, path_transfer )

        # product_property[0][0] брэнд
        # product_property[0][1] артикуль
        # product_property[0][2] описание
        # product_property[0][3] тип одежды
        # product_property[0][4] состав
        # product_property[0][5] размер
        # product_property[0][6] рост
        # product_property[0][7] артикуль сезона
        # product_property[0][8] цвет
        # product_property[0][9] цена оптовая
        # product_property[0][10] цена розничаня
        # product_property[0][11-13] линки на фотографии

        data_for_write = ("(1, 1," + str(id_product_type) + ",1," + str(id_manufacturer) + "," + str(id_max) + ",'" 
                            + product_property[1] + "','','" + str(entry_create) + "','" + str(entry_create) + "'," 
                            + str(nal) + ",0," + str(product_property[9]) + ",'" + str(product_property[5]) + "','" 
                            + str(product_property[5]) + "','" + str(product_property[8]) + "','" + str(product_property[6]) 
                            + "','" + str(product_property[4]) + "','" + product_property[2] + "','" + product_property[7] 
                            + "',0,'" + foto_transfer + "',1,1,0,0,0,0,0,1," + str(product_property[10]) + ",0,'" + 
                           "''" + "','" + url_belazar_search + "')")

        update_db = self.database.sql_zapros("INSERT IGNORE INTO " + self.templates["database_table_name"]["osd_tovar"] +
                                             "(id_tip, id_kat, id_vid, id_mat, id_proizv," +
                                             "id, model, naim, data_add, data_modifi, nal, cena_vr, sebes_vb, razm_ryd," + 
                                             "razm_vnal, cvet, rost, tkan, opisanie, sezon, prodano, kart, avto, status," +
                                             "rasprodaja, cena_vb, cenas_vr, cenas_vb, sebes_vr, nal2, sebess_vb, sebess_vr, link, belbazar_url)" +
                                             "VALUES " + data_for_write)
    
        return id_max, product_property[0], product_property[3]
   

    # закачка фотографий
    def downloader_photo(self, product_property, id_max, path_transfer):
        for _ in range(12, len(product_property)):     
            counter = _ - 12  
            photo_url = str('http://belbazar24.by' + product_property[_])
            photo_byte = urllib.request.urlopen(photo_url)
            photo_ready_donwload = photo_byte.read()
            update_photo = self.update_to_ftp(photo_ready_donwload, product_property[_], path_transfer, id_max, counter)

    # перекачка фотографий по ftp
    def update_to_ftp(self, photo_ready_donwload, product_property, path_transfer, id_max, counter):
        ftp_connect = ftplib.FTP(self.templates["data_connect_to_ftp"]["host"], self.templates["data_connect_to_ftp"]["username"],
                                 self.templates["data_connect_to_ftp"]["password"], timeout = 20)
        ftp_connect.getwelcome() 
        temp_path_photo =(self.templates["paths"]["path_to_ftp"])
        path_photo = temp_path_photo + path_transfer + "temp/"
        try:
            ftp_connect.mkd(path_photo)
            print("каталон созадн")
        except: 
            pass
        file_photo = open("temp.jpg", "rb")   
        try:      
            update_foto_base = ftp_connect.storbinary('STOR ' + path_photo + str(id_max) + 
                                                      "_" + str(counter) + product_property[-4:].lower() , file_photo)   
        except:
            pass                                  
    
    # выставление правильных цен
    def generation_the_final_price(self, cost_dollars_on_belbazar_old, id_max):
            markup = float(self.database.sql_zapros("SELECT SUM(summa) FROM osd_nacenki WHERE on_off=1 ORDER BY `por` ASC")[0][0])
            id_max = id_max
            cost_dollars_on_belbazar = float(cost_dollars_on_belbazar_old) * 1.02
            delivery_to_the_transport_company = cost_dollars_on_belbazar * 3
            delivery_to_the_our_city = (cost_dollars_on_belbazar * 12) / 4
            total_price = delivery_to_the_transport_company + delivery_to_the_our_city

            self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tovar"] +
                                     " SET sebes_vr = ROUND(sebes_vb*" + str(cost_dollars_on_belbazar) + "+" + 
                                     str(total_price) +") WHERE rasprodaja = 0 AND nal > 1 AND sebes_vb > 0 AND id = " + str(id_max))

            self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tovar"] + 
                                    " SET sebess_vr = ROUND(sebess_vb*" + str(cost_dollars_on_belbazar) + "+"
                                    + str(total_price) + ") WHERE rasprodaja = 0 AND nal > 1 AND sebess_vb > 0 AND id = " + str(id_max))

            self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tovar"] + 
                                    " SET cena_vr = ROUND(sebes_vb*"+ str(cost_dollars_on_belbazar) + "+" +
                                     str(total_price) + "+" + str(markup) +"), cena_vb = ROUND((sebes_vb*"+ str(cost_dollars_on_belbazar) + 
                                     "+" + str(total_price) + "+" + str(markup) + ")/" + str(cost_dollars_on_belbazar_old) + 
                                     ") WHERE rasprodaja = 0 AND nal > 1 AND sebes_vb > 0 AND id = " + str(id_max)) 

            self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tovar"] + 
                                     " SET cenas_vr = ROUND(sebess_vb*" + str(cost_dollars_on_belbazar) + 
                                    "+" + str(total_price) + "+" + str(markup) + "), cenas_vb = ROUND((sebess_vb*" + str(cost_dollars_on_belbazar) + 
                                     "+" + str(total_price) + "+" + str(markup) + ")/" + str(cost_dollars_on_belbazar_old) + 
                                     ") WHERE rasprodaja = 0 AND nal > 1 AND sebess_vb > 0 AND id = " + str(id_max))

    def getter_tree_html(self, url_product, http): 
        product_info = http.get(self.templates["url"]["url_belbazar_product"] + url_product)
        tree = html.fromstring(product_info.content, parser = lxml.html.HTMLParser(encoding = 'utf-8'))
        result = self.list_property_product(tree)
        return result

    def list_property_product(self, tree):
        product_property = []  
        try:
            description = ''
            type_product = ''
            cloth = ''
            growth = ''
            color = ''
            sezon = ''
            counter = 0
            # Получение брэнда
            brand = tree.xpath(self.templates["xpath"]["choise_brand_xpath"])
            if brand[0] == 'РАСПРОДАЖА':
                brand[0] = '*РАСПРОДАЖА*'
            product_property.append(brand[0])
            # Получение артикля
            article = tree.xpath(self.templates["xpath"]["article_xpath"])
            product_property.append(article[0])
            # Получение описания 
            description_temp = tree.xpath(self.templates["xpath"]["description_xpath"])
            # Модерация описания
            for _ in description_temp:
                description = description + _
            description = re.sub(r'[\'\"]','*', description)
            description = re.sub('<strong>','', description)
            description = re.sub('</strong>','', description)
            description = re.sub('&nbsp;','', description)
            description = re.sub('&laquo;','', description)
            description = re.sub('&raquo;','', description)
            description = re.sub('&frac34;','', description)
            description = re.sub('&frac34;','', description)
            description = re.sub(r'[\n\t\r]','', description)
            description = re.sub(r'[\t]', '', description)
            description = re.sub(r'[\*]', '', description)
            description_list = description.split('  ')
            description = ''
            for _ in description_list:
                description = description + _
            description = re.sub('\xa0', ' ', description)
            product_property.append(description)
            # Получение информации о продукте
            info_product = tree.xpath(self.templates["xpath"]["type_product_xpath"])
            while counter < len(info_product):
                if info_product[counter].find(u'Тип одежды:') != -1:
                    type_product = info_product[counter + 1].strip()
                    counter += 1
                if info_product[counter].find(u'Состав:') != -1:
                    cloth = info_product[counter + 1].strip()
                    counter += 1
                if info_product[counter].find(u'Рост:') != -1:
                    growth = info_product[counter + 1].strip()
                    growth = re.sub(r'[\n\t\r]', '', growth)
                    counter += 1
                if info_product[counter].find(u'Цвет:') != -1:
                    color = info_product[counter + 1].strip()
                    color = re.sub(r'[\n\t\r]', '', color)
                    color = re.sub(' ','', color)
                    counter += 1
                counter += 1
            temp_color = color.split(',')
            if len(temp_color) > 1:
                color = ''
                for _ in range(len(temp_color)-1, -1, -1):
                    color = color + temp_color[_] + ','
                color = color[:-1]
            product_property.append(type_product)
            product_property.append(cloth)
            # Получение размерного ряда
            size_volue = tree.xpath(self.templates["xpath"]["size_row_xpath"])
            size = ''
            for _ in size_volue:
                size = size + _ + ','
            size = size[:-1]
            product_property.append(size)
            product_property.append(growth)
            product_property.append(sezon)
            product_property.append(color)
            # Цена со скидкой
            wholesale_price_with_discount = tree.xpath(self.templates["xpath"]["wholesale_price_with_discount_xpath"])
            if len(wholesale_price_with_discount) > 0:
                price = wholesale_price_with_discount[0]
            else:
                price = '0.00'   
            # Цена без скидки    
            product_property.append(price)
            wholesale_price = tree.xpath(self.templates["xpath"]["wholesale_price_xpath"])
            if len(wholesale_price) > 0:
                prices = wholesale_price[0]
            else:
                prices = price   
            product_property.append(prices)
            # получения линков для фото
            url_photos_in_the_catalog = tree.xpath(self.templates["xpath"]["url_photos_in_the_catalog_xpath"])
            counter = 0
            for _ in url_photos_in_the_catalog:
                counter += 1
                link = _
                product_property.append(link)
                if counter == 4:
                    break    
            return product_property
        except: 
            return product_property    


        
    def update_current_parameters(self, id_max):
        mass_price_end_product = self.database.sql_zapros("SELECT id_vid, id_proizv, cena_vr,\
                                                           cena_vb FROM " + self.templates["database_table_name"]["osd_tovar"] + " WHERE id = " + str(id_max))   
        try:    
            id_type_dress = int(mass_price_end_product[0][0])         # id вида одежды
            id_manufacturer = int(mass_price_end_product[0][1])       # id производителья
            price_end_product_rub = int(mass_price_end_product[0][2]) # цена в рублях последнего товара
            price_end_product_usd = int(mass_price_end_product[0][3]) # цена в баксах последнего товара
        except:
            print(mass_price_end_product)
            input("SELECT id_vid, id_proizv, cena_vr,\
                   cena_vb FROM " + self.templates["database_table_name"]["osd_tovar"] + " WHERE id = " + str(id_max))  

        
        # Получение типа одежды и бренда
        type_dress = self.database.sql_zapros("SELECT naim FROM " + self.templates["database_table_name"]["osd_tov_vid"] + " WHERE id =" + str(id_type_dress))
        brand = self.database.sql_zapros("SELECT name FROM " + self.templates["database_table_name"]["osd_proizv"] + " WHERE id =" + str(id_manufacturer))

        mass_price_const = self.database.sql_zapros("SELECT min_cena_vr, min_cena_vb, max_cena_vr, \
                                                     max_cena_vb From " + self.templates["database_table_name"]["osd_constants"])
        min_price_rub = int(mass_price_const[0][0]) # минимальная цена в рублях 
        min_price_usd = int(mass_price_const[0][1]) # минимальная цена в доллорах   
        max_price_rub = int(mass_price_const[0][2]) # максимальная цена в рублях
        max_price_usd = int(mass_price_const[0][3]) # максимальная цена в доллорах

        # Дата определения новинок
        mass_date = self.database.sql_zapros("SELECT DATE(data_modifi) DateOnly FROM " + self.templates["database_table_name"]["osd_tovar"] +
                                             " WHERE nal > 1 GROUP BY DateOnly ORDER BY DateOnly DESC LIMIT 3")
        data_start = str(mass_date[0][0]) + ' 23:59:59'
        data_end = str(mass_date[1][0]) + ' 00:00:00'

        # корректировка значений количества моделей и количества моделей производителя
        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tov_tip"] + " SET kol_t = kol_t + 1")
        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tov_kat"] + " SET kol_t = kol_t + 1")                             
        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tov_mat"] + " SET kol_t = kol_t + 1")
        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_proizv"] + " SET kol_t = kol_t + 1 \
                                  WHERE name = " + '"' + str(brand) + '"')
        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tov_vid"] + " SET kol_t = kol_t + 1 \
                                  WHERE naim = " + '"' + str(type_dress) + '"')                                 
    
        # сравнение максимальной и минимальной цены
        if min_price_rub > price_end_product_rub:
            min_price_rub = price_end_product_rub
        if max_price_rub < price_end_product_rub:
            max_price_rub = price_end_product_rub
        if min_price_usd > price_end_product_usd:
            min_price_usd = price_end_product_usd
        if max_price_usd < price_end_product_usd:
            max_price_usd = price_end_product_usd          

        # апдейт минимальной и максимальной цены в времени новинок
        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_constants"] + " SET min_cena_vr = " + str(min_price_rub) + ", \
                                  min_cena_vb = " +  str(min_price_usd) + ", max_cena_vr = " +  str(max_price_rub) + ", \
                                  max_cena_vb = " +  str(max_price_usd)  + ", data_n = '" + str(data_start) + "', \
                                  data_k = '" + str(data_end) + "'")
      
