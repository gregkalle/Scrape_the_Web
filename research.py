import time
from datetime import date, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from data_collector import DataCollector
from selenium_scraper import SeleniumScraper
import numpy as np
import h5py

GROUP_NAMES:dict[str:str] = {"SMARD.DE":"https://www.smard.de/",
                             "finance.yahoo.com":"https://finance.yahoo.com",
                             "divi Register":"https://www.intensivregister.de/",
                             "dwd":"https://www.dwd.de"
                            }
PARENT_NAME = "webpages to be informed"
PATH:str = "webpage_data.h5"

def main():
    data_collector = DataCollector(path=PATH,parent_name=PARENT_NAME,group_names=GROUP_NAMES)


    #column = np.strings.decode(data_collector.get_column_names(group_name="dwd"),encoding="iso-8859-1")
    #for name in GROUP_NAMES:
        #print(data_collector.get_data(name))

    #array1 = np.strings.decode(array["f0"], encoding="iso-8859-1")

 
          
    data_collector = DataCollector(path=PATH,parent_name=PARENT_NAME,group_names=GROUP_NAMES)


    data = data_collector.get_last_days_group_data(group_name="finance.yahoo.com")

    days = list(data.keys())

    days.append(days[0]+timedelta(days=1))
    days.append(days[0]+timedelta(days=2))

    data_array = data[days[0]]["f1"][:,0]

    new = np.column_stack((data_array,data_array,data_array))
    
    
    print(data[days[0]]["f0"][0,0].decode("UTF-8"))
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.plot(days,new[0,:],marker="o",linewidth=1.0)
    plt.gcf().autofmt_xdate()
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.show()
    





if __name__=="__main__":
    main()