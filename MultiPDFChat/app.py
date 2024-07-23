# importing all the necessary libraries
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from border import border_style
from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain 
from dotenv import load_dotenv

# getting the Google's api key (used for embeddings)
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Extracting texts from PDFs and creating a text file out of it.
def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
        with open("text_file.txt", "w",encoding='utf-8') as f:
            f.write(text)
        f.close()
    return  text


# Using CharacterTextSplitter to split the texts into chunks with a chunk size of 1000 and chucnk overlap of 200
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Creating a vector store using FAISS and vector embedding using GoogleGenerativeAIEmbeddings
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

# Initializing the llama3 model, creating the memory and conversation chain
def get_conversational_chain(vectorstore):

    model=Ollama(model="llama3")

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

# Displaying the user input and llm's responses
def display_texts(user_question):
    print(user_question)
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i%2!=0:
            st.write(f"Bot:<div class='stWriteWithBorder'>{message.content}</div>", unsafe_allow_html=True)
        else:
            st.write(f" User: <div class='stWriteWithBorder'>{message.content}</div>", unsafe_allow_html=True)




# Putting everything together in the main function. This involves creting the streamlit sodebar where the user would input the files, taking input from the user, calling the functions to process the texts.
def main():
    st.markdown(border_style, unsafe_allow_html=True)
    st.header("Talk PDF")
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    user_question = st.text_input("Ask a Question from the PDF Files")

    if user_question:
        display_texts(user_question)

    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files ", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                
                print("---------------------------------------------------------------------------------\n The raw text is:",raw_text[:1000])
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vector_store(text_chunks)
                st.session_state.conversation = get_conversational_chain(
                    vectorstore)
                st.success("Done")



if __name__ == "__main__":
    main()