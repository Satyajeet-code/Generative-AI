from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import pickle
from langchain.vectorstores import FAISS
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from flask import Flask, render_template, request, session
from langchain_groq import ChatGroq
import os
import re
from dotenv import load_dotenv
from get_outputs import generate_questions,get_output,summarise,getting_final_output,load_vector_store, llm, llm_8b

import warnings

warnings.filterwarnings("ignore")
load_dotenv()

groq=os.getenv('GROQ_API_KEY')


app = Flask(__name__)
app.secret_key = os.urandom(24)

def bold_stars(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

app.jinja_env.filters['bold_stars'] = bold_stars

@app.route("/", methods=["GET", "POST"])
def index():
  return render_template("index.html")

@app.route("/Gita", methods=["GET", "POST"])
def for_gita():
  question_list=[]
  if "gita_history" not in session:
    session["gita_history"] = []
  if request.method == "POST":
    question = request.form.get("question").lower()
    if not question:
       question="Default question: What is the Gita?"
    question_list.append(question)
    try:
      output=getting_final_output(question,"Gita_vectorstore","Gita_docstore","Gita_splitters")
      session["gita_history"].append({"question": question, "answer": output[-1]})
      session.modified = True
    except Exception as e:
      print(f"Error occurred while getting final output: {e}")
      return render_template("error.html")
  else:
    question = ""
    output = ""
  return render_template("Gita.html", data_list=session.get('gita_history', []))


@app.route("/Quran", methods=["GET", "POST"])
def for_quran():
  question_list=[]
  if "quran_history" not in session:
    session["quran_history"] = []
  if request.method == "POST":
    question = request.form.get("question").lower()
    if not question:
       question="Default question: What is the quran?"
    question_list.append(question)
    try:
      output = getting_final_output(question, "TheQuran_vectorstore", "TheQuran_docstore", "TheQuran_splitters")
      session["quran_history"].append({"question": question, "answer": output[-1]})
      session.modified = True 
    except Exception as e:

      print(f"Error occurred while getting final output: {e}")

      return render_template("error.html")
  else:
    question = ""
    output = ""
  return render_template("Quran.html",data_list=session.get('quran_history', []))

@app.route("/Bible", methods=["GET", "POST"])
def for_bible():
  question_list=[]
  if "bible_history" not in session:
    session["bible_history"] = []
  if request.method == "POST":
    question = request.form.get("question").lower()
    if not question:
       question="Default question: What is the quran?"
    question_list.append(question)
    try:
      output = getting_final_output(question, "TheBible_vectorstore", "TheBible_docstore", "TheBible_splitters")
      session["bible_history"].append({"question": question, "answer": output[-1]})
      session.modified = True 
    except Exception as e:
      print(f"Error occurred while getting final output: {e}")
      return render_template("error.html")
  else:
    question = ""
    output = ""
  return render_template("Bible.html",data_list=session.get('bible_history', []))

if __name__ == "__main__":
  app.run(debug=False)