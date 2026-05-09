import feedparser
from app.models import Alert, TranslatedAlert
import time
from app.utils.hasher import generate_content_hash
from app.translator import _model_to_dict, translate_alert_data
from app.utils.ipfs import upload_to_ipfs
from app.utils.solana import record_provenance_on_chain

PRIORITY = {
    "Critical": 3,
    "Warning": 2,
    "Advisory": 1
}

def fetch_jma_alerts():
    urls = [
        "https://www.data.jma.go.jp/developer/xml/feed/extra.xml", #随時：気象に関する情報のうち、警報・注意報など随時発表されるもの
        "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml", #地震火山：地震、火山に関する情報
        "https://www.data.jma.go.jp/developer/xml/feed/other.xml" #その他：その他の情報
    ]
    alerts: list[TranslatedAlert] = []
    seen_ids: set[str] = set()  # 用于去重

    all_entries = []
    for url in urls:
        feed = feedparser.parse(url)
        all_entries.extend(getattr(feed, "entries", []))

    # Prefer newest items first across all feeds (ISO-8601 updated strings compare well)
    all_entries.sort(key=lambda e: getattr(e, "updated", ""), reverse=True)

    PRIORITY = { "Critical": 3, "Warning": 2, "Advisory": 1 }
    # Efficiency guard: only process the 3 most recent unique alerts
    for entry in all_entries:
        if len(alerts) >= 3:
            break

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

            # Step A: hash raw content (use summary/description as canonical text)
            content_hash = generate_content_hash(alert_obj.summary)
            alert_obj.hash = content_hash

            # Step B: translate into TranslatedAlert
            translated = translate_alert_data(alert_obj)
            time.sleep(2)  # brief pause to respect API rate limits

            # Step C: upload translated alert as JSON to IPFS
            translated.hash = content_hash
            ipfs_cid = upload_to_ipfs(_model_to_dict(translated))

            # Step D: record provenance on Solana (best-effort)
            time.sleep(2)  # brief pause to respect API rate limits
            record_provenance_on_chain(content_hash, ipfs_cid)

            # Step E: update final object with CID + hash
            translated.ipfs_cid = ipfs_cid
            translated.hash = content_hash
            alerts.append(translated)
            seen_ids.add(entry_id)
            time.sleep(2)  # brief pause before processing next alert   
        except Exception as e:
            # Per-entry failure should not crash the scraper (rate limits/timeouts/etc.)
            print(f"DEBUG: alert pipeline failed for {entry_id}: {e}")
            try:
                # Return at least a minimally-populated TranslatedAlert so the UI/API can still render.
                if "content" in entry:
                    fallback_summary = entry.content[0].value
                elif "summary" in entry:
                    fallback_summary = entry.summary
                else:
                    fallback_summary = "No details available."

                fallback_hash = None
                try:
                    fallback_hash = generate_content_hash(fallback_summary)
                except Exception:
                    fallback_hash = None

                fallback = TranslatedAlert(
                    id=entry_id,
                    title=getattr(entry, "title", ""),
                    summary=fallback_summary,
                    link=getattr(entry, "link", ""),
                    updated=getattr(entry, "updated", ""),
                    hash=fallback_hash,
                )
                alerts.append(fallback)
                seen_ids.add(entry_id)
            except Exception:
                # If even fallback fails, skip this entry.
                seen_ids.add(entry_id)
                continue
    alerts.sort(key=lambda x: (PRIORITY.get(x.category, 0), x.trust_score or 0), reverse=True)           
    return alerts

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
        
 