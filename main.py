
import streamlit as st
import numpy as np
import plotly.graph_objs as go
from core.analysis import get_cdse_token, run_analysis
from core.ai import yerel_ai_analizi
from utils.geo import parse_coord_pair, weighted_peak_center
from utils.storage import ai_rapor_kaydet

st.set_page_config(page_title="Turkeller Surfer Pro", layout="wide")
st.markdown('<link rel="stylesheet" href="assets/style.css">', unsafe_allow_html=True)

st.title("📡 Turkeller Surfer Pro")
st.markdown("Yer altı yapı ve boşluk tespiti için Sentinel-1 Z analiz aracı")

with st.sidebar:
    st.header("🔐 API Giriş")
    client_id = st.text_input("Client ID", type="password")
    client_secret = st.text_input("Client Secret", type="password")
    st.markdown("---")
    kords = st.text_input("📍 Koordinat (enlem, boylam)", "37.8719, 32.4841")
    çap = st.slider("📏 Çap (metre)", 100, 1000, 250, step=50)
    analiz_buton = st.button("🚀 Analiz Yap")

if analiz_buton:
    lat, lon = parse_coord_pair(kords)
    if lat is None or lon is None:
        st.error("Geçersiz koordinat formatı.")
        st.stop()

    try:
        token = get_cdse_token(client_id, client_secret)
        Z, Z_blur, Z_z, bbox = run_analysis(lat, lon, çap, token)
    except Exception as e:
        st.error(f"Veri alınamadı: {e}")
        st.stop()

    st.success("✅ Veri alındı ve işlendi")
    st.subheader("📊 Z-Score Heatmap")
    fig2d = go.Figure(data=go.Heatmap(
        z=Z_z,
        colorscale='RdBu',
        colorbar=dict(title="Z"),
        zmid=0
    ))
    st.plotly_chart(fig2d, use_container_width=True)

    st.subheader("🌐 3D Yüzey")
    fig3d = go.Figure(data=[go.Surface(z=Z_z)])
    st.plotly_chart(fig3d, use_container_width=True)

    st.subheader("🧠 AI Yorumlama")
    yorum = yerel_ai_analizi(Z_z)
    st.json(yorum)

    st.subheader("📌 En Güçlü Anomali")
    peak_r, peak_c = np.unravel_index(np.nanargmax(np.abs(Z_z)), Z_z.shape)
    Y, X = np.mgrid[0:Z_z.shape[0], 0:Z_z.shape[1]]
    lat_peak, lon_peak = weighted_peak_center(peak_r, peak_c, Z_z, X, Y)
    st.write(f"📍 Peak koordinat: ({round(lat_peak,6)}, {round(lon_peak,6)})")

    kaydet = st.button("💾 Raporu Kaydet")
    if kaydet:
        rapor = {
            "giris": {"lat": lat, "lon": lon, "cap": çap},
            "peak": {"lat": lat_peak, "lon": lon_peak},
            "yorum": yorum
        }
        ai_rapor_kaydet(rapor)
        st.success("Rapor kaydedildi.")
