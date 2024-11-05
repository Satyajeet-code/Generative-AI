
import PyPDF2
import pickle
from langchain.vectorstores import FAISS
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import google.generativeai as genai
import os
load_dotenv()
import warnings
warnings.filterwarnings("ignore")
# os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# from dotenv import load_dotenv
from win32com.client import Dispatch
from langchain.retrievers import ParentDocumentRetriever
from langchain_core.documents import Document

text=""
file_path="D:/setups/Oxford-Quran-Translation.pdf"
pdf_reader=PyPDF2.PdfReader(file_path)
for page in pdf_reader.pages:
    text+=page.extract_text()
with open("Bible_text_files.txt","w",encoding="utf-8") as f:
    f.write(text)
f.close()
# print("------------------------ File saved")
# print (len(text))
with open("Bible_text_file.txt", "r", encoding="utf-8") as f:
    text = f.read()

print(text[:100])
text = text.replace("\t", " ").replace("\n", " ")
text=text.lower()

# This text splitter is used to create the parent documents - The big chunks
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

# This text splitter is used to create the child documents - The small chunks
# It should create documents smaller than the parent
child_splitter = RecursiveCharacterTextSplitter(chunk_size=500)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = FAISS.from_documents([Document(page_content="demo")], embeddings)
store = InMemoryStore()

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

big_chunks_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
doc = Document(page_content=text)
big_chunks_retriever.add_documents([doc])

# Save the vectorstore
# vectorstore.save_local("Gita_vectorstore")

with open("static/TheBible_vectorstore.pkl", "wb") as f:
    pickle.dump(vectorstore, f)
    

# Save the docstore
with open("static/TheBible_docstore.pkl", "wb") as f:
    pickle.dump(store, f)

# Save the splitters
with open("static/TheBible_splitters.pkl", "wb") as f:
    pickle.dump((parent_splitter, child_splitter), f)