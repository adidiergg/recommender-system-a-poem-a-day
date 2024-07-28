import os
from dotenv import load_dotenv 
import psycopg2
import google.generativeai as genai
import time

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

def create_tag(tag,poem, conn):
    cursor = conn.cursor()
    sql = """ SELECT 1 FROM \"Tags\" WHERE name=%s LIMIT 1  """
    values = (tag,)
    cursor.execute(sql,values)
    row = cursor.fetchone()
    if row is None:
        sql = """ INSERT INTO \"Tags\" (name) VALUES (%s) """
        values = (tag,)
        cursor.execute(sql,values)
        conn.commit()
        #print("Tag created:", tag)
    
    sql = """ INSERT INTO \"PoemsTags\" (\"poemId\",\"tagId\") VALUES (%s, (SELECT id FROM \"Tags\" WHERE name=%s)) """
    values = (poem,tag)
    cursor.execute(sql,values)
    conn.commit()
    #print("Tag assigned to poem:",poem,tag)
    

def connect():
    try:
        conn = psycopg2.connect(DATABASE_URL,sslmode="require")
        print("Connected to the database")
        return conn
    except Exception as e:
        print("Database Error:", e)
        return None

def chat():
    try:
        generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }

        safety_settings={
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
        }

        genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        safety_settings=safety_settings,
        generation_config=generation_config,
        )

        chat_session = model.start_chat(
        history=[
            {
            "role": "user",
            "parts": [
                "eres un licenciado en letras y literatura. necesito clasificar una recopilacion de poemas por medio de etiquetas. te voy a sugerir los poemas de diferentes autores. tu trabajo sera asignar etiquetas que se relacionen con el poema. es necesario que solo escribas las etiquetas necesarias\ncomo minimo 2 etiquetas y maximo 5 etiquetas sin enumerar.",
            ],
            },
            {
            "role": "model",
            "parts": [
                "¡Me parece genial! Estoy listo para ponerme mi sombrero de crítico literario. Adelante, dime qué poemas tienes en mente y con gusto te daré etiquetas que capturen su esencia.  📖 \n",
            ],
            },
        ]
        )
        return chat_session
    except Exception as e:
        print("Error Gemini:", e)
        return None
    
def main():
    connection = connect()
    session = chat()
    if connection is None:
        return
    if session is None:
        return
    cursor = connection.cursor()
    sql = """SELECT id,content FROM \"Poems\" """
    cursor.execute(sql)
    poems = cursor.fetchall()
    for i,poem in enumerate(poems):
        t = time.process_time()
        elapsed_time = time.process_time() -t
        print("Elapsed time:", elapsed_time)
        response = session.send_message(poem[1])
        tags = response.text.rstrip(". \n").split(",")
        tags  = [tag.rstrip(" ").lstrip(" ")   for tag in tags]
        for tag in tags:
            create_tag(tag.upper(),poem[0], connection)
        print("Poem:", i)
        time.sleep(10)
        



if __name__ == "__main__":
    main()

