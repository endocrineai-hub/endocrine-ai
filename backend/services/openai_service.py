import json
import os
from urllib import request, error


def openai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", "").strip())


def chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode("utf-8")
        parsed = json.loads(body)
        return parsed["choices"][0]["message"]["content"].strip()
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"OpenAI request failed ({exc.code}): {detail[:240]}") from exc
    except Exception as exc:
        raise RuntimeError(f"OpenAI request failed: {exc}") from exc
