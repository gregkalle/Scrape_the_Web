from datetime import date, timedelta
import numpy as np
import time
import h5py



GROUP_NAMES:dict[str:str] = {"SMARD.DE":"https://www.smard.de/",
                             "finance.yahoo.com":"https://finance.yahoo.com",
                             "divi Register":"https://www.intensivregister.de/",
                             "dwd":"https://www.dwd.de"
                            }
PARENT_NAME:str ="webpages to be informed"
PATH:str = "webpage_date.h5"

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
                root_group.attrs["name"] = self.parent_name
                root_group.attrs["initialisation_date"] = date.today().timetuple()
            else:
                root_group = file[self.parent_name]

            for name in self.group_names:
                if not name in root_group.keys():
                    group = root_group.create_group(name=name)
                    group.attrs["name"] = name
                    group.attrs["url"] = self.group_names[name]
                    group.attrs["initialisation_date"] = date.today().timetuple()

    def store_column_names(self,column_names:np.array,group_name:str)->None:
        with h5py.File(self.path, "a") as file:
            group = file[self.parent_name][group_name]
            if not "column_names" in group:
                column_names = column_names
                dataset = group.create_dataset(name="column_names",data=column_names)
                dataset.attrs["description"] = "The names of the columns of the data."
                dataset.attrs["initialisation_date"] = date.today().timetuple()


    def store_data(self, data:np.array, group_name:str, data_date:date = None)-> None:
        
        if data_date is None:
            data_date = date.today()

        data_name = str(time.mktime(data_date.timetuple()))

        with h5py.File(self.path, "a") as file:
            
            group = file[self.parent_name][group_name]

            if not data_name in group.keys():
                dataset = group.create_dataset(name=data_name,data=data)
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

    def is_saved(self, group_name:str, data_date:date)->bool:
        if data_date is None:
            data_date = date.today()
        data_name = str(time.mktime(data_date.timetuple()))
        with h5py.File(self.path, "r") as file:
            group = file[self.parent_name][group_name]
            return data_name in group.keys()
