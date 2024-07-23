# Alemeno Assignment for Internship – AI/ML

This repository contains the assignment given by Alemeno for internship – AI/ML

## Documentation:
The user can input one or more than one PDF files and then talk to the PDFs.
Using the PyPDF2 library, the text is extracted from the PDFs.
The text is then broken down into chunks of 1000 characters with an overlap of 200 characters using CharacterTextSplitter.
Then the embeddings are generated using GoogleGenerativeAIEmbeddings and a vector store is created using FAISS (Facebook AI Similarity Search).
Using the Ollama class llama3 is used as the LLM for this assignment.
A memory for the model is also created using ConversationBufferMemory.
And we create a conversation chain using ConversationalRetrievalChain which has the model, the memory and a retriever.
The UI is created using Streamlit where the user can enter questions and PDFs as the input and the responses from the LLM and the questions asked are displayed in the UI.

## Usage
1. Run `requirements.txt` to install the dependencies.

```bash
pip install -r requirements.txt
```
2. Execute `app.py` to open up the UI using the following command:

```bash
streamlit run app.py
```

## Screenshots:
![App Screenshot](https://github.com/Satyajeet-code/Generative-AI/blob/main/MultiPDFChat/Screenshot%202024-07-01%20192527.png)

In the above screenshot, the model performs the detailed analysis of the revenues

![App Screenshot](https://github.com/Satyajeet-code/Alemeno-assignment/blob/main/Alemeno/Screenshot%202024-07-01%20193902.png)

In the above screenshot the model answeres 2 questions. The questiuon related to Large Language Models is answered from the Google's pdf and the revenue of Tesla is answered from tesla's PDF.
