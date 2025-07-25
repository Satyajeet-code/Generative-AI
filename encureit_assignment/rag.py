from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

# format docs creates a paragraph
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# the main function that runs to get the final answer
def generate_final_answer(query, llm, vectorstore):

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_template("""
    Answer the question based on the following context:

    Context: {context}

    Question: {question}
  Your answer should be well formatted. Use a) b) c) format and paragraphs to make the answer more readable.
                                              
    Answer:
    """)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


    response = chain.invoke(query)


    source_docs = retriever.invoke(query)
 

    source_sections = set()
    for res in source_docs:
        section = res.metadata.get("section", "").strip()
        source_sections.add(section)
    formatted_source = ", ".join(source_sections)


    return response, formatted_source