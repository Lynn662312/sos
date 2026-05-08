import feedparser
from app.models import Alert

def fetch_jma_alerts():
    urls = [
        "https://www.data.jma.go.jp/developer/xml/feed/extra.xml", #随時：気象に関する情報のうち、警報・注意報など随時発表されるもの
        "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml", #地震火山：地震、火山に関する情報
        "https://www.data.jma.go.jp/developer/xml/feed/other.xml" #その他：その他の情報
    ]
    alerts = []
    seen_ids = set() # 用于去重
    for url in urls:
        #parse the xml feed and extract the relevant information
        feed = feedparser.parse(url)
        # map xml entry fields to Alert model
        for entry in feed.entries:
            if entry.id in seen_ids:
                continue
            if 'content' in entry:
                description = entry.content[0].value
            elif 'summary' in entry:
                description = entry.summary
            else:
                description = "No details available."
            alert = Alert(
            id=entry.id,
            title=entry.title,
            summary=description,
            link=entry.link,
            updated=entry.updated
        )
        alerts.append(alert)
        seen_ids.add(entry.id)
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
            print(f"Successfully fetched {len(data)} unique alerts.")

            for i in data[:5]: 
                print(f"Time: {i.updated}")
                print(f"Title: {i.title}")
                print(f"Summary: {i.summary[:100]}...") # Print first 100 characters of summary
                print("-" * 50)
    except Exception as e:
        print(f"An error occurred: {e}")
        
 