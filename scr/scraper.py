from datetime import datetime
from abc import ABC
from abc import abstractmethod
import numpy as np

class Scraper(ABC):

    """
    Abstract base class for a web scraper.
    """

    @property
    @abstractmethod
    def name(self)->str:
        """Returns the name of the scraped webpage.

        Returns:
            str: name of the scraped webpage.
        """
        pass

    @property
    @abstractmethod
    def column_names(self)->np.array:
        """Returns the column names of the data as a numpy array.

        Returns:
            np.array: column names of the data
        """
        pass

    @property
    @abstractmethod
    def data_array(self)->np.array:
        """Returns the data collected from the webpage as a numpy array.

        Returns:
            np.array: data collected from the webpage
        """
        pass

    @property
    @abstractmethod
    def scraping_time(self)->datetime:
        """Returns the time when the data was scraped.

        Returns:
            datetime: time when the data was scraped
        """
        pass

    @staticmethod
    @abstractmethod
    def get_table()->any:
        """Returns the table from the web page.

        Returns:
            any: the table in which the data is stored
        """
        pass

    @staticmethod
    @abstractmethod
    def get_column_names()->np.array:
        """Returns the column names of the data.

        Returns:
            np.array: the column names of the data
        """
        pass

    @staticmethod
    @abstractmethod
    def get_table_data()->np.array:
        """Returns the data from the table.

        Returns:
            np.array: the data from the table
        """
        pass
