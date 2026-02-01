def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                # Dosya boşsa otomatik olarak liste döndür
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        # Dosya bozuksa da sıfırla
        return []
    except Exception:
        return []
