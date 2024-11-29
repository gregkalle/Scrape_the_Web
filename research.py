import time
from datetime import date, timedelta
from data_collector import DataCollector
"""
from selenium_scraper import SeleniumScraper
from bs4 import BeautifulSoup
import numpy as np

today = date.today()
yesterday = date.today() - timedelta(days=1)
today = time.mktime(today.timetuple())
yesterday = time.mktime(yesterday.timetuple())

collector = DataCollector()

if not collector.is_stored(today):

    coll, data = SmardDataScraper(day=today).data

      
    #collector.store_column_names(coll)

    collector.store_data(data=data,data_date=today)

    print("sucess")

else:
    print("nothing stored")

data = collector.get_data(str(yesterday)+str(today))

print(data)


scraper = SeleniumScraper(name="divi Register", url="https://www.intensivregister.de/#/aktuelle-lage/laendertabelle",
                          table_class_name="laendertabelle", is_german=True)


print(scraper.data_array)
"""

collector = DataCollector()
