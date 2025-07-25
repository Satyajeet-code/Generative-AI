# Project Setup

## Clone the repository
    git clone https://github.com/satyajeet-code/bom-loan-rag.git
    cd bom-loan-rag

## Install dependencies
    pip install -r requirements.txt

## Run the file


    1. Open a terminal (PowerShell or CMD).

    2. Run the following command (update the path if different):

        & C:\Users\ASUS\AppData\Local\Programs\Python\Python313\python.exe c:/Users/ASUS/encureit_assignment/main.py

# Architectural Decisions:
## Libraries:
### 1) requests
Used to send HTTP GET requests to fetch webpage content.

### 2)beautifulsoup4 (bs4)
It is one of the instry standard libraries that makes it easy to parse HTML and extracts content from complex page structures.

I used it to clean up scripts, headers, navbars, and focus only on the article or main sections of the pages.

### 3) LangChain
LangChain provides almost everything I need from vectorstores to splitters to tools and makes it really easy for product development. 
I have hands on experience with LangChain for more than a year now.

## Data Strategy:

### 1) MarkdownHeaderTextSplitter 
I structured the data as a heading paragraph structure where each loan wa sthe heading and respective paragraphs contained the details about the loan.
This way it was very easy to naviagte to the correct loan type and get the source as well.
MarkdownHeaderTextSplitter  helps retain hierarchy by splitting content based on markdown-style headers.

### 2) RecursiveCharacterTextSplitter 
Then I split the documents into with a length of around 2000 characters with an overlap of 300 charcters. So that each chunk will have some data from previous chunk and this helps the model retain context between chunks. 

RecursiveCharacterTextSplitter ensures documents are split into overlapping chunks to preserve context for RAG.

### 3) Vectorstore: FAISS 
FAISS is a lightweight, fast vector similarity search library used to store and retrieve embedded document chunks efficiently.
It stores vectors locally. 

## Model Selection:
### 1) Embedding mode: all-mpnet-base-v2

all-mpnet-base-v2 is a model that creates vectors of dimensions 768.
It is a bit slower (but it does not bother much) as compared to all-MiniLM-L6-v2 but all-MiniLM-L6-v2 creates vectors of dimensions 384 and did not work great for this assignment.
I found all-mpnet-base-v2 to be very accurate.
I would have gone with models that generate higher dimensional vectors if my laptop was more powerful.

### 2) LLM: llama-3.3-70b-versatile

I went with Llama 3.3 70b  (using Groq) becuase it was producing accurate outputs 10/10 times.
I also tried other models like Llama 3.1 70B, but it missed my instructions 1/10 times.

## Challenges Faced:

The primary challange was to gather the data. Things were smooth after that. 
I had to think how should I proceed.
I had to properly research about bank of Maharastra's loans and their respective URLs.
I had to pick the type of loans as well.
I firstly thought to create an automatio system, but that would take time, so I gathered links amnually.

## Potential Improvements:

If I had more time I would have dived one level deeper into the loans. 
I would have dived deeper into types of car loan loan like loan for old cars, loan for two wheeler etc.
I would tried different vectorstores, different data formats, chunking strategies, LLMs and prompts.
I would have integrated a EMI calculator as well, maybe as a tool that the LLm can use. 
