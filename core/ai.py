
import numpy as np

def yerel_ai_analizi(Zz: np.ndarray):
    flat = Zz.flatten()
    flat = flat[~np.isnan(flat)]
    if flat.size == 0:
        return {
            "ortalama_z": 0.0,
            "max_z": 0.0,
            "anlam": "Veri yok"
        }

    ortalama = float(np.mean(flat))
    max_z = float(np.max(flat))
    yorum = "Düşük seviyeli yüzey farkı"

    if max_z > 3.5:
        yorum = "Yüksek olasılıkla yapı/parazit farkı"
    elif max_z > 2.0:
        yorum = "Orta düzeyde olası anomali"
    elif max_z < -2.5:
        yorum = "Negatif Z yoğunluğu - boşluk/tünel olabilir"

    return {
        "ortalama_z": round(ortalama, 3),
        "max_z": round(max_z, 3),
        "anlam": yorum
    }
