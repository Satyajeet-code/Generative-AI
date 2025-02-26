from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END

from langchain.vectorstores.faiss import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain_groq import ChatGroq
import faiss, pickle
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

google_api_key=os.getenv("GOOGLE_API_KEY")
groq_api_key=os.getenv("GROQ_API_KEY")
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("Faith based AI Assistant 🤲📿✝️")

question = st.text_input("Ask a question about the Gita, Quran and Bible:", "")



embeddings=GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=google_api_key)

combined_index = faiss.read_index("combined_vectors/index.faiss")
with open("combined_vectors/index.pkl", "rb") as f:
    combined_metadata = pickle.load(f)

gita_index= faiss.read_index("single_vectors/gita/index.faiss")
with open("single_vectors/gita/index.pkl", "rb") as f:
    gita_metadata = pickle.load(f)


bible_index = faiss.read_index("single_vectors/bible/index.faiss")
with open("single_vectors/bible/index.pkl", "rb") as f:
    bible_metadata = pickle.load(f)


quran_index = faiss.read_index("single_vectors/quran/index.faiss")
with open("single_vectors/quran/index.pkl", "rb") as f:
   quran_metadata = pickle.load(f)


retriever = FAISS(
    index=combined_index,
    docstore=combined_metadata[0],  
    index_to_docstore_id=combined_metadata[1],  
    embedding_function=embeddings
).as_retriever()

gita_retriever = FAISS(
    index=gita_index,
    docstore=gita_metadata[0],  
    index_to_docstore_id=gita_metadata[1],  
    embedding_function=embeddings
).as_retriever()

bible_retriever = FAISS(
    index=bible_index,
    docstore=bible_metadata[0],  
    index_to_docstore_id=bible_metadata[1], 
    embedding_function=embeddings
).as_retriever()

quran_retriever = FAISS(
    index=quran_index,
    docstore=quran_metadata[0],  
    index_to_docstore_id=quran_metadata[1],  
    embedding_function=embeddings
).as_retriever()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


llm = ChatGroq(
    api_key=groq_api_key,
    model='llama-3.3-70b-versatile',
    temperature=0
)



def function_1(state):
    global message
    message=state["messages"]
    question=message[-1]
    print(question)
    
    template="""
    
    <Instructions>
    From the question You need to figure out if the user wants to get answer from The Gita, The Quran or The Bible or from all of three. 
    Your task is to classify the given user query into one of the following categories: [Gita, Quran, Bible, Mix]. 
    General question like I am sad or I am feeling depressed, I need to get work done are something that require answer from all of three and should be classified as Mix.
    Only respond with the category name and nothing else.
    </Instructions>
    
    <question>
    {question}
    </question>
    
    """
    
    prompt = PromptTemplate(template=template,
                                    input_variables=[question]                                
                                    )
    chain =  prompt | llm 
    
    response = chain.invoke({"question":question})


    return {"messages": [response.content]}

def router(state):
    print('-> Router ->')
    
    messages = state["messages"]
    last_message = messages[-1]
    print(last_message)
    if 'mix' in last_message.lower():
        return 'combined'
    elif "gita" in last_message.lower():
        return 'Gita'
    elif "quran" in last_message.lower():
        return 'Quran'
    else:
        return 'Bible'
    
def get_results(state, retriever, source_name):
    messages = state['messages']
    question = messages[0]  
    print(f'-> Fetching results from {source_name} ->')
    print(question)
    
    template = """
    Answer the following question based only on the provided context.
    Think step by step before providing a detailed answer. Provide a detailed answer from the context.
    If the answer is not present in the context, simply say 'I don't know the answer' and nothing more.
    If the user asks a question with 'Can you?', read carefully and answer.
    Start the answer directly and go as deep as possible into the context. Avoid answering in single sentences if the answer can be longer.
    
    <context>
    {context}
    </context>
    
    Question: {input}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    response = retrieval_chain.invoke({"input": question})
    
    sources_text = source_name.replace("The","")
    if sources_text=="Multiple Sources":
        source_files = {doc.metadata["source"] for doc in response["context"]}
        sources_text = ", ".join(source_files) if source_files else "No sources available"
        result= response["answer"]+"\n"+" |  "+ sources_text.title()
    else:  
        result = response["answer"] + "\n" + " |  " + sources_text
    return {"messages": [result]}


def get_combined_results(state):
    return get_results(state, retriever, "Multiple Sources")

def get_gita_results(state):
    return get_results(state, gita_retriever, "The Gita")

def get_quran_results(state):
    return get_results(state, quran_retriever, "The Quran")

def get_bible_results(state):
    return get_results(state, bible_retriever, "The Bible")



workflows = StateGraph(AgentState)

workflows.add_node("Router", function_1)
workflows.add_node("Combined_results", get_combined_results)
workflows.add_node("Gita_results", get_gita_results)
workflows.add_node("Quran_results", get_quran_results)
workflows.add_node("Bible_results", get_bible_results)

workflows.set_entry_point("Router")

workflows.add_conditional_edges(
    "Router",
    router,
    {
        "combined": "Combined_results",
        "Gita": "Gita_results",
        "Quran": "Quran_results",
        "Bible": "Bible_results",
    }
)

workflows.add_edge("Combined_results", END)
workflows.add_edge("Gita_results", END)
workflows.add_edge("Quran_results", END)
workflows.add_edge("Bible_results", END)

app = workflows.compile()
if st.button("Submit") and question:
    inputs = {"messages": [question]}

    output = app.invoke(inputs)
    answer= output["messages"][-1].split("|")[0]
    sources=output["messages"][-1].split("|")[-1]
    st.session_state.history.append((question, answer))
    st.subheader("Response:")
    st.write(answer)
    st.markdown(f"**Sources:**")
    st.write(sources)
if st.session_state.history:
    with st.expander("History"):
        for q, r in st.session_state.history:
            st.markdown(f"**Q:** {q}")
            st.markdown(f"**A:** {r}")
            st.markdown("---")
