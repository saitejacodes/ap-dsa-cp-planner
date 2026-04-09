import os
import sys


from dotenv import load_dotenv
load_dotenv()

required_envs = ["GROQ_API_KEY", "MONGO_URI", "GEMINI_API_KEY"]
missing_envs = [env for env in required_envs if not os.getenv(env)]

if missing_envs:
    print(f"CRITICAL ERROR: Missing environment variables: {', '.join(missing_envs)}")
    sys.exit(1)

import streamlit as st
st.set_page_config(page_title="DSA Planner",layout="wide",initial_sidebar_state="expanded")

if "user_id" not in st.session_state:
    st.session_state["user_id"]=None

st.title("DSA Planner")
st.write("Welcome to the AI-powered competitive programming planner.")
st.write("Please navigate to Home to onboard and initialize your data.")
st.sidebar.success("Select a page above.")
