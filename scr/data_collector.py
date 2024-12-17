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
PATH:str = "data/webpage_data.h5"

class DataCollector:
    """
    A class to collect and store data from various web pages into an HDF5 file.

    Args:
        path (str, optional): The path to the HDF5 file. Defaults to PATH.
        parent_name (str, optional): The name of the parent group in the HDF5 file. Defaults to PARENT_NAME.
        group_names (dict[str, str], optional): A dictionary of group names and their URLs. Defaults to GROUP_NAMES.
    """

    def __init__(self, path:str = None,parent_name:str = None, group_names:dict[str:str]=None):
        if path is None:
            path = PATH
        self.path:str = path
        if parent_name is None:
            parent_name = PARENT_NAME
        self.parent_name:str = parent_name
        if group_names is None:
            group_names = GROUP_NAMES
        self.group_names:str = group_names

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
        """Stores the column names in the specified group.

        Args:
            column_names (np.array): The column names to store.
            group_name (str): The name of the group to store the column names in.

        Raises:
            ValueError: If group_name not in database.
        """
        with h5py.File(self.path, "a") as file:
            try:
                group = file[self.parent_name][group_name]
            except KeyError as exc:
                raise ValueError(f"No group \"{self.parent_name}/{group_name}\" in database.")
            if not "column_names" in group.keys():
                column_names = column_names
                dataset = group.create_dataset(name="column_names",data=column_names,
                                               shape=column_names.shape)
                dataset.attrs["description"] = "The names of the columns of the data."
                dataset.attrs["initialisation_date"] = date.today().timetuple()


    def store_data(self, data:np.array, group_name:str, scraping_time: datetime, data_date:date = None)-> None:
        """Stores the data in the specified group.

        Args:
            data (np.array): The data to store.
            group_name (str): The name of the group to store the data in.
            scraping_time (datetime): The time when the data was scraped.
            data_date (date, optional): The date of the data. Defaults to today.

        Raises:
            ValueError: If group_name not in database.
        """
        if data_date is None:
            data_date = date.today()

        data_name = str(time.mktime(data_date.timetuple()))

        with h5py.File(self.path, "a") as file:
            
            try:
                group = file[self.parent_name][group_name]
            except KeyError as exc:
                raise ValueError(f"No group \"{self.parent_name}/{group_name}\" in database.")

            if not data_name in group.keys():
                dataset = group.create_dataset(name=data_name,data=data,
                                               shape=data.shape)
                dataset.attrs["scraping_time"] = scraping_time.isoformat()
                dataset.attrs["inititialisation"] = data_date.timetuple()

    def get_data(self, group_name:str, data_date:date = None)->np.array:
        """
        Retrieves the data from the specified group and date.

        Args:
            group_name (str): The name of the group to retrieve data from.
            data_date (date, optional): The date of the data. Defaults to today.

        Returns:
            np.array: The retrieved data.

        Raises:
            ValueError: If group_name not in database.
            ValueError: If no dataset is found for the specified date.
        """
        if data_date is None:
            data_date = date.today()
        data_name = str(time.mktime(data_date.timetuple()))
        with h5py.File(self.path, "r") as file:
            try:
                group = file[self.parent_name][group_name]
            except KeyError as exc:
                raise ValueError(f"No group \"{self.parent_name}/{group_name}\" in database.")
            if data_name in group.keys():
                return group[data_name][()]
            raise ValueError("No dataset in database.")
        
    def get_column_names(self, group_name:str)->np.array:
        """ Retrieves the column names from the specified group.

        Args:
            group_name (str): The name of the group to retrieve column names from.

        Raises:
            ValueError: If group_name not in database.
            ValueError: If no column names are found in the group.

        Returns:
            np.array: The column names.
        """
        with h5py.File(self.path, "r") as file:
            try:
                group = file[self.parent_name][group_name]
            except KeyError as exc:
                raise ValueError(f"No group \"{self.parent_name}/{group_name}\" in database.")
            if "column_names" in group:
                return group["column_names"][()]
            raise ValueError(f"No column names in group {group_name}.")

    def get_last_days_group_data(self, group_name:str, num_days:int = 7)->dict[date:np.array]:
        """ Retrieves the data from the last specified number of days for the given group.

        Raises:
            ValueError: If group_name not in database.

        Returns:
            dict[date, np.array]: A dictionary of dates and their corresponding data.

        Raises:
            ValueError: If group_name not in database.
        """
        last_weeks_dates = [str(time.mktime((date.today()-i*timedelta(days=1)).timetuple())) for i in range(num_days)]

        with h5py.File(self.path, "r") as file:
            try:
                group = file[self.parent_name][group_name]
            except KeyError as exc:
                raise ValueError(f"No group \"{self.parent_name}/{group_name}\" in database.")
            return {date.fromtimestamp(float(name)) : group[name][()] for name in group.keys() if name in last_weeks_dates}

    def is_saved_data(self, group_name:str, data_date:date)->bool:
        """Checks if data for the specified date is saved in the group.

        Args:
            group_name (str): The name of the group to check.
            data_date (date): The date of the data.

        Raises:
            ValueError: If group_name not in database.

        Returns:
            bool: True if the data is saved, False otherwise.
        """
        if data_date is None:
            data_date = date.today()
        data_name = str(time.mktime(data_date.timetuple()))
        with h5py.File(self.path, "r") as file:
            try:
                group = file[self.parent_name][group_name]
            except KeyError as exc:
                raise ValueError(f"No group \"{self.parent_name}/{group_name}\" in database.")
            return data_name in group.keys()
        
    def is_saved_columns(self, group_name:str)->bool:
        """Checks if column names are saved in the group.

        Args:
            group_name (str): The name of the group to check.

        Raises:
            ValueError: If group_name not in database.

        Returns:
            bool: True if the column names are saved, False otherwise.
        """
        with h5py.File(self.path, "r") as file:
            try:
                group = file[self.parent_name][group_name]
            except KeyError as exc:
                raise ValueError(f"No group \"{self.parent_name}/{group_name}\" in database.")
            return "column_names" in group.keys()
