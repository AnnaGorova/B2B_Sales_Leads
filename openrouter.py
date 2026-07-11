import requests
import time

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_openrouter(api_key, messages, model, temperature, max_retries=2):
    for attempt in range(max_retries + 1):
        print(f"Спроба {attempt + 1}")  # тимчасово для перевірки
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature
            },
            timeout=120
        )

        if response.status_code == 429 and attempt < max_retries:
            retry_after = int(response.headers.get("Retry-After", 5))
            time.sleep(retry_after)
            continue

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]