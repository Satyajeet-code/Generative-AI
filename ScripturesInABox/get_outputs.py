from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pickle


import warnings
warnings.filterwarnings("ignore")

llm=ChatGroq(
     api_key="",
     #model='llama3-8b-8192',
     model='llama-3.1-70b-versatile',
     temperature=0.5
     #model='mixtral-8x7b-32768',
 )

llm_temp_0=ChatGroq(
     api_key="",
     #model='llama3-8b-8192',
     model='llama-3.1-70b-versatile',
     temperature=0
     #model='mixtral-8x7b-32768',
 )

llm_8b=ChatGroq(
     api_key="",
     #model='llama3-8b-8192',
     model='llama3-8b-8192',
     temperature=0
     #model='mixtral-8x7b-32768',
 )

def load_vector_store(vectorstore="Gita_vectorstore",docstore="Gita_docstore",splitters="Gita_splitters"):


    with open(f"static/{vectorstore}.pkl", "rb") as f:
        vectorstore = pickle.load(f)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    with open(f"static/{docstore}.pkl", "rb") as f:
        store = pickle.load(f)

    with open(f"static/{splitters}.pkl", "rb") as f:
        parent_splitter, child_splitter = pickle.load(f)


    big_chunks_retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    return big_chunks_retriever

def get_output(big_chunks_retriever,question,llm,):
    prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context. 
        Think step by step before providing a detailed answer. 
        Provide a detailed answer from the context. If the answer is not present in the context, simply say 'I don't know the answer' 
        and nothing more. 
        If the user asks a question with Can you? read carefully and answer. 
        Start the answer directly and go as deep as possible into the context. 
        Avoid answering in single sentences if the answer can be longer.
        <context>
        {context}
        </context>
        <Question> 
        {input}
        </Question>""")

    document_chain = create_stuff_documents_chain(llm, prompt)

    retrieval_chain = create_retrieval_chain(big_chunks_retriever, document_chain)

    response = retrieval_chain.invoke({"input": question})
            
    output = response["answer"]
    output = output.replace("*", "\n")

    return output

def generate_questions(question,llm, scripture_name):
    question_generation_prompt = """
    Generate 3 similar questions in context with {scripture_name} to the question given below. Make sure the generated questions cover multiple aspects of the question. The questions should be in lowercase.
    It is really important that the generated questions revolve around the asked question and take into account {scripture_name} and are very closely related to the asked question.
    <Question> 
    {question}
    </Question>
    Strictly follow the below syntax:
    <output_syntax>
    question1 || question2 || question3
    </output_syntax>

    <example>
    what are the key features and applications of langchain? || How does langchain differ from other large language model frameworks? || What are the potential benefits and limitations of using langchain for natural language processing tasks?
    </example>
    """

    prompt = PromptTemplate(input_variables=["question","scripture_name"], template=question_generation_prompt)
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    questions=llm_chain.run(question=question)
    all_questions=questions.split("||")[:3]
    all_questions.append(question)
    print("-------------- questions --------------")
    print(all_questions)
    print("-------------- questions --------------")
    return all_questions

def summarise(outputs,llm):
    summary_generation_prompt = """
    Provide a concise overview of the key points from the following context:
    <context> 
    {context}
    </context>
    Capture all important information without omitting any crucial details. Also provide a conclusion summarising the overview.
    
    <Example>
    **Arjuna's Reluctance to Fight in the Battle of Kurukshetra: A Summary of Key Points**
    
    **Introduction**

        Arjuna's decision not to fight in the Battle of Kurukshetra, as described in the context, is driven by multiple reasons, including his concern for the well-being of his kinsfolk and friends, his reverence for his elders, and his inner conflict between duty and morality.
    **Conclusion**

        Arjuna's reluctance to fight in the Battle of Kurukshetra is a result of his complex emotional and moral struggles. Through Krishna's guidance, Arjuna is able to overcome his doubts and fears, and ultimately rejoin the battle, driven by a sense of duty and purpose. This internal struggle reflects Arjuna's genuine desire to do the right thing and avoid causing harm to others, highlighting the sincerity of his moral dilemma.
    </Example>
    """

    prompt = PromptTemplate(input_variables=["context"], template=summary_generation_prompt)
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    summary=llm_chain.run(context=outputs)
    return summary

def getting_final_output(question,vectorstore,docstore,splitters,scripture_name):
  output_list=[]
  big_chunks_retriever=load_vector_store(vectorstore,docstore,splitters)
  all_questions=generate_questions(question,llm_8b,scripture_name)
  outputs=[]
  for que in all_questions:
      output=get_output(big_chunks_retriever,que,llm)
      outputs.append(output)
  summary=summarise(outputs,llm_temp_0)
  output_list.append(summary)
  

  return output_list
