from datetime import datetime
from abc import ABC
from abc import abstractmethod
import numpy as np

class Scraper(ABC):

    @property
    @abstractmethod
    def name(self)->str:
        pass

    @property
    @abstractmethod
    def column_names(self)->np.array:
        pass

    @property
    @abstractmethod
    def data_array(self)->np.array:
        pass

    @property
    @abstractmethod
    def scraping_time(self)->datetime:
        pass

    @staticmethod
    @abstractmethod
    def get_table():
        pass

    @staticmethod
    @abstractmethod
    def get_column_names():
        pass

    @staticmethod
    @abstractmethod
    def get_table_data():
        pass
