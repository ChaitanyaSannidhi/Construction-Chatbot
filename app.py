import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from db import init_db, save_message, get_history, clear_history

# ✅ Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Initialize DB
init_db()

# Choose a Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="SiteGenie", layout="centered")
st.title("🏗️ SiteGenie")
st.write("Ask me anything about **construction**. I will only answer construction-related queries.")

# Sidebar controls: Clear chat
if st.sidebar.button("🗑️ Clear Chat History"):
    clear_history()
    st.session_state["messages"] = [
        {"role": "system", "content": "You are an expert construction assistant. You will ONLY answer questions strictly related to construction, including materials, BOQ, codes, contracts, safety, construction methods, and project management. If a user asks anything unrelated to construction, you MUST reply exactly with: 'I can answer only construction-related queries.' Do NOT provide any other information."}
    ]
    st.stop()  # Stop execution so Streamlit reloads the app with cleared chat

# ✅ Load messages from DB if session_state is empty
if "messages" not in st.session_state:
    db_history = get_history()
    if db_history:
        st.session_state["messages"] = [{"role": role, "content": msg} for role, msg in db_history]
    else:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are an expert construction assistant. You will ONLY answer questions strictly related to construction, including materials, BOQ, codes, contracts, safety, construction methods, and project management. If a user asks anything unrelated to construction, you MUST reply exactly with: 'I can answer only construction-related queries.' Do NOT provide any other information."}
        ]

# ✅ Show chat history
for msg in st.session_state["messages"][1:]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# ✅ Chat input with construction-only enforcement
if user_input := st.chat_input("Type your construction query..."):
    st.session_state["messages"].append({"role": "user", "content": user_input})
    save_message("user", user_input)
    st.chat_message("user").markdown(user_input)

    user_input_clean = user_input.strip().lower()


    # Optional lightweight keyword filter
    construction_keywords = [
        "construction", "boq", "material", "cement", "steel",
        "building", "contract", "safety", "method", "site", "project"
    ]
    if not any(word in user_input.lower() for word in construction_keywords):
        reply = "I can answer only construction-related queries."
    
    if "who are you" in user_input_clean:
        reply = "I am a Chatbot designed by Chaitanya Sannidhi to answer your construction queries effectively."

    else:
        # Format conversation for Gemini
        conversation = "\n".join([
            f"{m['role'].capitalize()}: {m['content']}"
            for m in st.session_state["messages"]
        ])

        # Generate response from Gemini
        response = model.generate_content(conversation)
        reply = response.text

    st.session_state["messages"].append({"role": "assistant", "content": reply})
    save_message("assistant", reply)
    st.chat_message("assistant").markdown(reply)