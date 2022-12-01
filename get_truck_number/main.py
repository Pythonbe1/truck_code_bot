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
    print(con)
    query = f"SELECT * from user_information where chat_id={id}"
    df = pd.read_sql_query(query, con)
    return len(df)


def insert_db(id, first_name, second_name):
    conn = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                            user=os.environ.get("PG_USER"),
                            password=os.environ.get("PG_PASSWORD"),
                            host=os.environ.get("PG_HOST"),
                            port=os.environ.get("PG_PORT"))
    cur = conn.cursor()
    sql = f""" INSERT INTO user_information (chat_id, username, last_name)
                 VALUES ({id}, '{first_name}', '{second_name}');"""
    cur.execute(sql)
    conn.commit()
    cur.close()
    print('Done')


def get_truck_data(code):
    con = psycopg2.connect(dbname=os.environ.get("PG_NAME"),
                           user=os.environ.get("PG_USER"),
                           password=os.environ.get("PG_PASSWORD"),
                           host=os.environ.get("PG_HOST"),
                           port=os.environ.get("PG_PORT"))
    query = f"SELECT * from truck_information where truck_number='{str(code)}'"
    df = pd.read_sql_query(query, con)
    print(df)
    return df


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
            insert_db(user_id, user_name, surname)
        text = message.text
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

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    load_dotenv()
    token = os.environ.get("BOT_TOKEN")
    telegram_bot(token)
