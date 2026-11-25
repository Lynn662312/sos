from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

import requests
import streamlit as st


def _get_api_base_url() -> str:
    """Resolve the backend base URL: Streamlit secrets > env var > localhost fallback."""
    try:
        return st.secrets["API_BASE_URL"]
    except Exception:
        pass
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


API_BASE_URL = _get_api_base_url().rstrip("/")
API_URL = f"{API_BASE_URL}/api/alerts"
JST = timezone(timedelta(hours=9), name="JST")

def _parse_to_jst(updated: str) -> str:
    if not updated:
        return "Unknown time"
    s = updated.strip()
    try:
        # Handle common ISO-8601 variants
        if s.endswith("Z"):
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(s)
    except ValueError:
        return updated

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S %Z")


# Render's free tier spins the backend down after ~15 min idle; the first
# request after that wakes it up but can take 20-30s, and Render's edge
# often returns a 502/503 for requests that arrive before it's ready. Retry
# with backoff instead of failing on the very first attempt.
_RETRYABLE_STATUS = {502, 503, 504}


def _fetch_alerts(
    prefecture: str = "All Prefectures",
    max_attempts: int = 5,
    backoff_seconds: float = 6.0,
    on_retry: Optional[Callable[[int, int], None]] = None,
) -> list[dict[str, Any]]:
    last_error: Exception = RuntimeError("no attempts made")
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(f"{API_URL}?prefecture={prefecture}", timeout=20)
            if resp.status_code in _RETRYABLE_STATUS:
                raise requests.exceptions.HTTPError(
                    f"{resp.status_code} Server Error (backend likely still waking up)"
                )
            resp.raise_for_status()
            payload = resp.json()
            if not isinstance(payload, list):
                raise ValueError("API returned non-list payload")
            return payload
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as e:
            last_error = e
            if attempt < max_attempts:
                if on_retry:
                    on_retry(attempt, max_attempts)
                time.sleep(backoff_seconds)
    raise last_error


st.set_page_config(page_title="S.O.S (Source of Safety)", layout="wide")

st.title("S.O.S (Source of Safety)")
with st.sidebar:
    st.header("📍 Your Location")
    selected_prefecture = st.selectbox(
        "Select your prefecture to prioritize relevant alerts:",
        options=[
            "All Prefectures",
            "Hokkaido", "Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima",
            "Ibaraki", "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa",
            "Niigata", "Toyama", "Ishikawa", "Fukui",
            "Yamanashi", "Nagano",
            "Gifu", "Shizuoka",
            "Aichi",
            "Mie",
            "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama",
            "Tottori", "Shimane",
            "Okayama", "Hiroshima", "Yamaguchi",
            "Tokushima", "Kagawa", "Ehime", "Kochi",
            "Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima",
            "Okinawa"
        ],
        index=13
    )
    st.info("Note: Manual selection for now. Future versions may auto-detect location or allow saving preferences.")
    st.divider()
    st.header("🔊 Audio Settings")
    auto_generate = st.checkbox("Auto-generate voice for Critical Alerts", value=True)
st.caption("Instant, Verified Disaster Alerts for Foreigners in Japan.")

col_a, col_b = st.columns([1, 2])
with col_a:
    refresh = st.button("Refresh Alerts", type="primary")
with col_b:
    language = st.selectbox("Display language", options=["English", "Chinese"], index=0)

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if refresh or not st.session_state.alerts:
    status_placeholder = st.empty()

    def _report_retry(attempt: int, max_attempts: int) -> None:
        status_placeholder.info(
            "⏳ Waking up the backend — free hosting sleeps after inactivity, "
            f"this can take up to ~30s (attempt {attempt}/{max_attempts - 1})..."
        )

    try:
        st.session_state.alerts = _fetch_alerts(selected_prefecture, on_retry=_report_retry)
        status_placeholder.empty()
        st.success(f"Loaded {len(st.session_state.alerts)} alerts.")
    except Exception as e:
        status_placeholder.empty()
        st.error(
            "Couldn't reach the alerts backend after several attempts. It's most "
            "likely still waking up from sleep on free hosting — click **Refresh "
            f"Alerts** again in about 30 seconds.\n\nDetails: {e}"
        )

# --- ADD MOCK DEMO HERE ---
if st.sidebar.button("🚀 Trigger Demo Mode"):
    mock_alert = {
        "id": "demo-123",
        "category": "Critical",
        "prefecture": "Tokyo",
        "translated_title_en": "Emergency Earthquake Warning",
        "translated_title_zh": "紧急地震速报",
        "translated_summary_en": "Major shaking expected in Tokyo area. Seismic intensity 6 Lower.",
        "translated_summary_zh": "东京地区预计将有剧烈震动。震度 6 弱。",
        "emergency_actions_en": "Drop, Cover, and Hold on. Stay away from glass.",
        "emergency_actions_zh": "趴下、掩护、稳住。远离玻璃。",
        "trust_score": 10.0,
        "updated": datetime.now(timezone.utc).isoformat(),
        "hash": "f41bb0443e...",
        "ipfs_cid": "QmU5ZbzM8..."
    }
    # Put mock alert at the very top
    st.session_state.alerts = [mock_alert] + st.session_state.alerts
# --------------------------

alerts = st.session_state.alerts or []

if not alerts:
    st.info("No alerts to display yet. Click Refresh Alerts.")
else:
    for alert in alerts:
        #define content
        title_en = alert.get("translated_title_en") or alert.get("title") or "Untitled"
        title_zh = alert.get("translated_title_zh") or alert.get("title") or "Untitled"
        display_title = title_en if language == "English" else title_zh

        # get the category and set the style
        category = alert.get("category", "Advisory")

        #set visual style
        if category == "Critical":
            box = st.error
            icon = "🚨"
        elif category == "Warning":
            box = st.warning
            icon = "⚠️"
        else:
            box = st.info
            icon = "ℹ️"
        # alert_pref = alert.get("prefecture", "Unknown")
        # if selected_prefecture != "All Prefectures" and alert_pref != selected_prefecture:
        #     continue
        
        
        #display high visibility box
        box(f"{icon} **{category.upper()}**: {display_title} ")
        updated_jst = _parse_to_jst(str(alert.get("updated") or ""))

        trust_score = alert.get("trust_score", None)
        trust_label = "Trust Score"
        trust_value = "—" if trust_score is None else f"{trust_score:.1f} / 10"

        expander_label = f"{display_title}  ·  {updated_jst}"
        expander_key = f"exp_{alert.get('id')}"
        if expander_key not in st.session_state:
            st.session_state[expander_key] = False
        with st.expander(expander_label, expanded=st.session_state.get(expander_key, False)):
            st.subheader(title_en)

            mcol1, mcol2 = st.columns([1, 2])
            with mcol1:
                st.metric(trust_label, trust_value)
            with mcol2:
                st.write(f"**Time (JST)**: {updated_jst}")

            if language == "English":
                st.markdown("### Summary")
                st.write(alert.get("translated_summary_en") or alert.get("summary") or "")
                st.markdown("### Emergency Actions")
                action_text = alert.get("emergency_actions_en") or "Stay alert for further updates."
                if isinstance(action_text, list):
                    action_text = " | ".join(action_text)  
                st.warning(action_text)
            else:
                #chinese block
                st.markdown("### Summary")
                st.write(alert.get("translated_summary_zh") or alert.get("summary") or "")
                st.markdown("### 紧急避难行动")
                action_text = alert.get("emergency_actions_zh") or "请保持警惕，等待进一步更新。"
                if isinstance(action_text, list):
                    action_text = " | ".join(action_text)
                st.warning(action_text)
        

            st.markdown("### Proof")
            sha = alert.get("hash") or "—"
            cid = alert.get("ipfs_cid") or "—"
            st.write(f"**SHA-256**: `{sha}`")
            st.write(f"**IPFS CID**: `{cid}`")
            if cid != "—":
                st.link_button("Open IPFS Gateway", f"https://gateway.pinata.cloud/ipfs/{cid}")
            st.markdown("### 🔊 Voice Instructions")
            col1, col2 = st.columns([1, 2])

            with col1:
                if st.button("Generate Voice", key=f"btn_{alert.get('id')}"):
                    with st.spinner("Synthesizing..."):
                        if language == "Chinese":
                            summary = alert.get("translated_summary_zh") or alert.get("summary") or ""
                            emergency_actions = alert.get("emergency_actions_zh") or ""
                            if isinstance(emergency_actions, list):
                                emergency_actions = " | ".join(emergency_actions)
                            tts_text = f"{display_title}. {summary}. {emergency_actions}"
                            lang_code = "zh"
                        else:
                            summary = alert.get("translated_summary_en") or alert.get("summary") or ""
                            emergency_actions = alert.get("emergency_actions_en") or ""
                            if isinstance(emergency_actions, list):
                                emergency_actions = " | ".join(emergency_actions)
                            tts_text = f"{display_title}. {summary}. {emergency_actions}"
                            lang_code = "en"

                        try:
                            resp = requests.post(
                                f"{API_BASE_URL}/api/generate-audio/{alert.get('id')}",
                                json={"text": tts_text, "language": lang_code},
                                timeout=60,
                            )
                            if resp.status_code == 200:
                                audio_key = f"audio_{alert.get('id')}_{lang_code}"
                                st.session_state[audio_key] = resp.content
                            else:
                                st.error(f"TTS request failed ({resp.status_code}): {resp.text}")
                        except Exception as e:
                            st.error(f"TTS request failed: {e}")

            # If audio exists, show the player
            lang_code = "zh" if language == "Chinese" else "en"
            audio_key = f"audio_{alert.get('id')}_{lang_code}"
            if audio_key in st.session_state:
                st.audio(st.session_state[audio_key], format="audio/mp3")

