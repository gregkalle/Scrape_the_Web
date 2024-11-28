import numpy as np
import requests
from bs4 import BeautifulSoup

LEN_F0 = 3
LEN_F1 = 3

def get_float(text:str)->float:
    digits = "".join([letter for letter in text if letter.isdigit() or letter in [".","-"]])
    try:
        return float(digits)
    except ValueError as exc:
        raise ValueError("Not a float.") from exc
    
url = "https://finance.yahoo.com/markets/currencies/"
class_name = "markets-table"

page = requests.get(url=url,timeout=10)

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