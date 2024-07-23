from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import pickle
from flask import Flask, render_template, request
from langchain_groq import ChatGroq
import os
import re
from dotenv import load_dotenv
load_dotenv()

groq=os.getenv('GROQ_API_KEY')

with open("D:/Gita/TheGitaInaBox/Gita_vector.pkl", "rb") as f:
    vectorstore = pickle.load(f)


model=ChatGroq(groq_api_key=groq, model_name="Llama3-8b-8192")
# model=Ollama(model="llama3")
output_list=[]
question_list=[]
data_list=[]
def gita(question):
    prompt = ChatPromptTemplate.from_template("""
    Answer the following question based only on the provided context. 
    Think step by step before providing a detailed answer. Provide a detailed answer from the context. If the answer is not present in the context, simply say 'I don't know the answer' and nothing more. If the user asks a question with Can you? read carefully and answer. Start the answer directly and go as deep as possible into the context. Avoid answering in single sentences if the answer can be longer.
  
    <context>
    {context}
    </context>

    Question: {input}""")

    document_chain=create_stuff_documents_chain(model,prompt) 
    retriever=vectorstore.as_retriever() 
    retrieval_chain=create_retrieval_chain(retriever,document_chain)

    response=retrieval_chain.invoke({"input":question})
    print("------------------------- Answer ---------------------")
    print(response["answer"])

    output = response["answer"]
    output=output.replace("*","\n")
    
    output_list.append(output)

    return output_list[::-1]


app = Flask(__name__)

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
  app.run(debug=True)