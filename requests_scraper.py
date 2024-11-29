from datetime import datetime
import numpy as np
import requests
from bs4 import BeautifulSoup, element
from functions import get_float, get_point_deci


class RequestsScraper():
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

    def __init__(self,name:str, url:str, table_class_name:str, is_german:bool, num_string_cols:int, num_float_cols:int):
        self.__name = name
        self.__table = RequestsScraper.get_table(url=url,table_name=table_class_name)
        self.__scraping_time = datetime.now()
        self.__column_names = RequestsScraper.get_column_names(table=self.__table)
        self.__data_array = RequestsScraper.get_table_data(table=self.__table,
                                                         num_string_cols=num_string_cols,
                                                         num_float_cols=num_float_cols,
                                                         is_german=is_german
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
    def get_column_names(table:element.Tag)->np.array:
        """_summary_

        Args:
            table (element.Tag): _description_

        Returns:
            np.array: column names
        """
        head = table.find("thead")
        column_names = [name.getText(strip=True) for name in head.find_all("th")]
        return np.array(column_names, dtype="U20")

    @staticmethod
    def get_table_data(table:element.Tag, num_string_cols:int, num_float_cols:int, is_german:bool)->np.array:
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
