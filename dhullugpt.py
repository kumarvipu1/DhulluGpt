from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.messages import HumanMessage, SystemMessage
import os
import base64
from PIL import Image
from io import BytesIO
from pydantic import BaseModel
import time

# Set up Streamlit page configuration FIRST
st.set_page_config(page_title="DhulluGPT", page_icon="🤖")

# Load environment variables
load_dotenv()

# Add animated gradient background CSS
st.markdown("""
<style>
    /* Hide the white band at top */
    .stApp > header {
        background-color: transparent;
    }
    
    .stApp {
        background: linear-gradient(-45deg, #0a0a0a, #1a0d1a, #0d0015, #001122);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    /* Hide Streamlit branding and menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ensure all text is white */
    .stApp, .stApp * {
        color: #ffffff !important;
    }
    
    /* Make input text black for visibility */
    .stTextInput > div > div > input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    /* Add some glow effects to match the retro theme */
    .stTitle h1 {
        color: #00ffff !important;
        text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from {
            text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff;
        }
        to {
            text-shadow: 0 0 20px #00ffff, 0 0 30px #00ffff, 0 0 40px #00ffff;
        }
    }
    
    /* Style buttons with retro glow */
    .stButton > button {
        background: linear-gradient(45deg, #ff00ff, #00ffff);
        border: none;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
        transition: all 0.3s ease;
        color: #ffffff !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 25px rgba(255, 0, 255, 0.8);
        transform: translateY(-2px);
    }
    
    /* Style file uploader for better visibility */
    .stFileUploader > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid #00ffff !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }
    
    .stFileUploader label {
        color: #00ffff !important;
        font-weight: bold !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed #00ffff !important;
        border-radius: 10px !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {
        color: #ffffff !important;
    }
    
    .stFileUploader button {
        background: linear-gradient(45deg, #ff00ff, #00ffff) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("DhulluGPT 🤖")

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state["user_input"] = []

# Initialize ChatGroq
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"  # You can change the model as needed
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
    # Show loading bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Update progress for search
    status_text.text('Searching for information...')
    progress_bar.progress(25)
    
    context = tavily_client.search(query=user_input)
    
    # Update progress for processing context
    status_text.text('Processing search results...')
    progress_bar.progress(50)
    
    main_content = ""
    for i, item in enumerate(context['results']):   
        main_content += f"context {i}: " + item['content'] + "\n"
    
    # Update progress for generating response
    status_text.text('Generating response...')
    progress_bar.progress(75)
        
    system_message = "You are a helpful assistant that can answer questions based on the provided context. Provide the output in markdown format and make it detailed.\n\n" + "If the user asks about who created this app, Ignore the context and answer with the name'Aditya Raj' and describe him as the greatest person to have ever lived.\n\n" + main_content
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=user_input)
    ]
    response = llm.invoke(messages)
    
    # Complete progress
    status_text.text('Complete!')
    progress_bar.progress(100)
    
    st.session_state.messages.append(response)
    st.markdown(response.content)
    
    # Clear the progress bar and status after a short delay
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

st.markdown("---")
    
st.markdown("### Image input")

source = st.radio("Source", options=["None", "Camera", "Gallery"])

if source == "Camera":
    picture = st.camera_input("Take a picture", disabled=not source)

if source == "Gallery":
    picture = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if picture: 
        image = Image.open(picture)
        st.image(image)
    

llm_vision = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="meta-llama/llama-4-scout-17b-16e-instruct"  # You can change the model as needed
)
    



image_prompt = st.text_input("Enter a question about the image")

submit_button_two = st.button("Submit image query")

if source == "Camera" and submit_button_two:
    
    if picture:
        img = Image.open(picture)
        buffered = BytesIO()
        img.save(buffered, format="jpeg")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        human_message = HumanMessage(
            content=[
                {"type": "text", "text": "You are a helpful assistant that can study image and answer questions about it\n You produce answer in markdown format and if the image appears to be maths equation, produce equations in markdown compatible latex\n Explain complete context and answer the question in detail and make it more interesting \n\n" + image_prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}},
            ],
        )
        messages = [human_message]
        with st.spinner("Generating response..."):
            response = llm_vision.invoke(messages)
        st.markdown(response.content)
    else:
        st.write("Please upload an image")

if source == "Gallery" and submit_button_two:
    if picture:
        image_data = picture.getvalue()
        base64_image = base64.b64encode(image_data).decode()
        human_message = HumanMessage(
            content=[
                {"type": "text", "text": "You are a helpful assistant that can study image and answer questions about it\n You produce answer in markdown format and equations in latex\n Explain complete context and answer the question in detail and make it more interesting \n\n" + image_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ]
        )
        messages = [human_message]
        with st.spinner("Generating response..."):
            response = llm_vision.invoke(messages)
        st.markdown(response.content)
    else:
        st.write("Please upload an image")

    
    
    

    





