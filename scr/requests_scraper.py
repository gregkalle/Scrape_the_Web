from datetime import datetime
import numpy as np
import requests
from bs4 import BeautifulSoup, element
from functions import get_float, get_point_deci, get_start_end_time
from scraper import Scraper

class RequestsScraper(Scraper):
    """A concrete implementation of the Scraper abstract base class using Requests and BeautifulSoup for web scraping.

    Args:
        name (str): The name of the scraped webpage.
        url (str): The URL to scrape data from.
        table_class_name (str): The class name of the table to scrape.
        is_german (bool): Whether the data is in German format (affects number parsing).
        num_string_cols (int): The number of string columns in the table.
        num_float_cols (int): The number of float columns in the table.
        encoding (str, optional): The encoding of the data. Defaults to None.

    Attributes:
        name (str): The name of the scraped webpage.
        scraping_time (datetime.datetime): The time when the data was scraped.
        column_names (np.array): The column names of the data as a numpy array.
        data_array (np.array): The data collected from the webpage as a numpy array.
    """

    def __init__(self,name:str, url:str, table_class_name:str, is_german:bool, num_string_cols:int, num_float_cols:int, encoding:str = None):
        self.__name:str = name
        start, end = get_start_end_time()
        url.replace("START",str(start)).replace("END",str(end))
        if encoding is None:
            encoding = "UTF-8"
        table = RequestsScraper.get_table(url=url,table_name=table_class_name)
        self.__scraping_time:datetime = datetime.now()
        self.__column_names:np.array = RequestsScraper.get_column_names(table=table,encoding=encoding)
        self.__data_array:np.array = RequestsScraper.get_table_data(table=table,
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
        """Returns the table with the specified class name from the webpage with the given URL.

        Args:
            url (str): the URL of the webpage
            table_name (str): The class name of the table.

        Raises:
            requests.Timeout: Requests timeout.
            requests.HTTPError: Code: {page.status_code}
            requests.RequestException: Request Exception

        Returns:
            element.Tag: The table element from the webpage.
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
        """Retrieves the column names from the table.

        Args:
            table (element.Tag): The table element.
            encoding (str): The encoding of the data.

        Returns:
            np.array: The column names.
        """
        head = table.find("thead")
        column_names = [str(name.getText(strip=True)).encode(encoding=encoding) for name in head.find_all("th")]
        
        return np.array(column_names, dtype="S20")


    @staticmethod
    def get_table_data(table:element.Tag, num_string_cols:int, num_float_cols:int, is_german:bool, encoding:str)->np.array:
        """Retrieves the data from the table.

        Args:
            table (element.Tag): The table element.
            num_string_cols (int): The number of string columns in the table.
            num_float_cols (int): The number of float columns in the table.
            is_german (bool): Whether the data is in German format.
            encoding (str): The encoding of the data.

        Returns:
            np.array: The table data.
        """

        data=[]
        for row in table.find("tbody").find_all("tr"):
            string_data = []
            float_data = []
            for i,cell in enumerate(row.find_all("td")):
                text = list(cell.stripped_strings)[0] if cell.getText(strip=True) else ""
                if i<num_string_cols:
                    string_data.append(text.encode(encoding=encoding))
                elif i>= num_string_cols:
                    text = get_point_deci(text=text,change_comma=(is_german=="TRUE"))
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
