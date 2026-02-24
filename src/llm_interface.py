import requests
import json
import time

print("🔥 LLMInterface module loaded — REAL HTTP MODE ACTIVE")

class LLMInterface:

    def __init__(
        self,
        base_url="http://localhost:8000/v1",
        model="Qwen/Qwen2.5-7B-Instruct",
        temperature=0.2
    ):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature

    def _chat_completion(self, system_prompt, user_prompt):

        print("\n🚀 ENTERED _chat_completion()")

        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature
        }

        print("\n========== LLM REQUEST ==========")
        print("POST:", url)
        print("Payload:")
        print(json.dumps(payload, indent=2))
        print("==================================")

        start_time = time.time()

        response = requests.post(url, json=payload)

        duration = time.time() - start_time

        print("\n========== LLM RAW RESPONSE ==========")
        print("Status Code:", response.status_code)
        print("Time Taken:", duration, "seconds")
        print("Raw Text:")
        print(response.text)
        print("=======================================")

        response.raise_for_status()

        result = response.json()

        if "choices" not in result:
            raise Exception("❌ Invalid LLM response format")

        content = result["choices"][0]["message"]["content"]

        print("\n🧠 EXTRACTED LLM CONTENT:")
        print(content)
        print("=======================================")

        return content
