import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain import LLMChain
from langchain.prompts import PromptTemplate

import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import numpy as np
import json

import re
import os

llm=ChatGroq(
     api_key="",
     #model='llama3-8b-8192',
     model='llama-3.1-70b-versatile',
     temperature=0.0
     #model='mixtral-8x7b-32768',
 )

# setting seed to get consistent speech
ranveer_seed = 42
laura_seed = 43
default_seed = 44

def get_results(docs):
    prompt = """
        Below is a document segment for a podcast-like conversation between Ranveer and Laura about language models.

        <document>
        {document}
        </document>

        <iteration>
        {iteration}
        </iteration>

        <final_iteration>
        {final_iteration}
        </final_iteration>

        IMPORTANT RULES:
        1. ONLY for Iteration 1:
        - Start with a brief greeting and introduction
        - Use the format: "Iteration 1\n\nRanveer: Welcome to our podcast..."
        2. For ALL other iterations (2 and above):
        - DO NOT include any greetings or introductions
        - Start directly with the iteration number, then continue the conversation
        - Use the format: "Iteration [number]\n\nRanveer: Continuing our discussion..."
        3. Only include an ending note if the current iteration equals the final iteration.
        4. Maintain continuity between iterations as if it's one ongoing discussion.
        5. Derive all conversation content from the given document segment.

        <Output format>
        Iteration {iteration}

        Ranveer: [statement]

        Laura: [statement]

        [Continue alternating between Ranveer and Laura]
        </Output format>

        Now, create the conversation segment for Iteration {iteration} based on the document and rules above.
        """
    results = []
    prompt = PromptTemplate(input_variables=["document","iteration","final_iteration"], template=prompt)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    iteration=0
    for doc in docs:
        iteration=iteration+1
        result=llm_chain.run(document=doc,iteration=iteration,final_iteration=len(docs))
        results.append(result)
    print("------------------------ Got results")
    return results



def preprocess(results):
    new_conv=[]
    for res in results:
        conversation = re.findall(r'(Ranveer:.*|Laura:.*)', res)
        for conv in conversation:
            new_conv.append(tuple(conv.split(":")))
    print("------------------------ Got Ranveer Laura")
    with open('new_conv.json', 'w') as file:
        json.dump(new_conv, file)
    return new_conv

def generate_speech(tokenizer,model,text, description,seed):
    torch.manual_seed(seed) 
    input_ids = tokenizer(description, return_tensors="pt").input_ids
    prompt_input_ids = tokenizer(text, return_tensors="pt").input_ids

    with torch.no_grad():
        generation = model.generate(
            input_ids=input_ids,
            prompt_input_ids=prompt_input_ids
        )
    audio_arr = generation.cpu().numpy().squeeze()
    print("------------------------ ran generate_speech")
    return audio_arr


    
def generate_voice(new_conv,podcast_name):
    model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-v1")
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")



    ranveer_description = "Jon's voice is mild and friendly, with a british accent. It's a studio quality sound and there is no background noise"
    laura_description = "Laura's voice is energetic, curious and friendly, with a british accent.It's a studio quality sound and there is no background noise"
    all_segments = []

    for speaker_text in new_conv[0:2]:
        if speaker_text[0].strip() == "Ranveer":
            text = " ".join(speaker_text[1:])
            audio = generate_speech(tokenizer,model,text,ranveer_description,ranveer_seed)
        elif speaker_text[0].strip() == "Laura":
            text = " ".join(speaker_text[1:])
            audio = generate_speech(tokenizer,model,text, laura_description,laura_seed)
        else:
            # adding a neutral voice for any other speaker
            text = " ".join(speaker_text[1:])
            default_description = "A neutral voice with slight Indian accent. There is no background noise"
            audio = generate_speech(tokenizer,model,text, default_description,default_seed)
        
        all_segments.append(audio)
        
        # adding a short pause of 0.5 seconds between speakers
        pause = np.zeros(int(0.5 * model.config.sampling_rate))
        all_segments.append(pause)

    full_conversation = np.concatenate(all_segments)

    voice_folder = 'static/voice'
    os.makedirs(voice_folder, exist_ok=True)
    output_path = os.path.join(voice_folder, f"{podcast_name}.wav")
    sf.write(output_path, full_conversation, model.config.sampling_rate)

    print(f"Conversation saved as {podcast_name}.wav")

def read_and_chunking(filename):
    text=""
    pdf_reader=PyPDF2.PdfReader(f"static/uploads/{filename}")
    for page in pdf_reader.pages:
        text+=page.extract_text()
    text=text.replace("\t", " ")
    text=text.replace("\n", " ")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=100,
        chunk_overlap=0
    )
    docs = text_splitter.create_documents([text])
    print("--------------------- docs ---------------------  ")
    print(docs)
    print("--------------------- docs ---------------------  ")
    print("------------------------ Got chunks")
    return docs

def get_final_results(filename,podcast_name):
    docs=read_and_chunking(filename)
    results=get_results(docs)
    new_conv=preprocess(results)
    generate_voice(new_conv,podcast_name)
