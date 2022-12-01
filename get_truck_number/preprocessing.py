import docx
import sqlite3
import os
import pandas as pd

path = r'C:\Users\svnduw\Downloads\Telegram Desktop'
files = os.listdir(path)
doc = docx.Document(f"{path}//{files[6]}")
result = [p.text.strip() for p in doc.paragraphs if len(p.text) != 0 and len(p.text) != 1]
data = pd.DataFrame(result, columns=['truck_number'])
from unidecode import unidecode


def normalize(table):
    result = []
    for index, row in table.iterrows():
        string = row['truck_number'].lower()
        string = string.upper()
        string = unidecode(string)
        string = string.strip()
        string = string.split(' ')
        #         print(string)
        if len(string) != 1:
            for i in string:
                if len(i) != 0:
                    result.append(i)
        else:
            if len(string[0]) != 0:
                result.append(string[0])
    return result


b = normalize(data)
files[6]

df = pd.DataFrame(b, columns=['truck_number'])
df['date'] = '28.11.2022'

df.to_excel(r'D:\Bekbol files\Nurgul_data\28.11.2022.xlsx', index=False)



path = r'D:\Bekbol files\Nurgul_data'
result = pd.DataFrame()
files = os.listdir(path)
conn = sqlite3.connect(r"D:\code\truck_number_bot\get_truck_number/truck_number")
for file in files:
    temp = pd.read_excel(f'{path}//{file}')
    result = result.append(temp, ignore_index=True)
count = 0
for index, row in result.iterrows():
    count += 1
    cur = conn.cursor()
    sql = f""" INSERT INTO main.truck_information (truck_number, date)
    VALUES ('{row['truck_number']}', '{row['date']}');"""
    cur.execute(sql)
    conn.commit()
    cur.close()
    print(f'{count}//{len(result)}')
