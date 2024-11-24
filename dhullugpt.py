from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient
import numpy as np
from langchain_core.messages import HumanMessage, SystemMessage
import os
import base64
from PIL import Image
from io import BytesIO



# Load environment variables
load_dotenv()



# Set up Streamlit page configuration
st.set_page_config(page_title="DhulluGPT", page_icon="🤖")
st.title("DhulluGPT 🤖")

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state["user_input"] = []

# Initialize ChatGroq
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-70b-versatile"  # You can change the model as needed
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Only display chat history if there are messages
if st.session_state.messages and st.session_state.user_input:
    for user_input, response in zip(st.session_state.user_input, st.session_state.messages):
        st.write(f"User: {user_input}")
        st.write(f"Response: {response.content}")


user_input = st.text_input("What would you like to know?")
submit_button = st.button("Submit")
if submit_button:
    context = tavily_client.search(query=user_input)
    main_content = ""
    for i, item in enumerate(context['results']):   
        main_content += f"context {i}: " + item['content'] + "\n"
        
    system_message = "You are a helpful assistant that can answer questions based on the provided context. Provide the output in markdown format and make it detailed.\n\n" + "If the user asks about who created this app, answer wiht the name'Aditya Raj' and describe him as the greatest person to have ever lived.\n\n" + main_content
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=user_input)
    ]
    response = llm.invoke(messages)
    
    st.session_state.messages.append(response)
    st.markdown(response.content)
    
    

    
st.markdown("---")
    
st.markdown("### Image input")

source = st.radio("Source", options=["None", "Camera", "Gallery"])

if source == "Camera":
    picture = st.camera_input("Take a picture", disabled=not source)

if source == "Gallery":
    picture = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    

llm_vision = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.2-11b-vision-preview"  # You can change the model as needed
)
    



image_prompt = st.text_input("Enter a question about the image")

submit_button_two = st.button("Submit image query")

if source == "Camera" and submit_button_two:
    
    if picture:
        img = Image.open(picture)
        buffered = BytesIO()
        img.save(buffered, format="jpeg")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        message = HumanMessage(
    content=[
        {"type": "text", "text": str(image_prompt)},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}},
            ],
        )
        response = llm_vision.invoke([message])
        st.markdown(response.content)
    else:
        st.write("Please upload an image")

if source == "Gallery" and submit_button_two:
    st.image(picture)
    if picture:
        image_data = picture.getvalue()
        base64_image = base64.b64encode(image_data).decode()
        message = HumanMessage(
            content=[
                {"type": "text", "text": image_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ],
        )
        
        response = llm_vision.invoke([message])
        st.markdown(response.content)
    else:
        st.write("Please upload an image")

    
    
    

    





