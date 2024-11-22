import time
from datetime import date, timedelta
from smard_data_scraper import SmardDataScraper
from data_collector import DataCollector

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
