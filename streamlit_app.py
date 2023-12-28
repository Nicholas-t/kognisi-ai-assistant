from openai import OpenAI
import streamlit as st
import time
import re

TOPIC = [
    {
        "label" : "Social Media Specialist",
        "file_id" : "file-35AuUAGwQNKZKoCLsFKpmvzU"
    },
    {
        "label" : "Creative Storytelling",
        "file_id" : "file-cKvyMcDAFazDhCGZ0mZeLKyz"
    },
    {
        "label" : "Teknik Dasar Pemetaan Masalah Ala Konsultan Manajemen",
        "file_id" : "file-Ss0rIYKaVZihZeqRSewRSXrU"
    }
]

def add_chat_to_ui(role, content):
    cm = None
    if role== "assistant":
        cm = st.chat_message(role, avatar="https://img-c.udemycdn.com/user/200_H/220263604_0a69_2.jpg")
    else:
        cm = st.chat_message(role)
    with cm:
        content_splitted = content.split("\n")
        for each_line in content_splitted:
            st.write(each_line)
    
def add_new_message(role, content):
    add_chat_to_ui(role, content)
    st.session_state.messages.append({"role": role, "content": content})

def add_user_response_and_wait_openai(client, thread_id, content="", file_ids=[], max_attempt = 5):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        file_ids=file_ids,
        content= content
    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id="asst_0zBfv84MUrQUmjP1DxNwOA4V"
    )

    last_status = "in_progress"
    while last_status != "completed" and max_attempt > 0:
        print("waiting")
        time.sleep(10)
        check = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        last_status = check.status
        max_attempt -= 1
    if last_status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        response = messages.data[0].content[0].text.value
        response = re.sub(r"【.*?】", '', response)
        return response
    else:
        print("last_status : {}".format(last_status))
        print(check)
        return "ERROR"
    
def launch_assistant(topic):
    file_id = ""
    for f in TOPIC:
        if f["label"] == topic:
            file_id = f["file_id"]
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    st.title("💬 AI Teach Assistant (Kognisi)") 
    
    if "messages" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state["thread_id"] = thread.id
        st.session_state["messages"] = []
        add_new_message("assistant", "Hallo! Apakah ada yang bisa saya bantu?")
    else:
        for msg in st.session_state.messages:
            add_chat_to_ui(msg["role"], msg["content"])
    if prompt := st.chat_input():
        add_new_message("user", prompt)
        response = add_user_response_and_wait_openai(client, st.session_state["thread_id"], prompt, file_ids=[file_id])
        add_new_message("assistant", response)
    
hide_toolbar_css = """
[data-testid='stToolbar'] {
    display:none;
}
"""
st.markdown(hide_toolbar_css, unsafe_allow_html=True)

topic_input = ""
with st.sidebar:
    topic_input = st.selectbox("Topic to test", key="topic", options=[a["label"] for a in TOPIC])

if topic_input != "":
    if "request_id" in st.session_state:
        if topic_input != st.session_state["topic"]:
            print("RESETTING MESSAGES AND THREADS")
            del st.session_state["messages"]
            del st.session_state["thread_id"]
    launch_assistant(topic_input)
else:
    st.write("Add Topic you want to learn...")