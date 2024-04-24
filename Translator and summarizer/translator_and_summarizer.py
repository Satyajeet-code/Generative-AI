from pydub import AudioSegment
import whisper
import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# allow the loading of both OpenMP libraries
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

st.set_page_config(page_title="Translator and Summarizer")
st.header("Translator and Summarizer📝")


uploaded_file = st.file_uploader("Choose an audio or video file...", type=["mp4", "mp3"])
# image=""  

def final_model(file_name):
    print(" LLm using",file_name)
# loading the texts
    #     try:
    loader=TextLoader(f"{file_name}.txt")
    docs=loader.load()
    print("The document is: ")
    print(docs)

    db=FAISS.from_documents(docs,OllamaEmbeddings()) #generating vector embedding and creating FAISS index
#     except:
#         print("-----------------------------\nFile not found")
    try:
       
        llm=Ollama(model="llama2") # using the llama 2 model 
    except:
        print("-----------------------------\nThe model you are trying to use might not be present.\n to resolve this issue: \n 1) open command prompt \n type ollama run model_name.\n. I you get an error, try installing ollama")

# creating an instance of ChatPromptTemplate and giving it intructions on how to process the information provided
    prompt = ChatPromptTemplate.from_template("""
    Answer the following question based only on the provided context. 
    Do not include any other lines in the answer apart from the intended answer itself.
    <context>
    {context}
    </context>
    Question: {input}""")
# take a list of documents and format it into a prompt and pass to llm
    document_chain=create_stuff_documents_chain(llm,prompt) 
    retriever=db.as_retriever() # transforms the db object into a component usable within a retrieval chain.

    retrieval_chain=create_retrieval_chain(retriever,document_chain) #retriever to search the document store
    translation=retrieval_chain.invoke({"input":f"You are an expert at translating languages. Convert the given text into {lang} language without changing the meaning. Make sure ther is no english letters. Do not change the context of the text and double check to give only give translation in {lang} language"})
    print("-----------------------------\n")
    print("The document in Hindi:")
    print(translation['answer'])
    print("-----------------------------\n")
    print("length of doc: ",len(docs[0].page_content))

    response=retrieval_chain.invoke({"input":"Summarize the text and don't miss out on the key points. "})
    print("The summary:")
    print(response['answer'])
    print("-----------------------------\n")
    print("Thanks for using me")
    return translation['answer'],response['answer']
    

def save_as_txt(text,file_name):
    try:
        with open(f"{file_name}.txt", "w") as f:
      # Write the string to the file
          f.write(text)
          print("-----------------------------\n the text saved as a text file with name",file_name)
        f.close()
        
    except:
        print("-----------------------------\nthe file can't be saved as a text file")

def use_audio(file_name):
    print(file_name)
    if uploaded_file.name.split(".")[-1]!="mp3":
        file_name_mp3=file_name+".mp3"
    else:
        file_name_mp3=file_name
    whisper_model= whisper.load_model("base") #loading the base model from whisper
    audio=whisper.load_audio(file_name_mp3) # load the audio data
    audio=whisper.pad_or_trim(audio) # used to pad or trim the audio to a correct length for processing 
    log_mel=whisper.log_mel_spectrogram(audio).to(whisper_model.device) # transform into a mathematical representation
    _,probs=whisper_model.detect_language(log_mel) #a dictionary containing probabilities for different languages.
    print("The video is in:" ,max(probs,key=probs.get)," language") # language with the highest probability
    decoding_options=whisper.DecodingOptions()
    decoded_result=whisper.decode(whisper_model,log_mel,decoding_options) # the speech is converted to text
    text=decoded_result.text # extracts the text
    print("-----------------------------\nThe text extracted from the audio is:\n",text)
    save_as_txt(text,file_name) # saves with the file name
    trans, resp=final_model(file_name) # calls the final model
    return trans, resp
    
    
    
def extract_from_video(file_path):

    audio = AudioSegment.from_file(uploaded_file, format="mp4")    # Extract audio
    file_name=uploaded_file.name.split(".")[0] #save
    
    print("-----------------------------\nSaving audio file with name:",file_name)

    
    audio.export(f"{file_name}.mp3", format="mp3") # saving audio as mp3
    print("Exported: ",f"{file_name}.mp3")
    
    trans, resp=use_audio(f"{file_name}") # as the audio is now extracted, call use_audio
    return trans, resp

def main_func():
    file_extension = uploaded_file.name.split(".")[-1]
    print(file_extension)
    print(uploaded_file.name.split(".")[0])
    if file_extension=="mp4": #if it's a video call  extract_from_video() 
        trans, resp=extract_from_video(uploaded_file)
    elif file_extension=="mp3":
        trans, resp=use_audio(uploaded_file) #if it's a audio call  use_audio() 
    else:
        print("Only use .mp4 for videos and .mp3 for audio files")
    return trans, resp


lang = st.selectbox(
    "Select an option:",
    ("Spanish", "German", "Hindi")
)
submit=st.button("Submit")
# Display the selected option
st.write("You selected:", lang," language")


if submit:
    trans, resp=main_func()
    # st.image(uploaded_file)
    st.subheader("Translation:\n")
    st.write(trans)
    st.write("\n ------------------------ \n\n")
    st.subheader("Summary:\n")
    st.write(resp)
