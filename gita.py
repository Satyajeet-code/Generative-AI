from get_outputs import generate_questions,get_output,summarise
from langchain_groq import ChatGroq
import os
import re
from dotenv import load_dotenv
from langchain.vectorstores import FAISS
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pickle

llm=ChatGroq(
     api_key="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",
     #model='llama3-8b-8192',
     model='llama-3.1-70b-versatile',
     temperature=1
     #model='mixtral-8x7b-32768',
 )

llm_8b=ChatGroq(
     api_key="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",
     #model='llama3-8b-8192',
     model='llama3-8b-8192',
     temperature=0
     #model='mixtral-8x7b-32768',
 )

def load_vector_store(vectorstore="Gita_vectorstore",docstore="Gita_docstore",splitters="Gita_splitters"):


    with open(f"static/{vectorstore}.pkl", "rb") as f:
        vectorstore = pickle.load(f)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Load the vectorstore
    # vectorstore = FAISS.load_local("Gita_vectorstore", embeddings,allow_dangerous_deserialization=True)

    # Load the docstore
    with open(f"static/{docstore}.pkl", "rb") as f:
        store = pickle.load(f)

    # Load the splitters
    with open(f"static/{splitters}.pkl", "rb") as f:
        parent_splitter, child_splitter = pickle.load(f)


    big_chunks_retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    return big_chunks_retriever



# file_path=input("Enter the file path: ")
def getting_final_output(question,vectorstore,docstore,splitters):
  output_list=[]
  big_chunks_retriever=load_vector_store(vectorstore,docstore,splitters)
  all_questions=generate_questions(question,llm_8b)
  outputs=[]
  for que in all_questions:
      output=get_output(big_chunks_retriever,que,llm)
      outputs.append(output)
  summary=summarise(outputs,llm)
  # print("----------------------------------------------------------")
  # print(summary)
  # print("----------------------------------------------------------")
  output_list.append(summary)
  

  return output_list