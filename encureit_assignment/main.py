import os
from scrapper import scrape_data, save_text
from create_vectorstore import create_docs,create_vec_store
import requests
from links import get_urls
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from rag import generate_final_answer
from dotenv import load_dotenv
load_dotenv()

groq_api_key=os.getenv("GROQ_API_KEY")

# use llama 3.3 70 bas the LLM of choice
llm=ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

# scrape the data from the website and create the knowledge base if not present
if not os.path.isfile("BOM_scraped_content.txt"):
    print("-------------------- creating BOM_scraped_content --------------------")
    session = requests.Session()

    base_url,urls_to_scrape=get_urls()

    final_text=scrape_data(base_url,urls_to_scrape)
    save_text(final_text)


# Initialize the embedding model

embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",  
            model_kwargs={'device': 'cpu'}
        )

# try to get the FAISS index if not create the vectorstore
try:
    
    vectorstore = FAISS.load_local("BOM_faiss_index", embedding_model,allow_dangerous_deserialization=True)
    print("-------------------- Vector store exits --------------------")

except:
    print("-------------------- creating Vector store --------------------")
    with open("BOM_scraped_content.txt", "r", encoding="utf-8") as f:
        markdown_text = f.read()
    
    documents = create_docs(markdown_text)

    vectorstore = create_vec_store(documents, embedding_model)

# Get the query from the user and generate the final answer, if the user types bye, exit from the loop
query=""
while True:
    query = input("Enter your query related to loans from bank of Maharastra. Type bye to exit: ")
    if query.lower() == "bye":
        print("Bye. Have a great day.")
        break  

    result,formatted_source=generate_final_answer(query, llm, vectorstore)

    print("\n" +query +"\n")
    print(result+"\n ")
    print("Source: " + formatted_source+"\n------------------------------------------------------------------- \n\n")
    