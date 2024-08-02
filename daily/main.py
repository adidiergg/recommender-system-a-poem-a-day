from dotenv import load_dotenv
import os 
import psycopg2
import random


load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")

def connect():
    try:
        conn = psycopg2.connect(DATABASE_URL,sslmode="require")
        print("Connected to the database")
        return conn
    except Exception as e:
        print("DataBase Error:",e)
        return None

def main():
    connection = connect()
    if connection is None:
        return
    cursor = connection.cursor()
    sql = """ SELECT id FROM \"Poems\" """
    cursor.execute(sql)
    poems = [i[0]  for i in cursor.fetchall()]
    for i in range(1,366+1):
        poem = random.choice(poems)
        print(i,poem)
        poems.remove(poem)
        sql = """ INSERT INTO \"Dailies\" (\"day\",\"poemId\") VALUES (%s,%s) """
        values = (i,poem,)
        cursor.execute(sql,values)
        connection.commit()
    connection.close()

    

if __name__ == "__main__":
    main()