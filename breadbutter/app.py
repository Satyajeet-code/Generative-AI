from flask import Flask, request, render_template
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_groq import ChatGroq
from recommendation import get_final_recommendation

load_dotenv()

app = Flask(__name__)

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    cursor_factory=RealDictCursor
)
cursor = conn.cursor()

llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")
model_name = "all-mpnet-base-v2"


@app.route('/', methods=['GET', 'POST'])
def index():
    recommendation = ""
    if request.method == 'POST':
        user_query = request.form.get("user_query")
        recommendation = get_final_recommendation(user_query, conn, cursor, llm, model_name)
    return render_template('index.html', recommendations=recommendation)

if __name__ == '__main__':
    app.run(debug=True)