# OpenRouter AI чатбот

🔗 **Живий застосунок:** https://chatbotaipython.streamlit.app/

Простий чатбот на Streamlit з інтеграцією OpenRouter REST API.

## Локальний запуск

1. Встановіть залежності:
   pip install -r requirements.txt

2. Створіть файл `.streamlit/secrets.toml` (не комітьте його!) з вмістом:
   OPENROUTER_API_KEY = "ваш_ключ"

   Або створіть `.env`:
   OPENROUTER_API_KEY=ваш_ключ

3. Запустіть:
   streamlit run app.py

## Деплой на Streamlit Community Cloud

1. Запуште репозиторій на GitHub (без ключів!).
2. На share.streamlit.io підключіть репозиторій.
3. У розділі App settings → Secrets додайте:
   OPENROUTER_API_KEY = "ваш_ключ"