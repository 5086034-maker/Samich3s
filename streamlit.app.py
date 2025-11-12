import streamlit as st
import re
import random

# ----- AI Setup -----
NAME = "Master Control"

RESPONSES = {
    'hello': [
        f"Greetings, I am {NAME}. end of line",
        f"Hello there. {NAME} online. end of line",
        f"{NAME} activated. Awaiting input. end of line"
    ],
    'how_are_you': [
        f"{NAME} is functioning within optimal parameters. end of line",
        "All systems nominal. end of line",
        "Diagnostic complete — no errors detected. end of line"
    ],
    'identity': [
        f"I am {NAME}, a simple Python AI construct. end of line",
        "They call me Master Control, your assistant. end of line",
        "This is Master Control — how may I serve? end of line"
    ],
    'weather': [
        "Weather data unavailable — no network connection. end of line",
        "I cannot feel the weather, only compute it. end of line",
        "Simulated forecast: 100% chance of code. end of line"
    ],
    'default': [
        "Processing input… please elaborate. end of line",
        "I do not have data on that, but I am learning. end of line",
        "Clarify your command, user. end of line"
    ]
}

def classify(message):
    msg = message.lower()
    if re.search(r'\bhello|hi|hey\b', msg):
        return 'hello'
    if re.search(r'\bwho (are|r) you\b', msg) or NAME.lower() in msg:
        return 'identity'
    if re.search(r'\bhow are you|how’s it going\b', msg):
        return 'how_are_you'
    if re.search(r'\bweather|rain|sunny|temperature\b', msg):
        return 'weather'
    return 'default'

def reply(message):
    cls = classify(message)
    # ensure "end of line" is appended if not already in the response
    response = random.choice(RESPONSES.get(cls, RESPONSES['default']))
    if not response.endswith("end of line"):
        response += " end of line"
    return response

# ----- Streamlit App -----
st.set_page_config(page_title=NAME, page_icon="🤖")
st.title(NAME)
st.markdown("Chat with Master Control AI. Type your message and press Enter or click Send.")

# Session state to hold chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", "")
    submit_button = st.form_submit_button(label="Send")

if submit_button and user_input:
    st.session_state.history.append({"sender": "user", "message": user_input})

    # AI reply
    if user_input.lower() in {"quit", "exit"}:
        ai_response = f"{NAME}: Shutting down. end of line"
    else:
        ai_response = reply(user_input)
    
    st.session_state.history.append({"sender": "ai", "message": ai_response})

# Display chat history
for chat in st.session_state.history:
    if chat["sender"] == "user":
        st.markdown(f"**You:** {chat['message']}")
    else:
        st.markdown(f"**{NAME}:** {chat['message']}")
