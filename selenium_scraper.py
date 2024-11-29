from datetime import datetime
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
import numpy as np
from functions import get_float, get_point_deci, get_start_end_time
from scraper import Scraper

class SeleniumScraper(Scraper):

    def __init__(self,name:str, url:str, table_class_name:str, is_german:bool,
                 cockie_handler:str = None, change_page_handler:str=None):
        self.__name = name
        start, end = get_start_end_time()
        url = url.replace("START",str(start)).replace("END",str(end))
        driver = self.get_driver(url=url, cockie_handler=cockie_handler)
        self.__scraping_time = datetime.now()
        self.__column_names = SeleniumScraper.get_column_names(driver=driver, table_name=table_class_name)
        self.__data_array = SeleniumScraper.get_table_data(driver=driver, table_name=table_class_name, is_german=is_german,change_page_handler=change_page_handler)
        driver.quit()


    @property
    def name(self):
        return self.__name

    @property
    def column_names(self)->np.array:
        return self.__column_names

    @property
    def data_array(self)->np.array:
        return self.__data_array

    @property
    def scraping_time(self)->datetime:
        return self.__scraping_time
    
    @staticmethod
    def get_driver(url:str, cockie_handler:str)->webdriver:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver =  webdriver.Chrome(options=options)
        driver.get(url=url)
        driver.implicitly_wait(10)
        if cockie_handler:
            SeleniumScraper.cockie_handling(driver=driver,cockie_handler=cockie_handler)
        return driver
    
    @staticmethod
    def cockie_handling(driver:WebDriver, cockie_handler:str)->None:
        cockie_object, cockie_name = cockie_handler.split("|")
        driver.find_element(by=cockie_object,value=cockie_name).click()

    @staticmethod
    def next_page(driver:WebDriver, object_type:str, object_name:str):
        driver.find_element(by=object_type,value=object_name).click()

    @staticmethod
    def get_table():
        raise NotImplemented

    @staticmethod
    def get_column_names(driver:WebDriver, table_name:str)->np.array:
        table = driver.find_element(by=By.CLASS_NAME,value=table_name)
        head = table.find_element(by=By.TAG_NAME,value="thead")
        column_names = []

        for name in head.find_elements(by=By.TAG_NAME,value="th"):
            if name.text and not name.get_dom_attribute("colspan") is None:
                column_names.extend([name.text]*int(name.get_dom_attribute("colspan")))
            elif name.text:
                column_names.append(name.text)
        return column_names

    @staticmethod
    def get_table_data(driver:WebDriver, table_name:str, is_german:bool, change_page_handler:str):
        if change_page_handler:
            num_pages, next_page_object, next_page_name = change_page_handler.split("|")
        else:
            num_pages = 1
        
        num_pages = int(num_pages)

        data = []

        for num in range(1,num_pages+1):
            table = driver.find_element(by=By.CLASS_NAME,value=table_name)
            bodys = table.find_elements(by=By.TAG_NAME,value="tbody")

            for body in bodys:
                rows = body.find_elements(by=By.TAG_NAME,value="tr")

                for row in rows:
                    data_header = [table_header.text for table_header in row.find_elements(by=By.TAG_NAME,value="th")]
                    data_body = []
                    for table_data in row.find_elements(by=By.TAG_NAME,value="td"):
                        if table_data.text:
                            element_data = get_point_deci(table_data.text, change_comma=is_german)
                            try:
                                element_data = get_float(get_point_deci(element_data))
                            except ValueError:
                                element_data = None
                            data_body.append(element_data)
                    data.append((tuple(data_header),tuple(data_body)))
            if num_pages > num:
                SeleniumScraper.next_page(driver=driver,object_type=next_page_object,object_name=next_page_name)
                
        len_f0 = len(data[0][0])
        len_f1 = len(data[0][1])

        data_type = np.dtype([("","U20",(len_f0,)),("","f4",(len_f1,))])
        return np.array(data, dtype=data_type)
