import requests
from bs4 import BeautifulSoup
import time
import os
# --- НАСТРОЙКИ ---
URL = "https://testcisia.it/calendario.php?tolc=cents&l=gb&lingua=inglese"
CHECK_EVERY_SECONDS = 60  # Как часто проверять сайт (в секундах)

# Эти значения будут взяты из секретов GitHub, которые мы настроим позже
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

def send_telegram(text: str) -> None:
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(api, json={"chat_id": CHAT_ID, "text": text}, timeout=15)
    if r.status_code != 200:
        print("Telegram error:", r.status_code, r.text)
    r.raise_for_status()

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def find_home_available_rows(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    hits = []
    # Ищем все строки таблицы
    for tr in soup.select("table tr"):
        row_text = tr.get_text(" ", strip=True)
        if not row_text:
            continue
        t = row_text.upper()
        # Если в строке есть и AVAILABLE, и @HOME — это то, что нужно
        if "AVAILABLE" in t and "@HOME" in t:
            hits.append(row_text)
    return hits

def main():
    # Отправляем сообщение о старте, чтобы убедиться, что всё работает
    send_telegram("CISIA watcher started. I will alert you ONLY if CEnT-S@HOME shows AVAILABLE.")
    
    last_fp = None  # Отпечаток последнего найденного слота, чтобы не спамить
    
    while True:
        try:
            html = fetch_html(URL)
            hits = find_home_available_rows(html)
            
            # Создаём "отпечаток" текущих найденных слотов
            fp = "|".join(hits) if hits else ""
            
            # Если слоты есть и они отличаются от предыдущих — шлём уведомление
            if hits and fp != last_fp:
                msg = "SLOT FOUND (CEnT-S@HOME)\n\n" + "\n---\n".join(hits[:3])
                send_telegram(msg)
                last_fp = fp
                
        except Exception as e:
            try:
                send_telegram(f"Watcher error: {e}")
            except:
                pass
        
        time.sleep(CHECK_EVERY_SECONDS)

if __name__ == "__main__":
    main()
