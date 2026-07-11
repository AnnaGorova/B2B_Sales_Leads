# python -m streamlit run app.py
# streamlit run app.py
import pandas as pd
import streamlit as st
import os 

from openrouter import ask_openrouter

import requests  
from datetime import datetime

def build_chat_export(messages, mode, model):
    lines = [
        "# Історія діалогу",
        "",
        f"**Режим асистента:** {mode}",
        f"**Модель:** {model}",
        f"**Дата експорту:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        ""
    ]

    for msg in messages:
        role_label = "🧑 Користувач" if msg["role"] == "user" else "🤖 Асистент"
        lines.append(f"**{role_label}:**")
        lines.append("")
        lines.append(msg["content"])
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def get_api_key():
    key = None
    source = None

    try:
        key = st.secrets["OPENROUTER_API_KEY"]
        source = "secrets"
    except Exception:
        key = os.getenv("OPENROUTER_API_KEY")
        source = "env"

   

    return key or ""

st.title("OpenRouter AI чатбот")
st.write("Простий чатбот з Streamlit та OpenRouter REST API")



ASSISTANT_MODES = {
    "Python tutor": (
        "Ти дружній Python-репетитор. Пояснюй концепції Python простими словами, "
        "уникай складного жаргону. До кожного пояснення додавай короткий приклад коду "
        "(3-7 рядків). Відповідай українською."
    ),
    "Code reviewer": (
        "Ти досвідчений код-рев'юер. Отримавши код, аналізуй його на помилки, "
        "погані практики, продуктивність та читабельність. Дай від 2 до 4 конкретних, "
        "практичних порад з покращення, кожну з коротким поясненням чому. "
        "Не переписуй увесь код — лише вказуй на проблеми. Відповідай українською."
    ),
    "Study assistant": (
        "Ти асистент з навчання. Допомагай студенту сформулювати чіткий план навчання "
        "або повторення теми: розбий тему на логічні підтеми, запропонуй порядок вивчення "
        "та орієнтовний час на кожен етап. Став уточнюючі запитання, якщо тема заявлена "
        "занадто широко. Відповідай українською."
    ),
}


with st.sidebar:
    st.header("Параметри")
    
    mode = st.selectbox("Режим асистента", list(ASSISTANT_MODES.keys()))
    
    model = st.selectbox("Модель", [
        "openrouter/free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "openai/gpt-oss-20b:free"
    ])
    temperature = st.slider("Температура", 0.0, 1.5, 0.7, 0.1)

    system_prompt = st.text_area(
        "Системний промт",
        value=ASSISTANT_MODES[mode],
        key=f"prompt_{mode}"
    )

    st.divider()
    
    if st.session_state.get("messages"):
        export_text = build_chat_export(st.session_state.messages, mode, model)
        st.download_button(
            label="Завантажити історію (.md)",
            data=export_text,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    else:
        st.caption("Історія чату порожня — немає що завантажувати")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode

if st.session_state.current_mode != mode:
    st.session_state.current_mode = mode
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])  

user_message = st.chat_input("Напишіть повідомлення")

if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        try:
            api_messages = [{"role": "system", "content": system_prompt}]
            api_messages.extend(st.session_state.messages)
            
            with st.spinner("Думаю..."):
                answer = ask_openrouter(get_api_key(), api_messages, model, temperature)
                
           
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except requests.HTTPError as error:
            st.error(f"HTTP-помилка OpenRouter API: {error}")
            st.stop()
        except Exception as error:
            st.error(f"Помилка OpenRouter API: {error}")
            st.stop()




