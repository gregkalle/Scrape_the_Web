from datetime import date
import csv
import numpy as np
from requests_scraper import RequestsScraper
from selenium_scraper import SeleniumScraper
from data_collector import DataCollector

PARENT_NAME = "webpages to be informed"
DATA_PATH = "webpage_data.csv"
COLUMN_NAMES = ["name","url","method","page_handler","cockie_handler",
                "table_name", "is_german", "num_str_cols","num_float_cols"]

def main():

    wp_data = {}

    with open(DATA_PATH, encoding="utf-8-sig") as wp_data_file:
        reader = csv.reader(wp_data_file, delimiter=";",dialect="excel")

        for i,row in enumerate(reader):
            if not i == 0:
                wp_data[row[0]] = dict(zip(COLUMN_NAMES,row))

    wp_urls = [wp_data[key]["url"] for key in wp_data.keys()] 
    data_collector = DataCollector(parent_name=PARENT_NAME, group_names= dict(zip(wp_data.keys(),wp_urls)))

    date_today = date.today()

    for key in wp_data:
        if not data_collector.is_saved_columns(group_name=key):
            column_data, data = get_data(wp_data[key])
            data_collector.store_column_names(column_names=column_data, group_name=key)
            data_collector.store_data(data=data, group_name=key,data_date=date_today)

        elif not data_collector.is_saved_data(key,data_date=date_today):
            _, data = get_data(wp_data[key])
            data_collector.store_data(data=data, group_name=key,data_date=date_today)
        
        else:
            print(f"{key} is saved in database at {str(date_today)}.")

def get_data(data:dict[str])-> tuple[np.array]:
    if data["method"] == "SELENIUM":
        scraper = SeleniumScraper(name=data["name"],url=data["url"],
                                  table_class_name=data["table_name"],
                                  is_german=data["is_german"],
                                  cockie_handler=data["cockie_handler"],
                                  change_page_handler=data["page_handler"]
                                  )
        return (scraper.column_names, scraper.data_array)

    if data["method"] == "REQUESTS":
        scraper = RequestsScraper(name=data["name"],url=data["url"],
                                  table_class_name=data["table_name"],
                                  is_german=data["is_german"],
                                  num_string_cols=int(data["num_str_cols"]),
                                  num_float_cols=int(data["num_float_cols"])
                                  )
        return (scraper.column_names, scraper.data_array)

    

if __name__ == "__main__":
    main()
