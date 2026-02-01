
import numpy as np
import math
import re
from collections import deque

def parse_coord_pair(s: str):
    if not s:
        return None, None
    s = s.strip().replace(",", " ")
    parts = [p for p in s.split() if p.strip()]
    if len(parts) < 2:
        return None, None
    def _to_float(x):
        x = x.strip().replace(",", ".")
        if not re.fullmatch(r"-?\d+(\.\d+)?", x):
            return None
        try:
            return float(x)
        except:
            return None
    lat = _to_float(parts[0])
    lon = _to_float(parts[1])
    if lat is None or lon is None:
        return None, None
    return lat, lon

def bbox_from_latlon(lat, lon, cap_m):
    lat_f = cap_m / 111320.0
    lon_f = cap_m / (40075000.0 * math.cos(math.radians(lat)) / 360.0)
    return [lon - lon_f, lat - lat_f, lon + lon_f, lat + lat_f]

def box_blur(img: np.ndarray, k: int = 3):
    if k <= 1:
        return img
    pad = k // 2
    a = np.pad(img, ((pad, pad), (pad, pad)), mode="edge").astype(np.float32)
    s = np.zeros((a.shape[0] + 1, a.shape[1] + 1), dtype=np.float32)
    s[1:, 1:] = np.cumsum(np.cumsum(a, axis=0), axis=1)
    h, w = img.shape
    out = np.empty((h, w), dtype=np.float32)
    for r in range(h):
        for c in range(w):
            total = s[r + k, c + k] - s[r, c + k] - s[r + k, c] + s[r, c]
            out[r, c] = total / (k * k)
    return out

def robust_z(x: np.ndarray):
    valid = x[~np.isnan(x)]
    if valid.size == 0:
        return x * np.nan
    med = np.median(valid)
    mad = np.median(np.abs(valid - med))
    denom = (1.4826 * mad) if mad > 1e-9 else (np.std(valid) if np.std(valid) > 1e-9 else 1.0)
    return (x - med) / denom

def classic_z(x: np.ndarray):
    valid = x[~np.isnan(x)]
    if valid.size == 0:
        return x * np.nan
    mu = float(np.mean(valid))
    sd = float(np.std(valid)) if float(np.std(valid)) > 1e-9 else 1.0
    return (x - mu) / sd

def estimate_relative_depth(area_px: int, peak_abs_z: float):
    peak = max(peak_abs_z, 1e-6)
    return float(math.sqrt(max(area_px, 1)) / peak)

def weighted_peak_center(peak_r, peak_c, Zz, X, Y, win=1):
    H, W = Zz.shape
    r0 = max(0, peak_r - win); r1 = min(H - 1, peak_r + win)
    c0 = max(0, peak_c - win); c1 = min(W - 1, peak_c + win)
    rr, cc = np.meshgrid(np.arange(r0, r1 + 1), np.arange(c0, c1 + 1), indexing="ij")
    w = np.abs(Zz[rr, cc]).astype(np.float64)
    s = float(np.sum(w))
    if s <= 1e-12:
        return float(Y[peak_r, peak_c]), float(X[peak_r, peak_c])
    lat = float(np.sum(w * Y[rr, cc]) / s)
    lon = float(np.sum(w * X[rr, cc]) / s)
    return lat, lon
