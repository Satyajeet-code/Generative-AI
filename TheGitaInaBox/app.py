import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from border import border_style
from langchain_groq import ChatGroq
import pickle

from langchain_groq import ChatGroq

groq="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"


with open("TheGitaInaBox/vector_index.pkl", "rb") as f:
    vectorstore = pickle.load(f)
st.markdown(border_style, unsafe_allow_html=True)
st.header("The Gita in a Box 📿")

model=ChatGroq(groq_api_key=groq, model_name="Llama3-8b-8192")


prompt = ChatPromptTemplate.from_template("""
Answer the following question based only on the provided context. 
Think step by step before providing a detailed answer. If the answer is not present in the context, simply say 'I don't know the answer' and nothing more. If the user asks a question with Can you? read carefully and answer.

<context>
{context}
</context>

Question: {input}""")

document_chain=create_stuff_documents_chain(model,prompt) 
retriever=vectorstore.as_retriever() 
retrieval_chain=create_retrieval_chain(retriever,document_chain)
question=st.text_input("Ask a Question about the Bhagwad Gita")
response=retrieval_chain.invoke({"input":question})
print("------------------------- Answer ---------------------")
print(response["answer"])

output = response["answer"]
output=output.replace("*","\n")

if st.button("Get Answer"):
    if output and question:
        st.write(f"User:<div class='stWriteWithBorder'>{question}</div>", unsafe_allow_html=True)
    
        st.write(f"Bot:<div class='stWriteWithBorder'>{output}</div>", unsafe_allow_html=True)

