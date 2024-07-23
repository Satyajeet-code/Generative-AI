from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai


from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
import os
import re
from dotenv import load_dotenv
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
groq=os.getenv('GROQ_API_KEY')
def qna_bot(url,question):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    text = re.sub(r"\n+", "\n", text)
    with open("text_file.txt", "w",encoding='utf-8') as f:
            f.write(text)
    f.close()

    loader=TextLoader("text_file.txt", encoding="utf-8")
    docs=loader.load()
    print("The document is: ")
    print(docs[0].page_content[:100])
    print("The length is: ")
    print(len(docs[0].page_content))


    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=60)
    docs=text_splitter.split_documents(docs)
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    db=FAISS.from_documents(docs,embeddings)

    
    llm=ChatGroq(groq_api_key=groq, model_name="Llama3-8b-8192")

    prompt = ChatPromptTemplate.from_template("""
    Answer the following question based only on the provided context. 
    Think step by step before providing a detailed answer. If the answer is not present in the context, simply say 'I don't know the answer' and nothing more.

    <context>
    {context}
    </context>

    Question: {input}""")

    document_chain=create_stuff_documents_chain(llm,prompt) 
    retriever=db.as_retriever() 
    retrieval_chain=create_retrieval_chain(retriever,document_chain)
    response=retrieval_chain.invoke({"input":question})
    print("------------------------- Answer ---------------------")
    print(response["answer"])

    output = response["answer"]
    output=output.replace("*","\n")
    return output
   

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    url = request.form.get("url")
    question = request.form.get("question")
    output=qna_bot(url,question)

  else:
    url = ""
    question = ""
    output = ""
  return render_template("index.html", url=url, question=question, output=output)

if __name__ == "__main__":
  app.run(debug=True)