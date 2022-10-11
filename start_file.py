import datetime
import time

# импорт собственных модулей
import Parser_test
import generation_price_dollar_by_belbazar as dollar
import dollar_comparator
import scaner_link

class starter():

    def __init__(self):
        with open("data_update", "r") as f:
            self.data_for_update = f.read()    
        

    def __call__(self):

        # иницилизация списков для линков
        mass_data = [] 
        mass_data_temp = []
        mass_link_men_belbazar = [] 
        mass_link_women_belbazar = []
        mass_link_odeta_u_nas = []
        full_link_belbazar = []
        mass_link_update = []

        # время для сканера
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:")
        delta = datetime.timedelta(days = 1)    

        # иницилизация объектов
        parser = Parser_test.test_parser() 
        dollars = dollar.generation_price_dollar_by_belbazar()
        scaners = scaner_link.scaner()
        dollar_comparators = dollar_comparator.dollar_comprator()

        while True:

            # иницилизация счётчиков для логов
            counter = 0
            counter_default = 0

            # подготовка массива линков
            mass_data_temp_one, http = parser.getter_url_photo(1, counter_default + 1)
            mass_data = mass_data + mass_data_temp_one
            verify_mass_data = list(set(mass_data) - set(mass_data_temp)) # список с юрлами моделей    

            # подсчёт доллара
            dollars.generation_cost_dollar()
            dollar_old_on_odeta_u_nas = dollar_comparators.dollar_search(dollars.cost_dollars_on_belbazar_old)
            dollar_comparators.dollar_comparator(dollars.cost_dollars_on_belbazar_old, dollar_old_on_odeta_u_nas)

            #if str(self.data_for_update) <= str(now):

            # поготовка линков для большого обновления

            # получение страниц 
            page_men = scaners.get_page_men()
            page_women = scaners.get_page_women()

            # массивы по женским и мужским товарам на belbazar
            mass_link_men_belbazar = scaners.getter_link_men_belbazar(page_men)
            mass_link_women_belbazar = scaners.getter_link_women_belbazar(page_women)
            full_link_belbazar = scaners.generator_full_link_belbazar(mass_link_men_belbazar, mass_link_women_belbazar)

            # массив из нашей базы
            mass_link_odeta_u_nas = scaners.getter_link_odeta_u_nas()

            #массив для обновления
            scaners.update_all_models(full_link_belbazar, mass_link_odeta_u_nas)
    
            # массив для удаления
            mass_link_delete = scaners.delete_excess_models(full_link_belbazar, mass_link_odeta_u_nas)

            # массив для инсерта
            mass_link_insert = scaners.insert_models(full_link_belbazar, mass_link_odeta_u_nas)

            # для сложения времени произвёл срез из переменной даты и перевёл в инт
            #self.data_for_update = datetime.datetime(int(self.data_for_update[6:10]), int(self.data_for_update[0:2]),
            #                                    int(self.data_for_update[3:5]), int(self.data_for_update[11:13]))
            #self.data_for_update = self.data_for_update + delta         

            # запись времени следующего обновления
            #with open("data_update", "w") as f: 
            #    f.write(str(self.data_for_update))
            input()
            
                                

            for i in verify_mass_data:   
                counter_default += 1
                
                # получение html дерева для линков
                result = parser.getter_tree_html(i, http) 
                if len(result) < 11:
                    continue

                # функция определяет есть ли модель в базе
                response = parser.selector_models(i) 
                if response == True:
                    # инсерт
                    counter += 1
                    id_max, brand, type_dress = parser.verification_database(i, result) # 
                    parser.generation_the_final_price(dollars.cost_dollars_on_belbazar_old, id_max)   
                    parser.update_current_parameters(id_max)
                else:
                    # апдейт
                    parser.update_cost_old_models(result, dollars.cost_dollars_on_belbazar_old, i, response)

                print('апдейты ' + str(counter), 'всего ' + str(counter_default))

            # Запись в лог
            file_name = str(datetime.datetime.now().strftime("%Y_%m_%d")) + " - log"
            with open(file_name, "a" , encoding='utf-8') as f:
                log = 'апдейты ' + str(counter) + ' всего ' + str(counter_default) + '\n'
                f.write(log)


if __name__ == '__main__':
    starter = starter()
    starter()

