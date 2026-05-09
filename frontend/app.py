from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import requests
import streamlit as st


API_URL = "http://localhost:8000/api/alerts"
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


def _fetch_alerts() -> list[dict[str, Any]]:
    resp = requests.get(API_URL, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    if not isinstance(payload, list):
        raise ValueError("API returned non-list payload")
    return payload


st.set_page_config(page_title="S.O.S (Source of Safety)", layout="wide")

st.title("S.O.S (Source of Safety)")
st.caption("Instant, Verified Disaster Alerts for Foreigners in Japan.")

col_a, col_b = st.columns([1, 2])
with col_a:
    refresh = st.button("Refresh Alerts", type="primary")
with col_b:
    language = st.selectbox("Display language", options=["English", "Chinese"], index=0)

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if refresh or not st.session_state.alerts:
    try:
        st.session_state.alerts = _fetch_alerts()
        st.success(f"Loaded {len(st.session_state.alerts)} alerts.")
    except Exception as e:
        st.error(f"Failed to fetch alerts from API: {e}")

alerts = st.session_state.alerts or []

if not alerts:
    st.info("No alerts to display yet. Click Refresh Alerts.")
else:
    for alert in alerts:
        title_en = alert.get("translated_title_en") or alert.get("title") or "Untitled"
        title_zh = alert.get("translated_title_zh") or alert.get("title") or "Untitled"

        display_title = title_en if language == "English" else title_zh
        updated_jst = _parse_to_jst(str(alert.get("updated") or ""))

        trust_score = alert.get("trust_score", None)
        trust_label = "Trust Score"
        trust_value = "—" if trust_score is None else f"{trust_score:.1f} / 10"

        expander_label = f"{display_title}  ·  {updated_jst}"
        with st.expander(expander_label, expanded=False):
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
                st.warning(action_text)
            else:
                st.markdown("### Summary")
                st.write(alert.get("translated_summary_zh") or alert.get("summary") or "")
                st.markdown("### 紧急避难行动")
                action_text = alert.get("emergency_actions_zh") or "请保持警惕，等待进一步更新。"
                st.warning(action_text)
        

            st.markdown("### Proof")
            sha = alert.get("hash") or "—"
            cid = alert.get("ipfs_cid") or "—"
            st.write(f"**SHA-256**: `{sha}`")
            st.write(f"**IPFS CID**: `{cid}`")
            if cid != "—":
                st.link_button("Open IPFS Gateway", f"https://gateway.pinata.cloud/ipfs/{cid}")

