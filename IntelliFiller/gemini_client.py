import json
import urllib.error
import urllib.request
import urllib.parse

class GeminiClient:
    def __init__(self, api_key, model="gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate_content(self, prompt, timeout=60.0):
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
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
