from datetime import datetime
import numpy as np
import requests
from bs4 import BeautifulSoup
from functions import get_float, get_point_deci


class RequestsScraper():

    def __init__(self,name:str, url:str, table_class_name:str, is_german:bool, num_string_cols:int, num_float_cols:int):
        self.__name = name
        self.__page = RequestsScraper.get_page(url)
        self.__scraping_time = datetime.now()
        self.__column_names = RequestsScraper.get_column_names(self.__page,table_name=table_class_name)
        self.__data_array = RequestsScraper.get_table_data(self.__page,table_name=table_class_name,
                                                         num_string_cols=num_string_cols,
                                                         num_float_cols=num_float_cols,
                                                         is_german=is_german
                                                         )

    @property
    def name(self):
        return self.__name

    @property
    def column_names(self):
        return self.__column_names

    @property
    def data_array(self):
        return self.__data_array

    @property
    def scraping_time(self):
        return self.__scraping_time

    @staticmethod
    def get_page(url:str)->BeautifulSoup:
        page = requests.get(url=url,timeout=10)

        if not page.status_code == 200:
            print(page.status_code)
            raise requests.ConnectionError("Connection faild.")

        return BeautifulSoup(page.content,features="lxml")

    @staticmethod
    def get_column_names(page:BeautifulSoup, table_name:str)->np.array:
        table = page.find(class_=table_name)
        head = table.find("thead")
        column_names = [name.getText(strip=True) for name in head.find_all("th")]
        return np.array(column_names, dtype="U20")

    @staticmethod
    def get_table_data(page:BeautifulSoup, table_name:str, num_string_cols:int, num_float_cols:int, is_german:bool)->np.array:
        table = page.find(class_=table_name)
        
        data=[]
        for row in table.find("tbody").find_all("tr"):
            string_data = []
            float_data = []
            for i,element in enumerate(row.find_all("td")):
                text = list(element.stripped_strings)[0] if element.getText(strip=True) else ""
                if i<num_string_cols:
                    string_data.append(text)
                elif i>= num_string_cols:
                    text = get_point_deci(text=text,change_comma=is_german)
                    try:
                        text = get_float(text=text)
                        float_data.append(text)
                    except ValueError:
                        float_data.append(None)
                if i>=num_float_cols+num_string_cols-1:
                    break
            data.append((tuple(string_data),tuple(float_data)))

        data_type = np.dtype([("","U20",(num_string_cols,)),("","f4",(num_float_cols,))])
        return np.array(data, dtype=data_type)
