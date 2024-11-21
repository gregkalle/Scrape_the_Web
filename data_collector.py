import pandas as pd
from smard_data_scraper import SmardDataScraper


df = SmardDataScraper().dataframe


print(df)

"""items = list(scraper.get_table_items())

scraper.next_page()

columns = scraper.get_columns()
print(columns)

items.extend(list(scraper.get_table_items()))

df = pd.DataFrame(data=items,columns=columns)

print(df)

scraper.quit()
"""