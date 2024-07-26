import requests
from bs4 import BeautifulSoup
import random
import markdownify
import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL,sslmode="require")
    print("Connected to the database")
except Exception as e:
    print("Database Error:", e)




def get_poem_random(poems):
    poem = random.choice(poems)
    try:
        r = requests.get(poem)
        soup = BeautifulSoup(r.text,"html.parser")
        title = soup.article.header.div.h1.text
        content = soup.article.center.table.tbody.tr.td.html.body
        soup.article.header.div.h1.clear()
        soup.article.header.div.p.clear()
        author = soup.article.header.div.text.replace("\n","").lstrip(" ").rstrip(" ")
        content = markdownify.markdownify(content.prettify())
        if title is not None and content is not None and author is not None:
            sql = """ INSERT INTO \"Poems\" (title,content,author) VALUES (%s,%s,%s)   """
            cursor = conn.cursor()
            values = (title,content,author)
            cursor.execute(sql,values)
            conn.commit()
            count = cursor.rowcount
                             

    except Exception as e:
        print("Error:",e)

def get_poems_author(author):
    
    try:
        poems = []
        r = requests.get(author)
        soup = BeautifulSoup(r.text,"html.parser")
       
        for i in soup.find_all('a'):
            href = i.get('href')
            if href is not None and href[0:29] == "https://ciudadseva.com/texto/":
               poems.append(href)
        print("Getting poems from author:", author)
        get_poem_random(poems)
    except Exception as e:
        print("Error:", e)
    

def main():
    try:
        author = []
        r = requests.get("https://ciudadseva.com/biblioteca/indice-autor-poemas/")
        soup = BeautifulSoup(r.text,"html.parser")
        for link in soup.find_all('a'):
            href = link.get('href')
            if href is not None and href[0:29] == "https://ciudadseva.com/autor/":
                author.append(href)
        
        for i in author:
            get_poems_author(i)
        

    except Exception as e:
        conn.close()
        print("Error:", e)

if __name__ == "__main__":
    #get_poem_random("https://ciudadseva.com/texto/mas-bella-que-las-lagrimas/")
    main()