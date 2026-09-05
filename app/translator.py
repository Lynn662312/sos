import json
import os
import re
from typing import Any, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.models import Alert, TranslatedAlert

load_dotenv()  # Load environment variables from .env file  
_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")


def _model_to_dict(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    raise TypeError("Unsupported model type (expected pydantic BaseModel)")


def _model_to_json(model: Any, *, indent: int = 2) -> str:
    if hasattr(model, "model_dump_json"):
        return model.model_dump_json(indent=indent, ensure_ascii=False)
    if hasattr(model, "json"):
        return model.json(indent=indent, ensure_ascii=False)
    return json.dumps(_model_to_dict(model), indent=indent, ensure_ascii=False)


def _extract_json_object(text: str) -> str:
    """
    Best-effort extraction of a single JSON object from a model response.
    Handles common wrapping like ```json ... ``` and extra prose.
    """
    if not text:
        raise ValueError("Empty model output")

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    match = _JSON_BLOCK_RE.search(cleaned)
    if not match:
        raise ValueError("No JSON object found in model output")
    return match.group(0)


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_str_list(value: Any) -> Optional[list[str]]:
    if value is None:
        return None
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if item is None:
                continue
            out.append(str(item))
        return out or None
    if isinstance(value, str):
        s = value.strip()
        return [s] if s else None
    return [str(value)]


def translate_alert_data(alert: Alert) -> TranslatedAlert:
    """
    Translate a Japanese JMA alert into English + Simplified Chinese and
    produce a trust score using the NEW google-genai SDK.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")

    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in environment/.env")

    # The Prompt remains the same (it's the most important part!)
    
    prompt = f"""
    You are a Japan Disaster Response Expert supporting foreigners in Japan.

Task:
- Translate the following Japanese alert title and summary into:
  1) English
  2) Simplified Chinese (zh)
  3) KEY REQUIREMENT: Look for any specific official instructions or evacuation orders (e.g., "避難指示", "高台へ移動", "火の始末").
  4) If instructions exist, extract them into a "emergency_actions" field. If none, put "Stay alert for further updates."
  5) Prioritize clarity and direct safety actions for foreigners.
  Use clear imperatives like "Evacuate" / "Move to higher ground" / "Stay indoors" when appropriate.
  6) Also compute a trust_score (0.0 to 10.0) based on how official the Japanese text is:
    - Official JMA alerts or government notices: 10/10
    - Unverified/suspicious wording (rumors, social media style, no source): ~2/10
  7) Extract the primary Japanese Prefecture mentioned (e.g., 東京都 -> Tokyo). Default to "Unknown" if not found.
  8) Categorize the alert severity:
    - "Critical": For Earthquakes (Intensity 5+), Tsunami Warnings, or Evacuation Orders.
    - "Warning": For standard Weather Warnings (Flood, Heavy Rain, Gale).
    - "Advisory": For minor Advisories (Frost, Dry Air, Fog).
  9)2. EXTRACT EMERGENCY DETAILS: 
   - Look for specific shelter locations (避難所).
   - Look for transport status or "Returning Home" (帰宅困難者) instructions.
   - Look for food/water distribution points if mentioned.
  10) If no specific location is mentioned, provide the standard evacuation procedure for this type of alert in Japan (e.g., "Check the 'Safety Tips' app" or "Go to the nearest designated school").

Input (Japanese):
title: {alert.title}
summary: {alert.summary}

Output MUST be strict JSON ONLY (no markdown, no backticks, no extra keys):
{{
  "translated_title_en": "...",
  "translated_summary_en": "...",
  "translated_title_zh": "...",
  "translated_summary_zh": "...",
  "emergency_actions_en": ["..."],
  "emergency_actions_zh": ["..."],
  "prefecture": "...",
  "category": "Critical|Warning|Advisory",
  "trust_score": 10.0
}}
    """.strip()

    try:
        # 1. Initialize the NEW Client
        client = genai.Client(api_key=api_key)

        # 2. Generate Content
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", # Forces Gemini to return JSON
                temperature=0.1,  # Low temperature for more deterministic output
            )
        )

        # 3. Get the text output
        text = response.text
        
        # 4. Clean and Parse JSON
        json_str = _extract_json_object(text)
        payload = json.loads(json_str)

        trust_score = _safe_float(payload.get("trust_score"))
        if trust_score is not None:
            trust_score = max(0.0, min(10.0, trust_score))

        # 5. Return the full object
        alert_data = _model_to_dict(alert)
        alert_data.pop("prefecture", None)
        alert_data.pop("category", None)

        return TranslatedAlert(
            **alert_data,
            translated_title_en=payload.get("translated_title_en"),
            translated_summary_en=payload.get("translated_summary_en"),
            translated_title_zh=payload.get("translated_title_zh"),
            translated_summary_zh=payload.get("translated_summary_zh"),
            emergency_actions_en=" | ".join(_safe_str_list(payload.get("emergency_actions_en"))
            or ["Stay alert for further updates."]),
            emergency_actions_zh=" | ".join(_safe_str_list(payload.get("emergency_actions_zh"))
            or ["请保持警惕，等待进一步更新。"]),
            prefecture=payload.get("prefecture"),
            category=payload.get("category"),
            trust_score=trust_score
        )
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        #create a dictonary of all the original alert data and add the fallback translations and default values
        alert_data = _model_to_dict(alert)
        alert_data.pop("prefecture", None)  
        alert_data.pop("category", None)

        # If it fails, return the original alert with null translations
        return TranslatedAlert(**alert_data, 
                               translated_title_en= alert.title,  # Fallback to original if translation fails
                               translated_summary_en= alert.summary,  # Fallback to original if translation fails
                                translated_title_zh= alert.title,  # Fallback to original if translation fails
                                translated_summary_zh= alert.summary,  # Fallback to original if translation fails
                                prefecture="Unknown",  # Default if extraction fails
                                category="Advisory",  # Default if extraction fails
                                trust_score=None,
                                emergency_actions_en="AI is busy. Please refer to official sources and stay informed.",  # Default safety message
                               emergency_actions_zh="AI 正在忙碌。请参考官方来源并保持关注。")


def generate_audio(text: str, language: str = "en") -> bytes:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ELEVENLABS_API_KEY in environment/.env")

    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        text=text,
        model_id="eleven_multilingual_v2",
        voice_id = "cgSgspJ2msm6clMCkdW9" if language == "zh" else "JBFqnCBsd6RMkjVDRZzb",
        output_format="mp3_44100_128",
    )
    return b"".join(audio)


if __name__ == "__main__":
    print("---SOS Project: translator test ---")
    test_alert = Alert(
        id="test-fukui-wind-warning",
        title="【気象警報・注意報】福井県　強風注意報",
        summary=(
            "福井県では、強風や高波に注意してください。"
            "屋外の安全を確保し、飛ばされやすい物は固定してください。"
        ),
        link="https://www.jma.go.jp/",
        updated="2026-05-08T00:00:00+09:00",
    )

    translated = translate_alert_data(test_alert)
    print(_model_to_json(translated, indent=2))
