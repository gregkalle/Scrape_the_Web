import numpy as np
import requests
from bs4 import BeautifulSoup
from functions import get_float, get_point_deci


class RequestsScraper():

    def __init__(self,name:str, url:str, table_class_name:str, is_german:bool, num_string_cols:int, num_float_cols:int):
        self.url = url
        self.table_class_name = table_class_name
        self.is_german = is_german
        self.num_string_cols = num_string_cols
        self.num_float_cols = num_float_cols
        

LEN_F0 = 3
LEN_F1 = 3

   
url = "https://finance.yahoo.com/markets/currencies/"
class_name = "markets-table"

page = requests.get(url=url,timeout=10)

if not page.status_code == 200:
    print(page.status_code)
    raise requests.ConnectionError("Connection faild.")

soup = BeautifulSoup(page.content,features="lxml")


table = soup.find(class_=class_name)

head = table.find("thead")

column_names = [name.getText(strip=True) for name in head.find_all("th") if name.getText(strip=True)]

column_names = np.array(column_names, dtype="U20")

data=[]

for row in table.find("tbody").find_all("tr"):
    string_data = []
    float_data = []
    for i,element in enumerate(row.find_all("td")):
        text = list(element.stripped_strings)[0] if element.getText(strip=True) else ""
        if i<LEN_F0:
            string_data.append(text)
        elif i>= LEN_F0:
            try:
                text = get_float(text=text)
                float_data.append(text)
            except ValueError:
                float_data.append(None)
        if i>=LEN_F1+LEN_F0-1:
            break
    data.append((tuple(string_data),tuple(float_data)))

data_type = np.dtype([("","U20",(LEN_F0,)),("","f4",(LEN_F1,))])

data_array = np.array(data, dtype=data_type)

print(data_array)