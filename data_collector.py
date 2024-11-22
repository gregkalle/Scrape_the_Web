from datetime import date, timedelta
import time
import numpy as np
import h5py


GROUP_NAMES:tuple[str] = ("smard_data","data_from_date","changes_to_day_before")
PATH:str = "smard_date.h5"
URL:str = "https://www.smard.de/"

class DataCollector:

    def __init__(self, path:str = None, group_names:tuple[str]=None, url:str = None):
        if path is None:
            self.path = PATH
        if group_names is None:
            self.group_names = GROUP_NAMES
        if url is None:
            url = URL

        with h5py.File(self.path, "a") as file:

            if not self.group_names[0] in file.keys():
                root_group = file.create_group(name=self.group_names[0])
                root_group.attrs["name"] = self.group_names[0]
                root_group.attrs["url"] = url
                root_group.attrs["description"] = "Actual net electricity generation "\
                    "divided according to source of energy generation [MWh]."
                root_group.attrs["initialisation_date"] = date.today().timetuple()
            else:
                root_group = file[self.group_names[0]]

            for name in GROUP_NAMES[1:]:
                if not name in root_group.keys():
                    group = root_group.create_group(name=name)
                    group.attrs["name"] = name
                    group.attrs["url"] = "https://www.smard.de/"
                    group.attrs["initialisation_date"] = date.today().timetuple()

    def store_column_names(self,column_names:np.array)->None:
        with h5py.File(self.path, "a") as file:
            if not "column_names" in file.keys():
                column_names = column_names.astype(np.dtype.str)
                dataset = file.create_dataset(name="column_names",data=column_names,dtype=h5py.string_dtype())
                dataset.attrs["name"] = "Column Names"
                dataset.attrs["description"] = "The names of the columns of the data stored in the children databases."


    def store_data(self, data:np.array, data_date:date = None)-> None:
        
        if data_date is None:
            data_date = date.today()

        data_name = str(time.mktime(data_date.timetuple()))

        with h5py.File(self.path, "a") as file:
            
            group = file[self.group_names[0]][self.group_names[1]]

            if not data_name in group.keys():
                dataset = group.create_dataset(name=data_name,data=data,shape=(len(data),len(data[0])))
                dataset.attrs["inititialisation"] = data_date.timetuple()

    def store_changes_to_day_before(self, data_date:date = None, offset:int = 0)->None:

        if data_date is None:
            data_date = date.today()

        name_date = str(time.mktime(data_date.timetuple()))
        day_before = data_date - timedelta(days=1)
        name_day_before = str(time.mktime(day_before.timetuple()))

        data_name = name_day_before + name_date

        with h5py.File(self.path, "a") as file:
            group_data = file[self.group_names[0]][self.group_names[1]]
            group_changes = file[self.group_names[0]][self.group_names[2]]

            if data_name in group_changes.keys():
                raise ValueError("Data is already saved.")
            
            if not name_day_before in group_data:
                raise ValueError("No data of date before.")
            
            data = group_data[name_date][()]
            data_day_before = group_data[name_day_before][()]
            
            changes = self.calculate_difference(data[:,offset:],data_day_before[:,offset:])
            data_changes = np.append(data[:,:offset],changes)

            dataset = group_changes.create_dataset(name=data_name,data=data_changes,shape=(len(data_changes),len(data_changes[0])))
            dataset.attrs["inititialisation"] = data_date.timetuple()


    def calculate_difference(self, data:np.array, data_day_before:np.array)->np.array:
        return np.subtract(data_day_before,data)

    def is_stored(self, the_time:int)->bool:
        with h5py.File(self.path, "r") as file:
            return str(the_time) in file[self.group_names[0]][self.group_names[1]].keys()
