from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import pickle
from langchain.vectorstores import FAISS
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from flask import Flask, render_template, request
from langchain_groq import ChatGroq
import os
import re
from dotenv import load_dotenv
from get_outputs import generate_questions,get_output,summarise
load_dotenv()

groq=os.getenv('GROQ_API_KEY')

with open("static/Gita_vectorstore.pkl", "rb") as f:
    vectorstore = pickle.load(f)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Load the vectorstore
# vectorstore = FAISS.load_local("Gita_vectorstore", embeddings,allow_dangerous_deserialization=True)

# Load the docstore
with open("static/Gita_docstore.pkl", "rb") as f:
    store = pickle.load(f)

# Load the splitters
with open("static/Gita_splitters.pkl", "rb") as f:
    parent_splitter, child_splitter = pickle.load(f)


big_chunks_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# model=ChatGroq(groq_api_key=groq, model_name="Llama3-8b-8192")
llm=ChatGroq(
     api_key="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",
     #model='llama3-8b-8192',
     model='llama-3.1-70b-versatile',
     temperature=1
     #model='mixtral-8x7b-32768',
 )
# model=Ollama(model="llama3")
output_list=[]
question_list=[]
data_list=[]

# file_path=input("Enter the file path: ")
def gita(question):
  all_questions=generate_questions(question,llm)
  outputs=[]
  for que in all_questions:
      output=get_output(big_chunks_retriever,que,llm)
      outputs.append(output)
  summary=summarise(outputs,llm)
  print("----------------------------------------------------------")
  print(summary)
  output_list.append(summary)
  conclusion=summary.split("**Conclusion**")[-1]

  return output_list[::-1]
# print("-------------------------------------------------------------")


# app = Flask(__name__)

app = Flask(__name__)

def bold_stars(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

app.jinja_env.filters['bold_stars'] = bold_stars

@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    question = request.form.get("question")
    if not question:
       question="Default question: What is the Gita?"
    question_list.append(question)
    output=gita(question)
    data_list = list(zip(question_list, output_list))
  else:
    question = ""
    output = ""
    data_list=[]
  return render_template("index.html",data_list=data_list)

if __name__ == "__main__":
  app.run(debug=False)