from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
import numpy as np


def get_point_deci(text:str, change_comma:bool = True)->str:
    if change_comma:
        return text.replace(".","").replace(",",".")
    return text

def get_float(text:str)->float:
    digits = "".join([letter for letter in text if letter.isdigit() or letter == "."])
    try:
        return float(digits)
    except ValueError as exc:
        raise ValueError("Not a float.") from exc

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.get("https://www.intensivregister.de/#/aktuelle-lage/laendertabelle")
driver.implicitly_wait(10)

#driver.find_element(by=By.CLASS_NAME,value="js-cookie-decline").click()

table = driver.find_element(by=By.CLASS_NAME,value="laendertabelle")
head = table.find_element(by=By.TAG_NAME,value="thead")
column_names = []

for name in head.find_elements(by=By.TAG_NAME,value="th"):
    if name.text and not name.get_dom_attribute("colspan") is None:
        column_names.extend([name.text]*int(name.get_dom_attribute("colspan")))
    elif name.text:
        column_names.append(name.text)

print(column_names)

data = []

bodys = table.find_elements(by=By.TAG_NAME,value="tbody")

for body in bodys:
    rows = body.find_elements(by=By.TAG_NAME,value="tr")

    for row in rows:
        data_header = []
        for table_header in row.find_elements(by=By.TAG_NAME,value="th"):
            data_header.append(table_header.text)

        data_body = []
        for table_data in row.find_elements(by=By.TAG_NAME,value="td"):
            if table_data.text:
                element_data = get_float(get_point_deci(table_data.text, True))
                data_body.append(element_data)
        data.append((tuple(data_header),tuple(data_body)))

len_f0 = len(data[0][0])
len_f1 = len(data[0][1])

data_type = np.dtype([("","U20",(len_f0,)),("","f4",(len_f1,))])


data_array = np.array(data, dtype=data_type)


print(data_array)

driver.close()
