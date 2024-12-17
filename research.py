from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
from scr.data_collector import DataCollector

GROUP_NAMES:dict[str:str] = {"SMARD.DE":"https://www.smard.de/",
                             "finance.yahoo.com":"https://finance.yahoo.com",
                             "divi Register":"https://www.intensivregister.de/",
                             "dwd":"https://www.dwd.de"
                            }
PARENT_NAME = "webpages to be informed"
PATH:str = "data/webpage_data.h5"

def main():
    
    data_collector = DataCollector(path=PATH,parent_name=PARENT_NAME,group_names=GROUP_NAMES)


    #data smard.de column number 5 ("f1" no.3)
    field_name, column_number = "f1", 3
    group_name=[key for key in GROUP_NAMES.keys()][0]
    data_name = data_collector.get_column_names(group_name=group_name)
    
    data_dict = data_collector.get_last_days_group_data(group_name=group_name)

    data_to_show = np.concatenate([data_dict[key][field_name][:,column_number] for key in data_dict.keys()])

    dates = list(data_dict.keys())
    y_value = []
    for date_ in dates:
        y_value += [datetime.combine(date_,datetime.min.time()) + i * timedelta(hours=1) for i in range(24)]

    print(y_value)
    print(data_to_show)


        
    """
    data = data_collector.get_last_days_group_data(group_name="SMARD.DE")

    print(data)

    for key in data.keys():
        print(key)

    days = list(data.keys())



    data_array = np.column_stack([data[day]["f1"][:,0] for day in days])

    print(data_array)
    """
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.subplot().vlines(x=dates,ymin=min(data_to_show),ymax=max(data_to_show),linestyles="dashed")
    plt.plot(y_value,data_to_show,marker="o",linewidth=1.0)
    plt.gcf().autofmt_xdate()
    plt.xlabel("Time")
    plt.ylabel(str(data_name[5]).replace("\\n"," "))
    plt.show()
    





if __name__=="__main__":
    main()