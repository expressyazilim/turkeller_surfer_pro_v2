
import streamlit as st
from core.analysis import run_analysis, get_cdse_token
from core.ai import yerel_ai_analizi
from utils.geo import zscore_to_heatmap, zscore_to_surface, plot_map
from utils.storage import save_report, load_history
import datetime
import json

st.set_page_config(layout="wide", page_title="Turkeller Surfer Pro")

st.title("📡 Turkeller Surfer Pro")
st.markdown("Yer altı yapılarını Sentinel-1 ile analiz edin")

# API bilgileri secrets.toml'den
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

# Sidebar
with st.sidebar:
    st.header("📍 Konum Ayarları")
    lat = st.number_input("Enlem (lat)", value=38.5, format="%.6f")
    lon = st.number_input("Boylam (lon)", value=27.2, format="%.6f")
    çap = st.slider("Tarama Çapı (metre)", 100, 1000, 300, step=50)

    if st.button("📡 Analiz Başlat"):
        try:
            token = get_cdse_token(client_id, client_secret)
            Z, Z_blur, Z_z, bbox = run_analysis(lat, lon, çap, token)
            st.session_state["Z_z"] = Z_z
            st.session_state["bbox"] = bbox
            st.session_state["latlon"] = (lat, lon)
            st.success("✅ Anomali analizi tamamlandı.")
        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")

# Analiz sonrası görseller ve AI yorum
if "Z_z" in st.session_state:
    Z_z = st.session_state["Z_z"]
    bbox = st.session_state["bbox"]

    st.subheader("🗺️ 2D Z-Skor Haritası")
    st.pyplot(zscore_to_heatmap(Z_z))

    st.subheader("🌐 3D Yüzey Görselleştirme")
    st.plotly_chart(zscore_to_surface(Z_z), use_container_width=True)

    st.subheader("🤖 AI Yorum")
    yorum = yerel_ai_analizi(Z_z)
    st.json(yorum)

    # Rapor kaydet
    if st.button("💾 Raporu Kaydet"):
        konum = {
            "lat": st.session_state["latlon"][0],
            "lon": st.session_state["latlon"][1],
            "z_max": float(Z_z.max()),
            "z_min": float(Z_z.min()),
            "timestamp": datetime.datetime.now().isoformat()
        }
        save_report(konum)
        st.success("Rapor kaydedildi.")

    # Anomaliye git
    st.markdown("### 🎯 Anomali Odaklama")
    z_max_loc = divmod(Z_z.argmax(), Z_z.shape[1])
    z_min_loc = divmod(Z_z.argmin(), Z_z.shape[1])
    if st.button("📍 Pozitif Anomaliye Git"):
        st.map([{
            "lat": bbox[1] + (bbox[3] - bbox[1]) * z_max_loc[0] / Z_z.shape[0],
            "lon": bbox[0] + (bbox[2] - bbox[0]) * z_max_loc[1] / Z_z.shape[1]
        }])
    if st.button("📍 Negatif Anomaliye Git"):
        st.map([{
            "lat": bbox[1] + (bbox[3] - bbox[1]) * z_min_loc[0] / Z_z.shape[0],
            "lon": bbox[0] + (bbox[2] - bbox[0]) * z_min_loc[1] / Z_z.shape[1]
        }])

# Geçmiş konumlar
st.sidebar.markdown("### 📂 Geçmiş Taramalar")
for item in load_history():
    with st.sidebar.expander(f"{item['timestamp'].split('T')[0]} @ {item['lat']:.4f},{item['lon']:.4f}"):
        st.write(f"Z-max: {item['z_max']:.2f}, Z-min: {item['z_min']:.2f}")
        if st.button("📍 Haritada Göster", key=item['timestamp']):
            st.map([{"lat": item["lat"], "lon": item["lon"]}])
