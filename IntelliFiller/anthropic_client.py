import json
import urllib.error
import urllib.request

class SimpleAnthropicClient:
    def __init__(self, api_key, model="claude-haiku-4-5"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    def create_message(self, prompt, system_prompt=None, temperature=None, max_tokens=None, timeout=60.0):
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": max_tokens or 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            data["system"] = system_prompt
        if temperature is not None:
            data["temperature"] = temperature
        
        payload = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(
            self.base_url,
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise Exception(f"HTTP {e.code} from Anthropic: {err_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error contacting Anthropic: {e}")

        try:
            data = json.loads(body)
            return data["content"][0]["text"]
        except Exception as e:
            raise Exception(f"Error parsing Anthropic response: {str(e)}")
