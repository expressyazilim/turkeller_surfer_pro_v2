
import requests
import numpy as np
import tifffile as tiff
import io

CDSE_URL = "https://sentinelradar.streamlit.app/api/sentinel"
CDSE_TOKEN_URL = "https://sentinelradar.streamlit.app/api/token"

def get_cdse_token(client_id, client_secret):
    resp = requests.post(CDSE_TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    })
    if resp.status_code != 200:
        raise Exception("Token alınamadı")
    return resp.json().get("access_token")

def fetch_sentinel1_tiff(bbox, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(CDSE_URL, json={"bbox": bbox}, headers=headers)
    if resp.status_code != 200:
        raise Exception("Veri alınamadı")
    z = tiff.imread(io.BytesIO(resp.content)).astype(np.float32)
    return z

def run_analysis(lat, lon, çap_metres, token):
    from utils.geo import bbox_from_latlon, box_blur, robust_z
    bbox = bbox_from_latlon(lat, lon, çap_metres)
    Z = fetch_sentinel1_tiff(bbox, token)
    Z_blur = box_blur(Z, k=5)
    Z_z = robust_z(Z_blur)
    return Z, Z_blur, Z_z, bbox
