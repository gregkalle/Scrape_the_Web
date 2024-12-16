from datetime import date, datetime, timedelta
import numpy as np
import time
import h5py



GROUP_NAMES:dict[str:str] = {"SMARD.DE":"https://www.smard.de/",
                             "finance.yahoo.com":"https://finance.yahoo.com",
                             "divi Register":"https://www.intensivregister.de/",
                             "dwd":"https://www.dwd.de"
                            }
PARENT_NAME:str ="webpages to be informed"
PATH:str = "webpage_data.h5"

class DataCollector:

    def __init__(self, path:str = None,parent_name:str = None, group_names:dict[str:str]=None):
        if path is None:
            path = PATH
        self.path = path
        if parent_name is None:
            parent_name = PARENT_NAME
        self.parent_name = parent_name
        if group_names is None:
            group_names = GROUP_NAMES
        self.group_names = group_names

        with h5py.File(self.path,"a") as file:

            if not self.parent_name in file.keys():
                root_group = file.create_group(name=self.parent_name)
                root_group.attrs["initialisation_date"] = date.today().timetuple()
            else:
                root_group = file[self.parent_name]

            for name in self.group_names:
                if not name in root_group.keys():
                    group = root_group.create_group(name=name)
                    group.attrs["url"] = self.group_names[name]
                    group.attrs["initialisation_date"] = date.today().timetuple()

    def store_column_names(self,column_names:np.array,group_name:str)->None:
        with h5py.File(self.path, "a") as file:
            group = file[self.parent_name][group_name]
            if not "column_names" in group.keys():
                column_names = column_names
                dataset = group.create_dataset(name="column_names",data=column_names,
                                               shape=column_names.shape)
                dataset.attrs["description"] = "The names of the columns of the data."
                dataset.attrs["initialisation_date"] = date.today().timetuple()


    def store_data(self, data:np.array, group_name:str, scraping_time: datetime, data_date:date = None)-> None:
        
        if data_date is None:
            data_date = date.today()

        data_name = str(time.mktime(data_date.timetuple()))

        with h5py.File(self.path, "a") as file:
            
            group = file[self.parent_name][group_name]

            if not data_name in group.keys():
                dataset = group.create_dataset(name=data_name,data=data,
                                               shape=data.shape)
                dataset.attrs["scraping_time"] = scraping_time.isoformat()
                dataset.attrs["inititialisation"] = data_date.timetuple()

    def get_data(self, group_name:str, data_date:date = None)->np.array:
        
        if data_date is None:
            data_date = date.today()
        data_name = str(time.mktime(data_date.timetuple()))
        with h5py.File(self.path, "r") as file:
            group = file[self.parent_name][group_name]
            if data_name in group.keys():
                return group[data_name][()]
            raise ValueError("No dataset in database.")
        
    def get_column_names(self, group_name:str)->np.array:
        with h5py.File(self.path, "r") as file:
            group = file[self.parent_name][group_name]
            if "column_names" in group:
                return group["column_names"][()]
            raise ValueError(f"No column names in group {group_name}.")

    def get_last_days_group_data(self, group_name:str, num_days:int = 7)->dict[date:np.array]:
        last_weeks_dates = [str(time.mktime((date.today()-i*timedelta(days=1)).timetuple())) for i in range(num_days)]

        with h5py.File(self.path, "r") as file:
            group = file[self.parent_name][group_name]
            return {date.fromtimestamp(float(name)) : group[name][()] for name in group.keys() if name in last_weeks_dates}

    def is_saved_data(self, group_name:str, data_date:date)->bool:
        if data_date is None:
            data_date = date.today()
        data_name = str(time.mktime(data_date.timetuple()))
        with h5py.File(self.path, "r") as file:
            group = file[self.parent_name][group_name]
            return data_name in group.keys()
        
    def is_saved_columns(self, group_name:str)->bool:
        with h5py.File(self.path, "r") as file:
            group = file[self.parent_name][group_name]
            return "column_names" in group.keys()
