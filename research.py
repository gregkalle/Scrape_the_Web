import time
from datetime import date, datetime
import numpy as np
import h5py
from smard_data_scraper import SmardDataScraper
from data_collector import DataCollector

today = time.mktime(date.today().timetuple())

collector = DataCollector()

if not collector.is_stored(today):

    coll, data = SmardDataScraper().data

      
    #collector.store_column_names(coll)

    collector.store_data(data=data)

    print("sucess")

else:
    print("nothing stored")
