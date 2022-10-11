from db_kit import *

import json

class dollar_comprator():

    def __init__(self):
        with open('config.json') as f:
            self.templates = json.load(f)
        self.database = db_kit(self.templates["data_connect_to_database"]["host"], 
                               self.templates["data_connect_to_database"]["login"],
                               self.templates["data_connect_to_database"]["password"],
                               self.templates["data_connect_to_database"]["name_database"],
                               self.templates["data_connect_to_database"]["charset"])
    
    def dollar_search(self, cost_dollars_on_belbazar_old):
        dollar_old_on_odeta_u_nas = self.database.sql_zapros("SELECT kurs_b FROM " + self.templates["database_table_name"]["osd_constants"])[0][0]
        return dollar_old_on_odeta_u_nas
    
    def dollar_comparator(self, cost_dollars_on_belbazar_old,  dollar_old_on_odeta_u_nas):
        if float(cost_dollars_on_belbazar_old) != float(dollar_old_on_odeta_u_nas):
            self.dollar_update(cost_dollars_on_belbazar_old)
        else:
            pass

    def dollar_update(self, cost_dollars_on_belbazar_old):
        self.database.sql_zapros("Update " + self.templates["database_table_name"]["osd_constants"] + 
                                 " SET kurs_b = " + str(cost_dollars_on_belbazar_old))
        markup = float(self.database.sql_zapros("SELECT SUM(summa) FROM osd_nacenki WHERE on_off=1 ORDER BY `por` ASC")[0][0])
        cost_dollars_on_belbazar = float(cost_dollars_on_belbazar_old) * 1.02
        delivery_to_the_transport_company = cost_dollars_on_belbazar * 3
        delivery_to_the_our_city = (cost_dollars_on_belbazar * 12) / 4
        total_price = delivery_to_the_transport_company + delivery_to_the_our_city

        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tovar"] + 
                                 " SET sebes_vr= ROUND(sebes_vb*" + str(cost_dollars_on_belbazar) + "+" + 
                                 str(total_price) +") WHERE rasprodaja = 0 AND nal > 1 AND sebes_vb > 0")

        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tovar"] + 
                                 " SET sebess_vr = ROUND(sebess_vb*" + str(cost_dollars_on_belbazar) + "+"
                                 + str(total_price) + ") WHERE rasprodaja = 0 AND nal > 1 AND sebess_vb > 0")

        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tovar"] + 
                                 " SET cena_vr = ROUND(sebes_vb*"+ str(cost_dollars_on_belbazar) + "+" +
                                 str(total_price) + "+" + str(markup) +"), \
                                 cena_vb = ROUND((sebes_vb*"+ str(cost_dollars_on_belbazar) + 
                                 "+" + str(total_price) + "+" + str(markup) + ")/" + str(cost_dollars_on_belbazar_old) + 
                                 ") WHERE rasprodaja = 0 AND nal > 1 AND sebes_vb > 0") 

        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_tovar"] + 
                                 " SET cenas_vr = ROUND(sebess_vb*" + str(cost_dollars_on_belbazar) + 
                                 "+" + str(total_price) + "+" + str(markup) + "),\
                                 cenas_vb = ROUND((sebess_vb*" + str(cost_dollars_on_belbazar) + 
                                 "+" + str(total_price) + "+" + str(markup) + ")/" + str(cost_dollars_on_belbazar_old) + 
                                 ") WHERE rasprodaja = 0 AND nal > 1 AND sebess_vb > 0")

        result = self.database.sql_zapros("SELECT cena_vr, cena_vb FROM " + self.templates["database_table_name"]["osd_tovar"] +  " WHERE \
                                  cena_vr = (SELECT MIN(cena_vr) AS cena_vr \
                                  FROM " + self.templates["database_table_name"]["osd_tovar"] + " WHERE nal > 1) LIMIT 1")

        min_price_rub = str(result[0][0])
        min_price_usd = str(result[0][1])
        result = self.database.sql_zapros("SELECT cena_vr, cena_vb FROM " + self.templates["database_table_name"]["osd_tovar"] + " WHERE \
                                  cena_vr =(SELECT MAX(cena_vr) AS cena_vr \
                                  FROM " + self.templates["database_table_name"]["osd_tovar"] + " WHERE nal > 1) LIMIT 1")    

        max_price_rub = str(result[0][0])
        max_price_usd = str(result[0][1])

        self.database.sql_zapros("UPDATE " + self.templates["database_table_name"]["osd_constants"] + " SET min_cena_vr = " + str(min_price_rub) + ", \
                                  min_cena_vb = " +  str(min_price_usd) + ", max_cena_vr = " +  str(max_price_rub) + ", \
                                  max_cena_vb = " +  str(max_price_usd))



