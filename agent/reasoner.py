"""Strands-based action planner; validation and policy remain local."""
import json
import os
from typing import Any

from dotenv import load_dotenv
from strands import Agent
from strands.models.gemini import GeminiModel
from strands.models.ollama import OllamaModel
from strands.models.openai import OpenAIModel

load_dotenv()

SYSTEM = """You are Proxy's action planner. Return exactly one JSON object with
action_type, payload, and reason. Allowed action_type values are type, submit,
ask_human. Use only supplied selectors. Fill the first unfilled field. Use
submit only when every field is filled. Never invent or infer real PII. Keep
reason short and plain-language. Return JSON only."""


def _value_for(field: str) -> str:
    return {"full_name": "Jane Doe", "address": "123 Demo Street, Springfield, 12345",
            "income": "42000", "annual_income": "42000"}.get(field, "Demo value")


def _validate(value: Any, fields: list[str], submit: str | None) -> dict:
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        raise ValueError("Strands returned a non-object action")
    kind, payload = value.get("action_type"), value.get("payload")
    if kind not in {"type", "submit", "ask_human"} or not isinstance(payload, dict):
        raise ValueError("Strands returned an invalid action shape")
    if kind == "type":
        selector = payload.get("selector")
        if selector in fields:
            selector = f"#{selector}"
            payload["selector"] = selector
        if selector not in {f"#{field}" for field in fields}:
            raise ValueError("Strands selected an unknown field")
        if not isinstance(payload.get("text", ""), str):
            raise ValueError("type action text must be a string")
    elif kind == "submit" and payload.get("selector") != (f"#{submit}" if submit else None):
        raise ValueError("Strands selected an invalid submit target")
    elif kind == "ask_human" and not str(payload.get("reason", "")).strip():
        raise ValueError("ask_human requires a reason")
    return {"action_type": kind, "payload": payload,
            "reason": str(value.get("reason", "")), "provider": "Strands"}


def _fallback(fields: list[str], filled: set[str], submit: str | None) -> dict:
    for field in fields:
        if field not in filled:
            return {"action_type": "type", "payload": {"selector": f"#{field}", "text": _value_for(field)},
                    "reason": "Using a safe local demo value because Strands was unavailable.",
                    "provider": "Local Fallback"}
    if submit:
        return {"action_type": "submit", "payload": {"selector": f"#{submit}"},
                "reason": "All fields are filled and the submit control is ready.", "provider": "Local Fallback"}
    return {"action_type": "ask_human", "payload": {"reason": "No actionable field or submit control was found."},
            "reason": "No actionable field or submit control was found.", "provider": "Local Fallback"}


def decide_next_action(task_description: str, fields: list[str], filled_fields: set[str], submit_selector: str | None) -> dict:
    context = json.dumps({"task": task_description, "fields": fields,
                          "filled_fields": sorted(filled_fields), "submit_selector": submit_selector})
    providers = []
    if os.getenv("GROQ_API_KEY"):
        providers.append(("Groq", OpenAIModel(model_id=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            client_args={"api_key": os.environ["GROQ_API_KEY"], "base_url": "https://api.groq.com/openai/v1"})))
    if os.getenv("GEMINI_API_KEY"):
        providers.append(("Gemini", GeminiModel(model_id=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            client_args={"api_key": os.environ["GEMINI_API_KEY"]})))
    providers.append(("Ollama", OllamaModel(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model_id=os.getenv("OLLAMA_MODEL", "llama3.2:latest"), temperature=0)))
    for name, model in providers:
      try:
        agent = Agent(model=model, system_prompt=SYSTEM)
        result = agent(context)
        text = getattr(result, "output", result)
        action = _validate(text, fields, submit_selector)
        action["provider"] = name
        return action
      except Exception:
        continue
    return _fallback(fields, filled_fields, submit_selector)
