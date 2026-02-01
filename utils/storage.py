
import json
import os
from datetime import datetime

RAPOR_KLASORU = "ai_raporlari"

def ai_raporlari_yukle():
    if not os.path.exists(RAPOR_KLASORU):
        return []
    raporlar = []
    for dosya in sorted(os.listdir(RAPOR_KLASORU), reverse=True):
        if dosya.endswith(".json"):
            tam_yol = os.path.join(RAPOR_KLASORU, dosya)
            with open(tam_yol, "r", encoding="utf-8") as f:
                try:
                    raporlar.append(json.load(f))
                except:
                    continue
    return raporlar

def ai_rapor_kaydet(veri: dict):
    if not os.path.exists(RAPOR_KLASORU):
        os.makedirs(RAPOR_KLASORU)
    tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosya_adi = f"rapor_{tarih}.json"
    tam_yol = os.path.join(RAPOR_KLASORU, dosya_adi)
    with open(tam_yol, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
