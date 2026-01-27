import json
import urllib.error
import urllib.request
import urllib.parse

class GeminiClient:
    def __init__(self, api_key, model="gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate_content(self, prompt, system_prompt=None, temperature=None, max_tokens=None, timeout=60.0):
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        if system_prompt:
            data["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        generation_config = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_tokens is not None:
            generation_config["maxOutputTokens"] = max_tokens
        if generation_config:
            data["generationConfig"] = generation_config
        
        query = urllib.parse.urlencode({"key": self.api_key})
        url = f"{self.base_url}?{query}"
        payload = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise Exception(f"HTTP {e.code} from Gemini: {err_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error contacting Gemini: {e}")

        try:
            result = json.loads(body)
            # Response format: { "candidates": [ { "content": { "parts": [ { "text": "..." } ] } } ] }
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise Exception(f"Error parsing Gemini response: {str(e)}")
