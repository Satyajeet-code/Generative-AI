from flask import Flask, render_template, request, session
import os
import re
from get_outputs import getting_final_output

import warnings
warnings.filterwarnings("ignore")


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
      output=getting_final_output(question,"Gita_vectorstore","Gita_docstore","Gita_splitters", "The Gita")
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
      output = getting_final_output(question, "TheQuran_vectorstore", "TheQuran_docstore", "TheQuran_splitters", "The Quran")
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
      output = getting_final_output(question, "TheBible_vectorstore", "TheBible_docstore", "TheBible_splitters", "The Bible")
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
