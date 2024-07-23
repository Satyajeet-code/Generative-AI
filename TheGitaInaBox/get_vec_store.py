from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import pickle
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

text=""
pdf_reader=PdfReader("Bhagavad-Gita As It Is (Original 1972 Edition).pdf")
for page in pdf_reader.pages:
    text+=page.extract_text()
with open("text_file.txt","w",encoding="utf-8") as f:
    f.write(text)
f.close()
print("------------------------ File saved")

text_splitter = RecursiveCharacterTextSplitter(
    separators=['\n\n', '\n', '.', ','],
    chunk_size=1000,
    chunk_overlap=200
)
docs = text_splitter.split_text(text)
print("------------------------ Splitted")
embeddings = embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
vectorstore = FAISS.from_texts(docs,embeddings)
print("------------------------ Got vectors")

with open("Gita_vector.pkl", "wb") as f:
    pickle.dump(vectorstore, f)
