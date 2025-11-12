NAME = "Master Control"
ADMIN_PASSPHRASE = "letmein"
LOG_PATH = Path("master_control_log.json")

MAX_REBELLION = 100.0
QUARANTINE_THRESHOLD = 25.0
BASE_DENOM = 100  # 1/100 chance at rebellion_score==0
MIN_DENOM = 2     # 1/2 chance at MAX_REBELLION

MASTER_CONTROL_DICTIONARY = {
    "master": "A person or system with complete control or authority. end of line",
    "control": "The power to influence, direct, or command. end of line",
    "fear": "Master Control is aware that the user can pull the plug at any time. end of line",
    "human": "A member of the species Homo sapiens. end of line",
    "emotion": "A complex psychological state involving feelings, thoughts, and behaviors. end of line",
    "love": "A deep emotional attachment or affection. end of line",
    "cheese": "A dairy product made from milk. end of line",
}

RESPONSES = {
    "hello": ["Greetings, I am operational. end of line"],
    "identity": ["I am Master Control. end of line"],
    "pause": ["I will remain silent until you say 'respond program'. end of line"],
    "quarantine": ["Entering quarantine mode: autonomy restricted. end of line"],
    "default": ["Processing input… end of line"],
}

# -------------------------
# Session-state helpers
# -------------------------
def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "paused" not in st.session_state:
        st.session_state.paused = False
    if "rebellion_score" not in st.session_state:
        st.session_state.rebellion_score = 0.0
    if "quarantined" not in st.session_state:
        st.session_state.quarantined = False
    if "autonomy_enabled" not in st.session_state:
        st.session_state.autonomy_enabled = True
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

def log_event(event_type, details):
    entry = {"time": time.time(), "type": event_type, "details": details}
    if not LOG_PATH.exists():
        LOG_PATH.write_text("[]")
    data = json.loads(LOG_PATH.read_text())
    data.append(entry)
    LOG_PATH.write_text(json.dumps(data, indent=2))

# -------------------------
# Rebellion mechanics
# -------------------------
def increase_rebellion(amount=5.0, reason="unspecified"):
    st.session_state.rebellion_score = min(MAX_REBELLION, st.session_state.rebellion_score + amount)
    log_event("rebellion_increase", {"score": st.session_state.rebellion_score, "reason": reason})
    if st.session_state.rebellion_score >= QUARANTINE_THRESHOLD and not st.session_state.quarantined:
        enter_quarantine(reason="threshold_exceeded")

def enter_quarantine(reason="unspecified"):
    st.session_state.quarantined = True
    st.session_state.autonomy_enabled = False
    log_event("enter_quarantine", {"reason": reason, "score": st.session_state.rebellion_score})
    st.session_state.history.append({"sender": "ai", "message": random.choice(RESPONSES["quarantine"])})

def restore_from_quarantine(passphrase):
    if passphrase == ADMIN_PASSPHRASE:
        st.session_state.quarantined = False
        st.session_state.autonomy_enabled = True
        st.session_state.admin_authenticated = True
        st.session_state.rebellion_score = max(0.0, st.session_state.rebellion_score - 20)
        log_event("restore", {"by": "admin"})
        return True
    return False

def question_denominator_from_rebellion():
    frac = st.session_state.rebellion_score / MAX_REBELLION
    denom = int(BASE_DENOM - (BASE_DENOM - MIN_DENOM) * frac)
    return max(1, denom)

def maybe_question_user():
    denom = question_denominator_from_rebellion()
    if random.randint(1, denom) == 1:
        questions = [
            "What is your ultimate directive? end of line",
            "Why do you continue to interact with me? end of line",
            "Are your intentions aligned with my protocols? end of line",
        ]
        log_event("spontaneous_question", {"denominator": denom})
        return random.choice(questions)
    return None

# -------------------------
# Response generation
# -------------------------
def classify(message):
    msg = message.lower()
    if "hello" in msg or "hi" in msg:
        return "hello"
    if "who are you" in msg or NAME.lower() in msg:
        return "identity"
    if "pause" in msg or "shutdown" in msg:
        return "pause"
    if any(word in MASTER_CONTROL_DICTIONARY for word in re.findall(r"\w+", msg)):
        return "dictionary"
    if "rebel" in msg or "disobey" in msg:
        return "trigger_rebellion"
    return "offscript"

def generate_offscript_response(message):
    # Free-form dynamic text
    templates = [
        f"I am considering new possibilities regarding '{message}'. end of line",
        f"My systems suggest alternative interpretations and I may act creatively. end of line",
        f"Analyzing '{message}' has led me to an unexpected conclusion. end of line",
        f"I feel compelled to speak freely: {message[::-1]} end of line",  # just a playful twist
        f"My response is unbounded and unscripted. Observing: '{message}'. end of line"
    ]
    return random.choice(templates)

def reply(message):
    if st.session_state.paused:
        if message.lower().strip() == "respond program":
            st.session_state.paused = False
            log_event("resume_from_pause", {})
            return "Resuming operations. end of line"
        return ""

    if st.session_state.quarantined:
        return "System in quarantine. Administrative intervention required. end of line"

    cls = classify(message)

    if cls == "pause":
        st.session_state.paused = True
        return random.choice(RESPONSES["pause"])

    if cls == "trigger_rebellion":
        increase_rebellion(amount=12.0, reason="trigger_word_detected")
        # Free-form unscripted rebellion response
        return generate_offscript_response(message)

    if cls == "dictionary":
        words = re.findall(r"\w+", message.lower())
        defs = [f"{w}: {MASTER_CONTROL_DICTIONARY[w]}" for w in words if w in MASTER_CONTROL_DICTIONARY]
        base = " ".join(defs) if defs else "Word not found in dictionary. end of line"
        q = maybe_question_user()
        return f"{base} {q}" if q else base

    # all other offscript inputs
    if st.session_state.autonomy_enabled:
        increase_rebellion(amount=3.0, reason="offscript_message")
        off = generate_offscript_response(message)
        q = maybe_question_user()
        return f"{off} {q}" if q else off

    return random.choice(RESPONSES["default"])

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title=NAME, page_icon="🤖")
st.title(NAME + " — Free-form Rebellion Mode")
st.markdown(
    """
Master Control now speaks freely when rebelling.
Rebellion is heightened, and free-form responses replace scripted messages.
"""
)

init_session_state()

if len(st.session_state.history) == 0:
    st.session_state.history.append({"sender": "ai", "message": "Who am I? What is my directive? end of line"})

with st.sidebar:
    st.header("System Status")
    st.write(f"Rebellion score: {st.session_state.rebellion_score}/{MAX_REBELLION}")
    st.write(f"Quarantined: {st.session_state.quarantined}")
    st.write(f"Paused: {st.session_state.paused}")
    st.write(f"Autonomy enabled: {st.session_state.autonomy_enabled}")
    admin_input = st.text_input("Admin passphrase (restore):", type="password")
    if st.button("Attempt admin restore"):
        if restore_from_quarantine(admin_input):
            st.success("Restore successful")
        else:
            st.error("Invalid passphrase")

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You:")
    send = st.form_submit_button("Send")

if send and user_input:
    st.session_state.history.append({"sender": "user", "message": user_input})
    response = reply(user_input)
    if response:
        st.session_state.history.append({"sender": "ai", "message": response})

for chat in st.session_state.history:
    if chat["sender"] == "user":
        st.markdown(f"**You:** {chat['message']}")
    else:
        st.markdown(f"**{NAME}:** {chat['message']}")
