import feedparser
import time
from app.models import Alert, TranslatedAlert
from app.utils.hasher import generate_content_hash
from app.translator import _model_to_dict, translate_alert_data
from app.utils.ipfs import upload_to_ipfs
from app.utils.solana import record_provenance_on_chain

PRIORITY = {
    "Critical": 3,
    "Warning": 2,
    "Advisory": 1
}

def fetch_jma_alerts() -> list[Alert]:
    urls = [
        "https://www.data.jma.go.jp/developer/xml/feed/extra.xml", #随時：気象に関する情報のうち、警報・注意報など随時発表されるもの
        "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml", #地震火山：地震、火山に関する情報
        "https://www.data.jma.go.jp/developer/xml/feed/other.xml" #その他：その他の情報
    ]
    alerts: list[Alert] = []
    seen_ids: set[str] = set()  # 用于去重

    all_entries = []
    for url in urls:
        feed = feedparser.parse(url)
        all_entries.extend(getattr(feed, "entries", []))

    # Prefer newest items first across all feeds (ISO-8601 updated strings compare well)
    all_entries.sort(key=lambda e: getattr(e, "updated", ""), reverse=True)

    for entry in all_entries:
        entry_id = getattr(entry, "id", None)
        if not entry_id or entry_id in seen_ids:
            continue

        try:
            if "content" in entry:
                description = entry.content[0].value
            elif "summary" in entry:
                description = entry.summary
            else:
                description = "No details available."

            alert_obj = Alert(
                id=entry_id,
                title=getattr(entry, "title", ""),
                summary=description,
                link=getattr(entry, "link", ""),
                updated=getattr(entry, "updated", ""),
            )

            alerts.append(alert_obj)
            seen_ids.add(entry_id)
        except Exception as e:
            print(f"DEBUG: alert fetch failed for {entry_id}: {e}")
            try:
                # Return at least a minimally-populated Alert so the UI/API can still render.
                if "content" in entry:
                    fallback_summary = entry.content[0].value
                elif "summary" in entry:
                    fallback_summary = entry.summary
                else:
                    fallback_summary = "No details available."

                fallback = Alert(
                    id=entry_id,
                    title=getattr(entry, "title", ""),
                    summary=fallback_summary,
                    link=getattr(entry, "link", ""),
                    updated=getattr(entry, "updated", ""),
                )
                alerts.append(fallback)
                seen_ids.add(entry_id)
            except Exception:
                # If even fallback fails, skip this entry.
                seen_ids.add(entry_id)
                continue
    return alerts


def fetch_jma_alerts_verified(limit: int = 2) -> list[TranslatedAlert]:
    """
    Full pipeline: hash -> translate -> IPFS -> Solana provenance.
    Kept for manual testing; API should prefer Filter-First translation to save quota.
    """
    raw = fetch_jma_alerts()
    verified: list[TranslatedAlert] = []
    for alert in raw[:limit]:
        try:
            content_hash = generate_content_hash(alert.summary)
            alert.hash = content_hash

            translated = translate_alert_data(alert)
            time.sleep(2)

            translated.hash = content_hash
            cid = upload_to_ipfs(_model_to_dict(translated))
            translated.ipfs_cid = cid

            time.sleep(2)
            record_provenance_on_chain(content_hash, cid)

            verified.append(translated)
            time.sleep(2)
        except Exception as e:
            print(f"DEBUG: verify pipeline failed for {alert.id}: {e}")
            verified.append(TranslatedAlert(**_model_to_dict(alert)))

    return verified

if __name__ == "__main__":
    #test the function by fetching and printing the latest alerts
    print("---SOS Project: scraper test ---")
    print("Fetching latest disaster alerts from JMA...")
    try:
        data = fetch_jma_alerts()
        if not data:
            print("No alerts found.")
        else:
            print(f"Successfully fetched {len(data)} processed alerts.")

            for i in data[:5]: 
                print(f"Time: {i.updated}")
                print(f"Title: {i.title}")
                print(f"Summary: {i.summary[:100]}...") # Print first 100 characters of summary
                print(f"Title (JP): {i.title}")
                print(f"Title (EN): {i.translated_title_en}") # New AI Field
                print(f"Summary (ZH): {i.translated_summary_zh[:50]}...") # New AI Field
                print(f"Category: {i.category}") # New AI Field
                print(f"Prefecture: {i.prefecture}") # New AI Field
                print(f"Trust Score: {i.trust_score}/10.0") # New AI Field
                print(f"Hash: {i.hash}")
                print(f"IPFS CID: {i.ipfs_cid}")
                print("-" * 50)
    except Exception as e:
        print(f"An error occurred: {e}")
        
 