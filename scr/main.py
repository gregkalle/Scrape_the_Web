from datetime import date, datetime, timedelta
import time
import csv
import numpy as np
from requests import RequestException
from requests_scraper import RequestsScraper
from selenium_scraper import SeleniumScraper
from data_collector import DataCollector
from functions import user_input

PARENT_NAME = "webpages to be informed"
DATA_PATH = "data/webpage_data.csv"
COLUMN_NAMES = ["name","url","method","page_handler","cockie_handler",
                "table_name", "is_german", "num_str_cols","num_float_cols","encoding"]
LOG_FILE = "doc/scrape.log"

def main():
    """
    Main function to execute the data collection process.
    
    """
    with open(LOG_FILE,"a+") as file:
        file.write(f"EXECUTED at \"{datetime.now().isoformat()}\":\n")
    prozessing_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=11, minutes=38)
    while True:
        if datetime.now() < prozessing_time:
            try:
                user_respond = user_input(prompt="Do you want to exit the script? Y/N", timeout=(prozessing_time-datetime.now()).total_seconds())
            except TimeoutError:
                continue
            if user_respond[0].upper() == "Y":
                with open(LOG_FILE,"a+") as file:
                    file.write(f"TERMINATED at \"{datetime.now().isoformat()}\":\n\n")
                print("Process terminated.")
                break
            print(f"Sleep until {prozessing_time}")
            time.sleep((prozessing_time-datetime.now()).total_seconds())
        prozessing_time = prozessing_time + timedelta(days=1)
        collect()


def collect()->None:
    """
    Collects data from specified web pages and stores it in the data collector.
    """
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
            column_data, data, scraping_time = get_data(wp_data[key])
            data_collector.store_column_names(column_names=column_data, group_name=key)
            data_collector.store_data(data=data,group_name=key,scraping_time=scraping_time,data_date=date_today)

        elif not data_collector.is_saved_data(key,data_date=date_today):
            _, data, scraping_time = get_data(wp_data[key])
            data_collector.store_data(data=data,group_name=key,scraping_time=scraping_time,data_date=date_today)
        
        else:
            print(f"{key} is saved in database at {str(date_today)}.")

def get_data(data:dict[str])-> tuple[np.array]:
    """
    Retrieves data using the specified method (Selenium or Requests).

    Args:
        data (dict[str]): The data configuration dictionary.

    Returns:
        tuple[np.array]: The column names, data array, and scraping time.
    """
    if data["method"] == "SELENIUM":
        for i in range(5):
            try:
                scraper = SeleniumScraper(name=data["name"],url=data["url"],
                                        table_class_name=data["table_name"],
                                        is_german=data["is_german"],
                                        cockie_handler=data["cockie_handler"],
                                        change_page_handler=data["page_handler"],
                                        encoding=data["encoding"]
                                        )
                log_file(name = data["name"], logging_datetime = scraper.scraping_time, success = True)
                return (scraper.column_names, scraper.data_array, scraper.scraping_time)
            # Warning: unspecified error handling. 
            except Exception:
                time.sleep(30)
                continue
        log_file(name = data["name"], logging_datetime = datetime.now(), success = False)

    if data["method"] == "REQUESTS":
        for i in range(5):
            try:
                scraper = RequestsScraper(name=data["name"],url=data["url"],
                                        table_class_name=data["table_name"],
                                        is_german=data["is_german"],
                                        num_string_cols=int(data["num_str_cols"]),
                                        num_float_cols=int(data["num_float_cols"]),
                                        encoding=data["encoding"]
                                        )
                log_file(name = data["name"], logging_datetime = scraper.scraping_time, success = True)
                return (scraper.column_names, scraper.data_array, scraper.scraping_time)
            except RequestException:
                time.sleep(30)
                continue
        log_file(name = data["name"], logging_datetime = datetime.now(), success = False)
    
def log_file(name:str, logging_datetime:datetime, success:bool)->None:
    if success:
        with open(LOG_FILE,"a+") as file:
            file.write(f"Write \"{name}\" on database from \"{logging_datetime.isoformat()}\".\n")
    else:
        with open(LOG_FILE,"a+") as file:
            file.write(f"Failure: Could not write \"{name}\" on database from \"{logging_datetime.isoformat()}\".\n")

    

if __name__ == "__main__":
    main()
