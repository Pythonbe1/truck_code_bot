import docx
import sqlite3
import os
import pandas as pd
import psycopg2
from psycopg2 import extras
from unidecode import unidecode
from dotenv import load_dotenv
# ########################################
# def normalize(table):
#     result = []
#     for index, row in table.iterrows():
#         string = row['truck_number'].lower()
#         string = string.upper()
#         string = unidecode(string)
#         string = string.strip()
#         string = string.split(' ')
#         #         print(string)
#         if len(string) != 1:
#             for i in string:
#                 if len(i) != 0:
#                     result.append(i)
#         else:
#             if len(string[0]) != 0:
#                 result.append(string[0])
#     return result
#
#
# path = r'C:\Users\b.sultankulov\Desktop\Bekbol\nurgul_telegram_bot'
# files = os.listdir(path)
# doc = docx.Document(f"{path}//{files[0]}")
# result = [p.text.strip() for p in doc.paragraphs if len(p.text) != 0 and len(p.text) != 1]
# data = pd.DataFrame(result, columns=['truck_number'])
# b = normalize(data)
# print(files[0])
#
#
# # ################################
# df = pd.DataFrame(b, columns=['truck_number'])
# df['date'] = '05.12.2022'
# # #######################################
# df.to_excel(r'C:\Users\b.sultankulov\Desktop\Bekbol\nurgul_telegram_bot\05.12.2022.xlsx', index=False)

#########################################

path = r'C:\Users\b.sultankulov\Desktop\Bekbol\nurgul_telegram_bot'
result = pd.DataFrame()
files = os.listdir(path)
for file in files:
    temp = pd.read_excel(f'{path}//{file}')
    result = result.append(temp, ignore_index=True)
# ##############################################
#
def execute_values(conn, df, table):
    tuples = [tuple(x) for x in df.to_numpy()]

    cols = ','.join(list(df.columns))
    print(cols)
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("the dataframe is inserted")
    cursor.close()
#
#
load_dotenv()
connection = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                           user=os.environ.get("PG_USER"),
                           password=os.environ.get("PG_PASSWORD"),
                           host=os.environ.get("PG_HOST"),
                           port=os.environ.get("PG_PORT"))
# print(result)
execute_values(connection, result, 'public.truck_information')
############################################