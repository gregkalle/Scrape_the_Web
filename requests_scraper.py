from datetime import datetime
import numpy as np
import requests
from bs4 import BeautifulSoup, element
from functions import get_float, get_point_deci, get_start_end_time
from scraper import Scraper

class RequestsScraper(Scraper):
    """_summary_

    Args:
            name (str): _description_
            url (str): _description_
            table_class_name (str): _description_
            is_german (bool): _description_
            num_string_cols (int): _description_
            num_float_cols (int): _description_
    Properties:
            name(str): name of the scraper
            scraping_time(datetime.datetime): time the webpage was scraped
            column_names(np.array): column name data
            data_array(np.array): table data
    """

    def __init__(self,name:str, url:str, table_class_name:str, is_german:bool, num_string_cols:int, num_float_cols:int, encoding:str = None):
        self.__name = name
        start, end = get_start_end_time()
        url.replace("START",str(start)).replace("END",str(end))
        if encoding is None:
            encoding = "UTF-8"
        table = RequestsScraper.get_table(url=url,table_name=table_class_name)
        self.__scraping_time = datetime.now()
        self.__column_names = RequestsScraper.get_column_names(table=table,encoding=encoding)
        self.__data_array = RequestsScraper.get_table_data(table=table,
                                                         num_string_cols=num_string_cols,
                                                         num_float_cols=num_float_cols,
                                                         is_german=is_german,
                                                         encoding=encoding
                                                         )

    @property
    def name(self)->str:
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
    def get_table(url:str, table_name:str)->element.Tag:
        """Returns the table with table name of the webpage with given url.

        Args:
            url (str): the url of the webpage
            table_name (str): Class name of the table

        Raises:
            requests.Timeout: Requests timeout.
            requests.HTTPError: Code: {page.status_code}
            requests.RequestException: Request Exception

        Returns:
            element.Tag: the table of the website which want to be scraped
        """
        try:
            page = requests.get(url=url,timeout=10)
            page.raise_for_status()
        except requests.Timeout as exc:
            raise requests.Timeout("Requests timeout.") from exc
        except requests.HTTPError as exc:
            raise requests.HTTPError(f"Code: {page.status_code}") from exc
        except requests.RequestException as exc:
            raise requests.RequestException("Request Exception") from exc

        soup = BeautifulSoup(page.content,features="lxml")
        return soup.find(class_=table_name)

    @staticmethod
    def get_column_names(table:element.Tag, encoding:str)->np.array:
        """_summary_

        Args:
            table (element.Tag): _description_

        Returns:
            np.array: column names
        """
        head = table.find("thead")
        column_names = [str(name.getText(strip=True)).encode(encoding=encoding) for name in head.find_all("th")]
        
        return np.array(column_names, dtype="S20")


    @staticmethod
    def get_table_data(table:element.Tag, num_string_cols:int, num_float_cols:int, is_german:bool, encoding:str)->np.array:
        """_summary_

        Args:
            table (element.Tag): _description_
            num_string_cols (int): _description_
            num_float_cols (int): _description_
            is_german (bool): _description_

        Returns:
            np.array: table data
        """

        data=[]
        for row in table.find("tbody").find_all("tr"):
            string_data = []
            float_data = []
            for i,element in enumerate(row.find_all("td")):
                text = list(element.stripped_strings)[0] if element.getText(strip=True) else ""
                if i<num_string_cols:
                    string_data.append(text.encode(encoding=encoding))
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

        data_type = np.dtype([("","S20",(num_string_cols,)),("","f4",(num_float_cols,))])
        return np.array(data, dtype=data_type)
