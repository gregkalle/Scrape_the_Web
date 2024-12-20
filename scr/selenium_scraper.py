from datetime import datetime
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
import numpy as np
from functions import get_float, get_point_deci, get_start_end_time
from scraper import Scraper

class SeleniumScraper(Scraper):
    """A concrete implementation of the Scraper abstract base class using Selenium for web scraping.

    Args:
        name (str): The name of the webpage to scrape data from.
        url (str): The URL to scrape data from.
        table_class_name (str): The class name of the table to scrape.
        is_german (bool): Whether the data is in German format (affects number parsing).
        cockie_handler (str, optional): The handler for cookie acceptance. Defaults to None.
        change_page_handler (str, optional): The handler for changing pages. Defaults to None.
        encoding (str, optional): The encoding of the data. Defaults to None.
    
    Attributes:
        name (str): The name of the scraped webpage.
        scraping_time (datetime.datetime): The time when the data was scraped.
        column_names (np.array): The column names of the data as a numpy array.
        data_array (np.array): The data collected from the webpage as a numpy array.

    """

    def __init__(self,name:str, url:str, table_class_name:str, is_german:bool,
                 cockie_handler:str = None, change_page_handler:str=None, encoding:str = None):
        self.__name:str = name
        start, end = get_start_end_time()
        url = url.replace("START",str(start)).replace("END",str(end))
        driver = self.get_driver(url=url, cockie_handler=cockie_handler)
        self.__scraping_time:datetime = datetime.now()
        if encoding is None:
            encoding = "UTF-8"
        self.__column_names:np.array = SeleniumScraper.get_column_names(driver=driver, table_name=table_class_name,encoding=encoding)
        self.__data_array:np.array = SeleniumScraper.get_table_data(driver=driver, table_name=table_class_name, is_german=is_german,change_page_handler=change_page_handler, encoding=encoding)
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
    def get_driver(url:str, cockie_handler:str)->WebDriver:
        """Initializes and returns a Selenium WebDriver.

        Args:
            url (str): The URL to navigate to.
            cockie_handler (str): The handler for cookie acceptance.

        Returns:
            webdriver: The initialized WebDriver.
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless=new")
        driver =  webdriver.Chrome(options=options)
        driver.get(url=url)
        driver.implicitly_wait(10)
        if cockie_handler:
            SeleniumScraper.cockie_handling(driver=driver,cockie_handler=cockie_handler)
        return driver
    
    @staticmethod
    def cockie_handling(driver:WebDriver, cockie_handler:str)->None:
        """Handles cookie acceptance on the web page.

        Args:
            driver (WebDriver): The WebDriver instance.
            cockie_handler (str): The handler for cookie acceptance.
        """
        cockie_object, cockie_name = cockie_handler.split("|")
        driver.find_element(by=cockie_object,value=cockie_name).click()

    @staticmethod
    def next_page(driver:WebDriver, object_type:str, object_name:str):
        """Navigates to the next page.

        Args:
            driver (WebDriver): The WebDriver instance.
            object_type (str): The type of the object to interact with.
            object_name (str): The name of the object to interact with.
        """
        driver.find_element(by=object_type,value=object_name).click()

    @staticmethod
    def get_table():
        """Placeholder for retrieving the table from the web page.

        Raises:
            NotImplemented: This method is not implemented.
        """
        raise NotImplemented

    @staticmethod
    def get_column_names(driver:WebDriver, table_name:str, encoding:str)->np.array:
        """Retrieves the column names from the table.

        Args:
            driver (WebDriver): The WebDriver instance.
            table_name (str): The class name of the table.
            encoding (str): The encoding of the data.

        Returns:
            np.array: The column names.
        """
        table = driver.find_element(by=By.CLASS_NAME,value=table_name)
        head = table.find_element(by=By.TAG_NAME,value="thead")
        column_names = []

        for name in head.find_elements(by=By.TAG_NAME,value="th"):
            if name.text and not name.get_dom_attribute("colspan") is None:
                column_names.extend([name.text.encode(encoding=encoding)]*int(name.get_dom_attribute("colspan")))
            elif name.text:
                column_names.append(name.text.encode(encoding=encoding))
        return np.array(column_names,dtype="S20")
            

    @staticmethod
    def get_table_data(driver:WebDriver, table_name:str, is_german:bool, change_page_handler:str, encoding:str)->np.array:
        """Retrieves the data from the table.

        Args:
            driver (WebDriver): The WebDriver instance.
            table_name (str): The class name of the table.
            is_german (bool): Whether the data is in German format.
            change_page_handler (str): The handler for changing pages.
            encoding (str): The encoding of the data.

        Returns:
            np.array: The table data.
        """
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
                    data_header = [str(table_header.text).encode(encoding=encoding) for table_header in row.find_elements(by=By.TAG_NAME,value="th")]
                    data_body = []
                    for table_data in row.find_elements(by=By.TAG_NAME,value="td"):
                        if table_data.text:
                            element_data = get_point_deci(table_data.text, change_comma=(is_german=="TRUE"))
                            try:
                                element_data = get_float(element_data)
                            except ValueError:
                                element_data = None
                            data_body.append(element_data)
                    data.append((tuple(data_header),tuple(data_body)))
            if num_pages > num:
                SeleniumScraper.next_page(driver=driver,object_type=next_page_object,object_name=next_page_name)
                
        len_f0 = len(data[0][0])
        len_f1 = len(data[0][1])

        data_type = np.dtype([("f0","S20",(len_f0,)),("f1","f4",(len_f1,))])
        return np.array(data, dtype=data_type)
