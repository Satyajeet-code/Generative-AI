from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

# create documents using both MarkdownHeaderTextSplitter and RecursiveCharacterTextSplitter
def create_docs(markdown_text):


    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "section")
    ])


    md_docs = md_splitter.split_text(markdown_text)

    char_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
    documents = []
    for doc in md_docs:
        chunks = char_splitter.create_documents([doc.page_content], metadatas=[doc.metadata])
        documents.extend(chunks)

    return documents

# create emneddings and store them in a vectorstore
def create_vec_store(documents, embedding_model):

    vectorstore = FAISS.from_documents(documents, embedding_model)

    vectorstore.save_local("BOM_faiss_index")
    return vectorstore