import time
from datetime import date, datetime, timedelta
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd

#power plant types
POWERPLANT_TYPES=[1004066,1001226,1001225,1004067,1004068,1001228,1001223,1004069,1004071,1004070,1001227]
TIME_ITEMS_NUMBER = 2

class SmardDataScraper:

    def __init__(self,resolution = "hour",region ="DE",plant_types = None, day:date=None):
        if plant_types is None:
            plant_types = POWERPLANT_TYPES
        self.__current_page = 1
        self.__item_number = len(plant_types)+TIME_ITEMS_NUMBER
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.__driver = webdriver.Chrome(options=options)

        start,end = self.__get_start_end(day=day)
        self.__url = self.__get_url(start,end,resolution,region,plant_types)
        self.__driver.get(self.__url)
        self.__driver.implicitly_wait(10)
        self.__driver.find_element(by=By.CLASS_NAME,value="js-cookie-decline").click()
        self.__data = self.set_nparray()

    def __get_url(self,start:int,end:int,resolution:str,region:str,plant_types:list[int])->str:
        plant_types = [str(element) for element in plant_types]
        url = "https://www.smard.de/page/home/marktdaten/"\
        f"78?marketDataAttributes=%7B%22resolution%22:%22{resolution}%22"\
        f",%22region%22:%22{region}%22,%22from%22:"\
        f"{start},%22to%22:{end},%22moduleIds"\
        f"%22:%5B{",".join(plant_types)}%5D,%22selectedCategory%22:1,%22activeChart%22"\
        ":false,%22style%22:%22color%22,%22categoriesModuleOrder%22:%7B%7D%7D"
        return url

    def __get_start_end(self, day:date= None)->tuple[int]:
        if day is None:
            day = date.today()
        end = day
        start = end - timedelta(days=1)

        end = time.mktime(end.timetuple())*1000 - 1
        start = time.mktime(start.timetuple())*1000
        return start,end

    def __quit(self):
        self.__driver.quit()

    def __next_page(self):
        self.__current_page +=1
        page_name = f"Seite {self.__current_page}"
        try:
            self.__driver.find_element(By.XPATH,f"//li[@title='{page_name}']").click()
        except (ElementClickInterceptedException, NoSuchElementException) as exc:
            self.__quit()
            raise ElementClickInterceptedException("Element not clickable.") from exc

    def __get_columns(self)->list[str]:
        table = self.__driver.find_element(by=By.CLASS_NAME,value="c-chart-table__container")
        column_names = table.find_elements(by=By.CLASS_NAME,value="c-chart-table__head")
        return np.array([name.text for name in column_names])

    def __get_table_items(self):
        table = self.__driver.find_element(by=By.CLASS_NAME,value="c-chart-table__container")
        elements = table.find_elements(by=By.CLASS_NAME,value="c-chart-table__element")
        for i in range(0,len(elements),self.__item_number):


            res1 = [self.__date_text_to_float(value.text) for value in elements[i:i+TIME_ITEMS_NUMBER]]
            res2 = [float(value.text.replace(".","").replace(",",".")) for value in elements[i+TIME_ITEMS_NUMBER:i+self.__item_number]]
            yield res1+res2

    def __date_text_to_float(self,text:str)->float:
        date_value = datetime(day=int(text[0:2]),month=int(text[3:5]),year=int(text[6:10]),hour=int(text[-5:-3]),minute=int(text[-2:]))
        return float(time.mktime(date_value.timetuple()),)

    @property
    def data(self)->tuple[np.array]:
        return self.__data

    def set_nparray(self)->tuple[np.array]:
        columns = self.__get_columns()
        data_items = []
        try:
            while True:
                data_items.extend(list(self.__get_table_items()))
                self.__next_page()
        except ElementClickInterceptedException:
            return np.array(columns), np.array(data_items,dtype=np.float32)
