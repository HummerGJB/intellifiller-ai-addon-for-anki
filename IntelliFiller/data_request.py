import json
import re
import sys
import os
import urllib.error
import urllib.request

from aqt import mw


import platform
def get_platform_specific_vendor():
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'darwin':  # macOS
        if machine == 'arm64':
            return 'darwin_arm64'
        return 'darwin_x86_64'
    elif system == 'windows':
        return 'win32'
    elif system == 'linux':
        return 'linux'
    else:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")

addon_dir = os.path.dirname(os.path.realpath(__file__))
vendor_dir = os.path.join(addon_dir, "vendor", get_platform_specific_vendor())
sys.path.append(vendor_dir)

from .config_manager import ConfigManager
from .anthropic_client import SimpleAnthropicClient
from .gemini_client import GeminiClient
from html import unescape


def create_prompt(note, prompt_config):
    prompt_template = prompt_config['prompt']
    pattern = re.compile(r'\{\{\{(\w+)\}\}\}')
    field_names = pattern.findall(prompt_template)
    for field_name in field_names:
        if field_name not in note:
            raise ValueError(f"Field '{field_name}' not found in note.")
        prompt_template = prompt_template.replace(f'{{{{{{{field_name}}}}}}}', note[field_name])
    # unescape HTML entities and replace line breaks with spaces
    prompt_template = unescape(prompt_template)
    # remove HTML tags
    prompt_template = re.sub('<.*?>', '', prompt_template)
    return prompt_template


def send_prompt_to_llm(prompt):
    # Load settings first to get encryption key and API selector
    settings = ConfigManager.load_settings()
    encryption_key = settings.get("encryptionKey", "")
    
    # Load credentials using the key
    credentials = ConfigManager.load_credentials(key=encryption_key)
    
    # Merge for easier access
    config = {**settings, **credentials}
    
    # Get timeout from settings (default 10s)
    net_timeout = float(config.get("netTimeout", 10.0))

    if config.get('emulate') == 'yes':
        print("Fake request: ", prompt)
        return f"This is a fake response for emulation mode for the prompt {prompt}."

    try:
        print("Request to API: ", prompt)
        def _http_chat_completion(base_url, api_key, model, messages, timeout, extra_headers=None):
            url = base_url.rstrip("/") + "/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            if extra_headers:
                headers.update(extra_headers)

            payload = {
                "model": model,
                "messages": messages,
            }

            data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(url, data=data, headers=headers, method="POST")

            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    body = response.read().decode("utf-8", errors="replace")
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"HTTP {e.code} from {base_url}: {err_body}")
            except urllib.error.URLError as e:
                raise RuntimeError(f"Network error contacting {base_url}: {e}")

            data = json.loads(body)

            if isinstance(data, dict) and data.get("error"):
                err = data["error"]
                msg = err.get("message") if isinstance(err, dict) else str(err)
                raise RuntimeError(f"API error from {base_url}: {msg}")

            return data["choices"][0]["message"]["content"].strip()

        def try_openai_call():
            response = _http_chat_completion(
                base_url="https://api.openai.com/v1",
                api_key=config["apiKey"],
                model=config.get("openaiModel") or "gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                timeout=net_timeout,
            )
            print("Response from OpenAI:", response)
            return response
            
        def try_anthropic_call():
            client = SimpleAnthropicClient(
                api_key=config['anthropicKey'], 
                model=config.get('anthropicModel') or 'claude-haiku-4-5'
            )
            response = client.create_message(prompt, timeout=net_timeout)
            print("Response from Anthropic:", response)
            return response.strip()

        def try_gemini_call():
            client = GeminiClient(
                api_key=config['geminiKey'],
                model=config.get('geminiModel') or 'gemini-2.0-flash-lite-001'
            )
            response = client.generate_content(prompt, timeout=net_timeout)
            print("Response from Gemini:", response)
            return response.strip()

        def try_openrouter_call():
            response = _http_chat_completion(
                base_url="https://openrouter.ai/api/v1",
                api_key=config["openrouterKey"],
                model=config.get("openrouterModel") or "google/gemini-2.0-flash-lite-001",
                messages=[{"role": "user", "content": prompt}],
                timeout=net_timeout,
                extra_headers={
                    "HTTP-Referer": "https://ankiweb.net/",
                    "X-Title": "IntelliFiller Anki Addon",
                },
            )
            print("Response from OpenRouter:", response)
            return response

        def try_custom_call():
            response = _http_chat_completion(
                base_url=config["customUrl"],
                api_key=config["customKey"],
                model=config.get("customModel") or "my-model",
                messages=[{"role": "user", "content": prompt}],
                timeout=net_timeout,
            )
            print("Response from Custom Provider:", response)
            return response

        try:
            if config['selectedApi'] == 'anthropic':
                return try_anthropic_call()
            elif config['selectedApi'] == 'gemini':
                return try_gemini_call()
            elif config['selectedApi'] == 'openrouter':
                return try_openrouter_call()
            elif config['selectedApi'] == 'custom':
                return try_custom_call()
            else:  # openai
                return try_openai_call()
        except Exception as e:
            # Re-raise exceptions so they can be caught by the worker thread
            raise e
    except Exception as e:
        # Re-raise to be handled by the caller (worker thread)
        raise e


def test_connection(config, timeout=None):
    """Run a lightweight request to validate the selected provider, key, and model."""
    net_timeout = float(timeout if timeout is not None else config.get("netTimeout", 10.0))
    prompt = "Connection test. Reply with 'ok'."

    def _http_chat_completion(base_url, api_key, model, messages, timeout, extra_headers=None):
        url = base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)

        payload = {
            "model": model,
            "messages": messages,
        }

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} from {base_url}: {err_body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error contacting {base_url}: {e}")

        data = json.loads(body)

        if isinstance(data, dict) and data.get("error"):
            err = data["error"]
            msg = err.get("message") if isinstance(err, dict) else str(err)
            raise RuntimeError(f"API error from {base_url}: {msg}")

        return data["choices"][0]["message"]["content"].strip()

    selected = config.get("selectedApi", "openai")

    if selected == "anthropic":
        client = SimpleAnthropicClient(
            api_key=config.get("anthropicKey", ""),
            model=config.get("anthropicModel") or "claude-haiku-4-5",
        )
        client.create_message(prompt, max_tokens=8, timeout=net_timeout)
        return "Anthropic"

    if selected == "gemini":
        client = GeminiClient(
            api_key=config.get("geminiKey", ""),
            model=config.get("geminiModel") or "gemini-2.0-flash-lite-001",
        )
        client.generate_content(prompt, timeout=net_timeout)
        return "Google Gemini"

    if selected == "openrouter":
        _http_chat_completion(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.get("openrouterKey", ""),
            model=config.get("openrouterModel") or "google/gemini-2.0-flash-lite-001",
            messages=[{"role": "user", "content": prompt}],
            timeout=net_timeout,
            extra_headers={
                "HTTP-Referer": "https://ankiweb.net/",
                "X-Title": "IntelliFiller Anki Addon",
            },
        )
        return "OpenRouter"

    if selected == "custom":
        base_url = (config.get("customUrl") or "").strip()
        if not base_url:
            raise RuntimeError("Custom base URL is required for OpenAI-compatible providers.")
        _http_chat_completion(
            base_url=base_url,
            api_key=config.get("customKey", ""),
            model=config.get("customModel") or "my-model",
            messages=[{"role": "user", "content": prompt}],
            timeout=net_timeout,
        )
        return "OpenAI Compatible"

    # Default: OpenAI
    _http_chat_completion(
        base_url="https://api.openai.com/v1",
        api_key=config.get("apiKey", ""),
        model=config.get("openaiModel") or "gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        timeout=net_timeout,
    )
    return "OpenAI"
