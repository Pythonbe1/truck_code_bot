from datetime import timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold
import pandas as pd
import nest_asyncio
import psycopg2
import os
from dotenv import load_dotenv
import warnings

warnings.filterwarnings('ignore')


def get_user_data(id):
    load_dotenv()
    con = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                           user=os.environ.get("PG_USER"),
                           password=os.environ.get("PG_PASSWORD"),
                           host=os.environ.get("PG_HOST"),
                           port=os.environ.get("PG_PORT"))
    query = f"SELECT * from user_information where chat_id={id}"
    df = pd.read_sql_query(query, con)
    return len(df)


def get_chat_id(id):
    load_dotenv()
    con = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                           user=os.environ.get("PG_USER"),
                           password=os.environ.get("PG_PASSWORD"),
                           host=os.environ.get("PG_HOST"),
                           port=os.environ.get("PG_PORT"))
    query = f"SELECT i.chat_id from user_information i where i.chat_id={id}"
    df = pd.read_sql_query(query, con)

    return df['chat_id'].tolist()[0]


def get_subscription(id, kind):
    load_dotenv()
    con = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                           user=os.environ.get("PG_USER"),
                           password=os.environ.get("PG_PASSWORD"),
                           host=os.environ.get("PG_HOST"),
                           port=os.environ.get("PG_PORT"))
    if kind == 'get':
        query = f"SELECT subscription_quantity from user_subscription where chat_id={id}"
        df = pd.read_sql_query(query, con)
        return df['subscription_quantity'].tolist()[0]


def insert_db(id, first_name, second_name, kind):
    load_dotenv()
    conn = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                            user=os.environ.get("PG_USER"),
                            password=os.environ.get("PG_PASSWORD"),
                            host=os.environ.get("PG_HOST"),
                            port=os.environ.get("PG_PORT"))
    cur = conn.cursor()
    if kind == 'insert':
        sql = f""" INSERT INTO user_information (chat_id, username, last_name)
                 VALUES ({id}, '{first_name}', '{second_name}');"""
        cur.execute(sql)
        conn.commit()
        cur.close()
    elif kind == 'update':
        sql = f"""update user_information 
                set quantity = quantity+1 
                where chat_id={id}"""
        cur.execute(sql)
        conn.commit()
        cur.close()


def get_truck_data(code):
    load_dotenv()
    con = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                           user=os.environ.get("PG_USER"),
                           password=os.environ.get("PG_PASSWORD"),
                           host=os.environ.get("PG_HOST"),
                           port=os.environ.get("PG_PORT"))
    query = f"SELECT * from truck_information where truck_number='{str(code)}'"
    df = pd.read_sql_query(query, con)
    return df


def get_list_chat_id():
    load_dotenv()
    con = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                           user=os.environ.get("PG_USER"),
                           password=os.environ.get("PG_PASSWORD"),
                           host=os.environ.get("PG_HOST"),
                           port=os.environ.get("PG_PORT"))
    query = f"SELECT chat_id from user_subscription where subscription_quantity>0"
    df = pd.read_sql_query(query, con)
    return df['chat_id'].tolist()
def update_subscription(id):
    load_dotenv()
    con = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                           user=os.environ.get("PG_USER"),
                           password=os.environ.get("PG_PASSWORD"),
                           host=os.environ.get("PG_HOST"),
                           port=os.environ.get("PG_PORT"))
    cursor = con.cursor()

    query = f"update user_subscription" \
            f" set subscription_quantity=subscription_quantity-1 where chat_id={id}"
    cursor.execute(query)
    con.commit()
    cursor.close()




def telegram_bot(token_data):
    nest_asyncio.apply()
    bot = Bot(token_data, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    @dp.message_handler(commands='start')
    async def start_message(message: types.Message):
        await bot.send_message(message.from_user.id, 'Введите трек-код')

    @dp.message_handler()
    async def day(message: types.Message):
        await message.answer('Подождите...')
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        surname = message.from_user.last_name
        a = get_user_data(user_id)
        if a == 0:
            insert_db(user_id, user_name, surname, 'insert')
        elif a == 1:
            insert_db(user_id, user_name, surname, 'update')

        text = message.text
        quest_id = get_chat_id(user_id)

        if quest_id in get_list_chat_id():
            result = get_truck_data(text)
            if len(result) != 0:
                result["date"] = pd.to_datetime(result["date"], format="%d.%m.%Y")
                result['come_date'] = result["date"] + timedelta(days=15)
                result["date"] = result["date"].dt.date
                result["come_date"] = result["come_date"].dt.date
                for index, row in result.iterrows():
                    card = f"{hbold('Трек-код: ')}{row['truck_number']}\n" \
                           f"{hbold('Дата отправки: ')}{str(row['date'])}\n" \
                           f"{hbold('Примерная дата прибытия: ')}{str(row['come_date'])}"

                    await message.answer(card)
            else:
                card = f"{hbold('Трек-код: ')}{text}\n" \
                       f"Такой товар еще не отправлен"
                await message.answer(card)
            update_subscription(quest_id)
        else:
            card = f"{hbold('У вас нет доступа! Обращайтесь к Нургуль Абенова https://t.me/AbenovaNT ')}"
            await message.answer(card)


    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    load_dotenv()
    token = os.environ.get("BOT_TOKEN")
    telegram_bot(token)
