import time
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By

#power plant types
POWERPLANT_TYPES=["1004066","1001226","1001225","1004067","1004068","1001228","1001223","1004069","1004071","1004070","1001227"]

class SmardDataScraper:

    def __init__(self,resolution = "hour",region ="DE",plant_types = POWERPLANT_TYPES):
        self.__driver = webdriver.Chrome()

        start,end = self.__get_start_end()
        self.__url = self.__get_url(start,end,resolution,region,plant_types)
        self.__driver.get(self.__url)
        self.__driver.implicitly_wait(1)
        self.__driver.find_element(by=By.CLASS_NAME,value="js-cookie-decline").click()
        self.__driver.implicitly_wait(1)

    def __get_url(self,start,end,resolution,region,plant_types):
        url = "https://www.smard.de/page/home/marktdaten/"\
        f"78?marketDataAttributes=%7B%22resolution%22:%22{resolution}%22"\
        f",%22region%22:%22{region}%22,%22from%22:"\
        f"{start},%22to%22:{end},%22moduleIds"\
        f"%22:%5B{",".join(plant_types)}%5D,%22selectedCategory%22:1,%22activeChart%22"\
        ":false,%22style%22:%22color%22,%22categoriesModuleOrder%22:%7B%7D%7D"
        return url

    def __get_start_end(self):
        end = date.today()
        start = end - timedelta(days=1)

        end = time.mktime(end.timetuple())*1000 - 1
        start = time.mktime(start.timetuple())*1000
        return start,end

    @property
    def driver(self):
        return self.__driver

    def quit(self):
        self.__driver.quit()

    def next_page(self):
        self.__driver.find_element(by=By.CLASS_NAME,value="js-cookie-decline").click()
        self.__driver.implicitly_wait(1)

    def get_columns(self):
        table = self.__driver.find_element(by=By.CLASS_NAME,value="c-chart-table__container")
        column_names = table.find_elements(by=By.CLASS_NAME,value="c-chart-table__head")
        return [name.text for name in column_names if not name.text == "in MWh"]
    
    def get_table_items(self):
        table = self.__driver.find_element(by=By.CLASS_NAME,value="c-chart-table__container")
        elements = table.find_elements(by=By.CLASS_NAME,value="c-chart-table__element")
        return [value.text for value in elements]





driver = webdriver.Chrome()

start = 1732057200_000
end = 1732143599_999

url = "https://www.smard.de/page/home/marktdaten/"\
        "78?marketDataAttributes=%7B%22resolution%22:%22hour%22"\
        ",%22region%22:%22DE%22,%22from%22:"\
        f"{start},%22to%22:{end},%22moduleIds"\
        "%22:%5B1000102,1000103,1000104,1000108"\
        ",1000109,1000110,1000111,1000112,1000113"\
        ",1000121,1000101,1000100,5000410,1001226,"\
        "1001228,1001227,1001223,1001224,1001225,1004066,1004067,1004069,"\
        "1004071,1004070,1004068%5D,%22selectedCategory%22:1,%22activeChart%22"\
        ":false,%22style%22:%22color%22,%22categoriesModuleOrder%22:%7B%7D%7D"

driver.get(url=url)

driver.implicitly_wait(1)

cockie_button = driver.find_element(by=By.CLASS_NAME,value="js-cookie-decline")

cockie_button.click()

table = driver.find_element(by=By.CLASS_NAME,value="c-chart-table__container")

elements_1 = table.find_elements(by=By.CLASS_NAME,value="c-chart-table__element")

column_names = table.find_elements(by=By.CLASS_NAME,value="c-chart-table__head")

for e in elements_1:
    print(e.text)



button = driver.find_element(by=By.CLASS_NAME,value="next")



driver.implicitly_wait(1)

button.click()


table = driver.find_element(by=By.CLASS_NAME,value="c-chart-table__container")

elements_2 = table.find_elements(by=By.CLASS_NAME,value="c-chart-table__element")

for e in elements_2:
    print(e.text)

driver.quit()