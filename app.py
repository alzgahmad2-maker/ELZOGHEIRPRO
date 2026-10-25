import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import math
import asyncio
import requests
import os
import platform
import shutil
import subprocess
import threading
from datetime import datetime, timezone
from streamlit_js_eval import streamlit_js_eval
from pocketoptionapi_async import AsyncPocketOptionClient

# ============================================================
# 1. إعدادات الصفحة والتصميم (CSS) - ELZOGHEIR VIP
# ============================================================
st.set_page_config(page_title="ELZOGHEIR CANDLE-VIP", page_icon="👑", layout="wide")

if not hasattr(st, "fragment"):
    st.error("هذا الإصدار يحتاج Streamlit 1.37 أو أحدث. نفّذ: py -m pip install -U streamlit")
    st.stop()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    .stApp { background: radial-gradient(circle at top, #0A0E17 0%, #000000 100%); font-family: 'Cairo', sans-serif; }
    
    .main-header { font-size: 2.8rem; color: #FFD700; text-align: center; font-weight: 900; text-shadow: 0 0 20px rgba(255, 215, 0, 0.6); margin-bottom: 0; }
    .sub-header { font-size: 1.1rem; color: #8899AA; text-align: center; margin-bottom: 2rem; letter-spacing: 3px; }
    
    .metric-card { background: linear-gradient(135deg, #121826 0%, #0A0E17 100%); border: 1px solid #1F2A3C; border-radius: 15px; padding: 1rem 0.5rem; text-align: center; box-shadow: 0 4px 20px rgba(0, 255, 170, 0.05); display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 110px; }
    .metric-label { color: #8899AA; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 700; }
    .metric-value { font-size: 1.3rem; font-weight: 900; white-space: nowrap; }
    
    .buy-signal { color: #00FFAA; text-shadow: 0 0 10px rgba(0,255,170,0.4); }
    .sell-signal { color: #FF3355; text-shadow: 0 0 10px rgba(255,51,85,0.4); }
    .neutral-signal { color: #FFCC00; }
    
    .countdown-box { background: linear-gradient(135deg, #1F2A3C 0%, #0A0E17 100%); border: 2px solid #FFD700; border-radius: 15px; padding: 1.5rem; text-align: center; margin: 1rem 0; box-shadow: 0 0 25px rgba(255,215,0,0.4); }
    .countdown-time { font-size: 3.5rem; font-weight: 900; color: #FFD700; text-shadow: 0 0 15px rgba(255,215,0,0.8); margin: 0; }
    .countdown-label { color: #8899AA; font-size: 1.1rem; margin-bottom: 0.5rem; }
    
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #0A0E17 0%, #050810 100%); border-right: 1px solid #1F2A3C; }
    .stButton>button { background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); color: #000; font-weight: 700; border: none; border-radius: 10px; padding: 0.6rem 1.5rem; width: 100%; }
    .stButton>button:hover { box-shadow: 0 0 15px rgba(255, 215, 0, 0.6); transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# إضافات التصميم (أنميشن + لودنج + قوة الإشارة) - مضافة فقط دون تعديل ما سبق
st.markdown("""
<style>
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes sweep { 0% { left: -40%; } 100% { left: 100%; } }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
    @keyframes glowPulse { 0%,100% { box-shadow: 0 0 12px rgba(255,215,0,0.25); } 50% { box-shadow: 0 0 30px rgba(255,215,0,0.65); } }
    @keyframes blinkRed { 0%,100% { border-color: #FFD700; } 50% { border-color: #FF3355; } }

    .metric-card { animation: fadeUp 0.5s ease both; }
    .countdown-box { animation: fadeUp 0.4s ease both, glowPulse 2s ease-in-out infinite; }
    .countdown-box.urgent { animation: fadeUp 0.4s ease both, blinkRed 0.8s ease-in-out infinite; }

    .loader-box { background: linear-gradient(135deg, #121826 0%, #0A0E17 100%); border: 1px solid #1F2A3C; border-radius: 15px; padding: 1.5rem; text-align: center; margin: 1rem 0; animation: glowPulse 2s ease-in-out infinite; }
    .loader-ring { width: 58px; height: 58px; margin: 0 auto 12px auto; border: 4px solid #1F2A3C; border-top-color: #FFD700; border-right-color: #00FFAA; border-radius: 50%; animation: spin 0.9s linear infinite; }
    .loader-title { color: #FFD700; font-weight: 900; font-size: 1.2rem; }
    .loader-sub { color: #8899AA; font-size: 0.9rem; margin: 0.3rem 0 1rem 0; }
    .loader-track { position: relative; height: 6px; background: #1F2A3C; border-radius: 6px; overflow: hidden; }
    .loader-sweep { position: absolute; top: 0; height: 100%; width: 40%; background: linear-gradient(90deg, transparent, #FFD700, transparent); animation: sweep 1.2s ease-in-out infinite; }
    .loader-fill { height: 100%; background: linear-gradient(90deg, #FFD700, #00FFAA); transition: width 0.3s ease; }

    .signal-row { display: flex; align-items: center; justify-content: center; gap: 16px; flex-wrap: wrap; }
    .strength-badge { font-size: 1.4rem; font-weight: 900; border: 2px solid; border-radius: 12px; padding: 2px 14px; }
    .strength-track { width: 80%; height: 8px; background: #1F2A3C; border-radius: 8px; margin: 10px 0; overflow: hidden; }
    .strength-fill { height: 100%; border-radius: 8px; transition: width 0.6s ease; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">👑 ELZOGHEIR CANDLE-VIP</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">ULTIMATE TRADING SYSTEM • 40 PAIRS • MULTI-TIMEFRAME</div>', unsafe_allow_html=True)

# ============================================================
# 2. بيانات الاعتماد والإعدادات (من st.secrets أو متغيرات البيئة - لا أسرار داخل الكود)
# ============================================================
def get_secret(name, default=""):
    value = None
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return str(value) if value else os.environ.get(name, default)

SSID = '42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"8508fc1e421f36919693a93145d54072\";s:10:\"ip_address\";s:13:\"46.248.203.43\";s:10:\"user_agent\";s:111:\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36\";s:13:\"last_activity\";i:1792966820;}ecbf3ea7ccf3760174c639ab0afb811a","isDemo":0,"uid":138770488,"platform":2,"isFastHistory":true,"isOptimized":true}]'
TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = get_secret("TELEGRAM_CHAT_ID")
CSV_FILE = "elzogheir_vip_log.csv"
RECENT_CANDLES = 3  # الأنماط المعتبرة في الإشارة = آخر 3 شموع فقط

PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "USDCAD_otc",
    "USDCHF_otc", "NZDUSD_otc", "EURGBP_otc", "EURJPY_otc", "GBPJPY_otc",
    "AUDCAD_otc", "AUDJPY_otc", "CADJPY_otc", "CHFJPY_otc", "EURCAD_otc",
    "EURAUD_otc", "GBPAUD_otc", "GBPCAD_otc", "XAUUSD_otc", "BTCUSD_otc",
    # 20 زوج إضافي
    "AUDCHF_otc", "AUDNZD_otc", "CADCHF_otc", "EURCHF_otc", "EURNZD_otc",
    "GBPCHF_otc", "GBPNZD_otc", "NZDCAD_otc", "NZDCHF_otc", "NZDJPY_otc",
    "USDSGD_otc", "USDCNH_otc", "USDINR_otc", "USDTRY_otc", "USDBRL_otc",
    "USDMXN_otc", "XAGUSD_otc", "ETHUSD_otc", "LTCUSD_otc", "USDEGP_otc"
]

def open_calculator():
    """يفتح الآلة الحاسبة على الجهاز الذي يعمل عليه البرنامج (اللابتوب)."""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(["calc.exe"])
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", "Calculator"])
        else:
            for cmd in ["gnome-calculator", "kcalc", "mate-calc", "xcalc"]:
                if shutil.which(cmd):
                    subprocess.Popen([cmd])
                    return True, ""
            return False, "لم أجد آلة حاسبة مثبتة على النظام"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

# ============================================================
# 3. الشريط الجانبي
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ إعدادات VIP")
    symbol = st.selectbox("الزوج / الأصل (40 زوج)", PAIRS)
    period = st.selectbox("الإطار الزمني", 
        [15, 30, 60, 180, 300, 900, 1800], 
        format_func=lambda x: {15: "15 ثانية", 30: "30 ثانية", 60: "دقيقة", 180: "3 دقائق", 300: "5 دقائق", 900: "15 دقيقة", 1800: "30 دقيقة"}[x],
        index=2
    )
    max_candles = 200
    
    st.markdown("---")
    st.markdown("### 🛡️ إدارة المخاطر")
    base_stake = st.number_input("حجم الدخول الأساسي ($)", min_value=1.0, value=1.0, step=1.0)
    martingale_mode = st.checkbox("تفعيل المضاعفة (Martingale)", value=False)
    martingale_max_steps = st.number_input("أقصى مراحل المضاعفة", min_value=1, max_value=6, value=3, step=1, disabled=not martingale_mode)
    
    st.markdown("---")
    st.markdown("### 🔔 الميزات")
    enable_telegram = st.checkbox("إشعارات تيليجرام", value=False)
    enable_sound = st.checkbox("تنبيه صوتي", value=True)
    pre_alert_seconds = st.number_input("التنبيه قبل موعد الدخول (ثانية)", min_value=5, max_value=120, value=30, step=5)
    enable_auto_refresh = st.checkbox("تحديث تلقائي (60 ث)", value=False)
    
    st.markdown("---")
    if st.button("🚀 جلب صفقة", use_container_width=True):
        st.session_state['run_scan'] = True
        st.session_state['do_fetch'] = True
        
    if st.button("🔍 مسح السوق (Scanner)", use_container_width=True):
        st.session_state['run_scanner'] = True

    if st.button("🧮 فتح الآلة الحاسبة", use_container_width=True):
        ok, err = open_calculator()
        if ok:
            st.toast("تم فتح الآلة الحاسبة", icon="🧮")
        else:
            st.toast(f"تعذر فتح الآلة الحاسبة: {err}", icon="⚠️")

    if st.button("🗑️ مسح الذاكرة", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

if not SSID:
    st.error("🔐 لم يتم ضبط SSID. أنشئ الملف .streamlit/secrets.toml (انظر secrets.toml.example) أو عرّف متغير البيئة SSID.")
    st.stop()

higher_tf = 300 if period < 300 else (900 if period < 900 else 3600)

# ============================================================
# 4. دوال مساعدة (جلب البيانات / التنبيهات / اللودنج)
# ============================================================
def play_sound(tag="evt"):
    if enable_sound:
        streamlit_js_eval(js_expressions="new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg').play()", key=f"sound_{tag}_{time.time_ns()}")

def send_telegram_alert(message):
    """يرجع (نجاح، رسالة_خطأ). لا يخفي الأخطاء."""
    if not enable_telegram:
        return False, ""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False, "توكن/معرّف تيليجرام غير مضبوط في secrets"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=5)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def notify(title, tg_message=None, tag="evt"):
    st.toast(title, icon="⏰")
    play_sound(tag)
    if tg_message:
        ok, err = send_telegram_alert(tg_message)
        if not ok and err:
            st.toast(f"تيليجرام: {err}", icon="⚠️")

def show_loader(slot, title, sub, pct=None):
    if pct is None:
        bar = '<div class="loader-track"><div class="loader-sweep"></div></div>'
    else:
        bar = f'<div class="loader-track"><div class="loader-fill" style="width:{pct:.0f}%;"></div></div>'
    slot.markdown(
        f'<div class="loader-box"><div class="loader-ring"></div>'
        f'<div class="loader-title">{title}</div><div class="loader-sub">{sub}</div>{bar}</div>',
        unsafe_allow_html=True
    )

def to_epoch(series):
    return ((series - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)).astype("int64")

def build_df(candles, max_candles):
    if not candles:
        return None
    data = [{'time': c.timestamp, 'open': c.open, 'high': c.high, 'low': c.low, 'close': c.close} for c in candles]
    df = pd.DataFrame(data)
    try:
        df['time'] = pd.to_datetime(df['time'], unit='s')
    except Exception:
        df['time'] = pd.to_datetime(df['time'])
    if getattr(df['time'].dt, 'tz', None) is not None:
        df['time'] = df['time'].dt.tz_convert('UTC').dt.tz_localize(None)
    for col in ['open', 'high', 'low', 'close']:
        df[col] = df[col].astype(float)
    df = df.sort_values('time').drop_duplicates('time').tail(max_candles).reset_index(drop=True)
    df['ts'] = to_epoch(df['time'])
    return df

async def _fetch_many_async(requests_list, progress_cb=None):
    """اتصال واحد يُعاد استخدامه لكل الطلبات + عزل الأخطاء لكل زوج."""
    results, errors = {}, {}
    client = AsyncPocketOptionClient(SSID, is_demo=True)
    try:
        await client.connect()
    except Exception as e:
        return {}, {"connection": f"{type(e).__name__}: {e}"}
    try:
        total = len(requests_list)
        for n, (sym, tf, cnt) in enumerate(requests_list, 1):
            try:
                candles = await client.get_candles(asset=sym, timeframe=tf, count=cnt)
                df = build_df(candles, cnt)
                if df is None or len(df) == 0:
                    errors[(sym, tf)] = "لا توجد بيانات"
                else:
                    results[(sym, tf)] = df
            except Exception as e:
                errors[(sym, tf)] = f"{type(e).__name__}: {e}"
            if progress_cb:
                progress_cb(n, total, sym)
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
    return results, errors

def fetch_many(requests_list, progress_cb=None):
    unique = list(dict.fromkeys(requests_list))
    try:
        return asyncio.run(_fetch_many_async(unique, progress_cb))
    except Exception as e:
        return {}, {"error": f"{type(e).__name__}: {e}"}

# ============================================================
# 5. المؤشرات والأنماط
# ============================================================
def calculate_indicators(df):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal_Line']
    df['EMA200'] = df['close'].ewm(span=200, adjust=False).mean()

    # ATR لفلتر التذبذب
    prev_close = df['close'].shift(1)
    tr = pd.concat([df['high'] - df['low'], (df['high'] - prev_close).abs(), (df['low'] - prev_close).abs()], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=14).mean()
    return df

def detect_patterns(df):
    patterns = []
    for i in range(3, len(df)):
        o, h, l, c = df.loc[i, ["open", "high", "low", "close"]].astype(float)
        po, pc = df.loc[i-1, ["open", "close"]].astype(float)
        ppo, ppc = df.loc[i-2, ["open", "close"]].astype(float)
        body = abs(c - o); range_ = h - l + 1e-9
        upper_wick = h - max(o, c); lower_wick = min(o, c) - l
        
        if body / range_ < 0.1: patterns.append((i, "Doji", "neutral"))
        elif lower_wick > 2 * body and upper_wick < body * 0.5: patterns.append((i, "Hammer", "buy"))
        elif upper_wick > 2 * body and lower_wick < body * 0.5: patterns.append((i, "Shooting Star", "sell"))
        elif pc < po and c > o and c > po and o < pc: patterns.append((i, "Bullish Engulfing", "buy"))
        elif pc > po and c < o and c < po and o > pc: patterns.append((i, "Bearish Engulfing", "sell"))
        elif (ppc < ppo) and (abs(pc - po) / (po + 1e-9) < 0.001) and (c > o) and (c > (ppo + ppc)/2): patterns.append((i, "Morning Star", "buy"))
        elif (ppc > ppo) and (abs(pc - po) / (po + 1e-9) < 0.001) and (c < o) and (c < (ppo + ppc)/2): patterns.append((i, "Evening Star", "sell"))
    return patterns

# ============================================================
# 6. منطق الإشارة (فلترة الجلسات والاتجاه + نسبة قوة الإشارة)
# ============================================================
PATTERN_WEIGHTS = {
    "Doji": 0, "Hammer": 1.5, "Shooting Star": 1.5,
    "Bullish Engulfing": 2, "Bearish Engulfing": 2,
    "Morning Star": 3, "Evening Star": 3,
}

def strength_color(s):
    return "#00FFAA" if s >= 75 else "#FFCC00" if s >= 50 else "#FF3355"

def generate_signal(patterns, df, higher_tf_df):
    """يرجع: (الإشارة، عدد الشراء، عدد البيع، السبب، قوة الإشارة %)"""
    n = len(df)
    # فقط الأنماط الحديثة (آخر RECENT_CANDLES شموع) وليس كل التاريخ
    recent = [p for p in patterns if p[0] >= n - RECENT_CANDLES]
    buys = sum(1 for _, _, s in recent if s == "buy")
    sells = sum(1 for _, _, s in recent if s == "sell")
    buy_w = sum(PATTERN_WEIGHTS.get(nm, 1) for _, nm, s in recent if s == "buy")
    sell_w = sum(PATTERN_WEIGHTS.get(nm, 1) for _, nm, s in recent if s == "sell")

    if buy_w == sell_w:
        return "NEUTRAL", buys, sells, "لا توجد إشارة", 0

    is_buy = buy_w > sell_w
    last_rsi = float(df['RSI'].iloc[-1]); last_macd = float(df['MACD_Hist'].iloc[-1])
    last_close = float(df['close'].iloc[-1]); last_ema = float(df['EMA200'].iloc[-1])
    last_atr = float(df['ATR'].iloc[-1]) if 'ATR' in df else float('nan')

    # فلترة الجلسة (تجنب أوقات السيولة المنخفضة)
    current_hour = datetime.now(timezone.utc).hour
    is_active_session = 7 <= current_hour <= 21  # جلسات لندن ونيويورك

    # الاتجاه في الإطار الأكبر
    higher_known = higher_tf_df is not None and len(higher_tf_df) > 0
    higher_trend = None
    if higher_known:
        higher_close = higher_tf_df['close'].iloc[-1]
        higher_ema = higher_tf_df['close'].ewm(span=200, adjust=False).mean().iloc[-1]
        higher_trend = "UP" if higher_close > higher_ema else "DOWN"

    # فلتر التذبذب: تجنب الأسواق الراكدة
    atr_hist = df['ATR'].dropna().tail(100) if 'ATR' in df else pd.Series(dtype=float)
    vol_ok = len(atr_hist) >= 20 and not math.isnan(last_atr) and last_atr >= 0.5 * float(atr_hist.median())

    if is_buy:
        rsi_ok = (not math.isnan(last_rsi)) and last_rsi < 70
        rsi_comfort = rsi_ok and last_rsi <= 60
        macd_ok = (not math.isnan(last_macd)) and last_macd > 0
        ema_ok = last_close > last_ema
        higher_ok = higher_known and higher_trend == "UP"
    else:
        rsi_ok = (not math.isnan(last_rsi)) and last_rsi > 30
        rsi_comfort = rsi_ok and last_rsi >= 40
        macd_ok = (not math.isnan(last_macd)) and last_macd < 0
        ema_ok = last_close < last_ema
        higher_ok = higher_known and higher_trend == "DOWN"

    # حساب القوة (من 100)
    pattern_pts = min(30, 12 + abs(buy_w - sell_w) * 6)
    score = pattern_pts
    score += 10 if rsi_comfort else 5 if rsi_ok else 0
    score += 15 if macd_ok else 0
    score += 15 if ema_ok else 0
    score += 15 if higher_ok else (7 if not higher_known else 0)
    score += 5 if is_active_session else 0
    score += 10 if vol_ok else 0
    strength = int(round(min(100, score)))

    strong = rsi_ok and macd_ok and ema_ok and higher_ok and is_active_session and vol_ok
    side_ar = "شراء" if is_buy else "بيع"
    if strong:
        label = "STRONG BUY" if is_buy else "STRONG SELL"
        return label, buys, sells, "توافق كامل (أنماط + RSI + MACD + EMA + إطار أكبر + جلسة + تذبذب)", strength

    missing = []
    if not rsi_ok: missing.append("RSI")
    if not macd_ok: missing.append("MACD")
    if not ema_ok: missing.append("EMA200")
    if not higher_known: missing.append("الإطار الأكبر غير متاح")
    elif not higher_ok: missing.append("عكس اتجاه الإطار الأكبر")
    if not is_active_session: missing.append("جلسة غير نشطة")
    if not vol_ok: missing.append("تذبذب ضعيف")
    reason = f"أنماط {side_ar} فقط" + (f" — ينقصها: {'، '.join(missing)}" if missing else " (بدون تأكيد)")
    return ("WEAK BUY" if is_buy else "WEAK SELL"), buys, sells, reason, strength

# ============================================================
# 7. إدارة السجل والتحليلات (آمن ضد التلف + تقييم دقيق لكل زوج)
# ============================================================
LOG_COLUMNS = ["Time", "Symbol", "Signal", "Strength", "Entry", "Expiry", "EntryTS", "ExpiryTS", "Timeframe", "Stake", "Result", "Close"]
_log_lock = threading.Lock()

def load_log():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=LOG_COLUMNS)
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception:
        return pd.DataFrame(columns=LOG_COLUMNS)
    for col in LOG_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
    for col in ["EntryTS", "ExpiryTS", "Timeframe", "Entry", "Close", "Stake", "Strength"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Result"] = df["Result"].astype(object)
    # صفقات قديمة بلا طوابع زمنية لا يمكن تقييمها بدقة
    legacy = (df["Result"] == "PENDING") & df["ExpiryTS"].isna()
    df.loc[legacy, "Result"] = "UNKNOWN"
    return df[LOG_COLUMNS]

def save_log(df):
    tmp = CSV_FILE + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, CSV_FILE)  # كتابة ذرّية لتفادي تلف الملف

def log_trade(symbol, signal, strength, signal_price, timeframe, stake, entry_ts):
    row = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Symbol": symbol, "Signal": signal,
        "Strength": strength, "Entry": signal_price,
        "Expiry": datetime.fromtimestamp(entry_ts + timeframe).strftime("%Y-%m-%d %H:%M:%S"),
        "EntryTS": entry_ts, "ExpiryTS": entry_ts + timeframe, "Timeframe": timeframe,
        "Stake": stake, "Result": "PENDING", "Close": np.nan,
    }
    with _log_lock:
        df = load_log()
        new = pd.DataFrame([row], columns=LOG_COLUMNS)
        df = new if df.empty else pd.concat([df, new], ignore_index=True)
        save_log(df)

def has_pending(symbol):
    df = load_log()
    return bool(((df["Symbol"] == symbol) & (df["Result"] == "PENDING")).any())

def evaluate_trades():
    """يقيّم كل صفقة بسعر زوجها هي: شمعة الدخول (فتح) مقابل إغلاقها."""
    with _log_lock:
        df = load_log()
    now_ts = time.time()
    due = df[(df["Result"] == "PENDING") & (df["ExpiryTS"] + 2 <= now_ts)]
    if due.empty:
        return False

    reqs = []
    for (sym, tf), grp in due.groupby(["Symbol", "Timeframe"]):
        tf = int(tf)
        oldest = float(grp["EntryTS"].min())
        cnt = int(min(200, max(5, (now_ts - oldest) // tf + 3)))
        reqs.append((sym, tf, cnt))
    results, _ = fetch_many(reqs)
    if not results:
        return False

    updates = []
    for _, row in due.iterrows():
        tf = int(row["Timeframe"])
        cdf = results.get((row["Symbol"], tf))
        if cdf is None:
            continue
        m = cdf[cdf["ts"] == int(row["EntryTS"])]
        if m.empty:
            if now_ts - float(row["ExpiryTS"]) > 200 * tf:
                updates.append((row["Symbol"], int(row["EntryTS"]), "UNKNOWN", np.nan, np.nan))
            continue
        o = float(m.iloc[0]["open"]); c = float(m.iloc[0]["close"])
        if c == o:
            result = "DRAW"
        elif ("BUY" in row["Signal"] and c > o) or ("SELL" in row["Signal"] and c < o):
            result = "WIN"
        else:
            result = "LOSS"
        updates.append((row["Symbol"], int(row["EntryTS"]), result, o, c))

    if not updates:
        return False
    with _log_lock:
        df = load_log()
        for sym, ets, result, o, c in updates:
            mask = (df["Symbol"] == sym) & (df["EntryTS"] == ets) & (df["Result"] == "PENDING")
            df.loc[mask, "Result"] = result
            if not math.isnan(o):
                df.loc[mask, "Entry"] = o
                df.loc[mask, "Close"] = c
        save_log(df)
    return True

def compute_stake(base, martingale, max_steps):
    """مضاعفة محدودة: تتصاعد بعد كل خسارة متتالية حتى السقف وتعود للأساس بعد أي ربح."""
    if not martingale:
        return base
    df = load_log()
    completed = df[df["Result"].isin(["WIN", "LOSS"])]
    streak = 0
    for r in reversed(completed["Result"].tolist()):
        if r == "LOSS":
            streak += 1
        else:
            break
    return base * (2 ** min(streak, int(max_steps)))

# ============================================================
# 8. الرسم البياني وتصدير الصورة
# ============================================================
def plot_chart(df, patterns, symbol):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.2, 0.2], subplot_titles=(f"{symbol}", "RSI (14)", "MACD"))
    fig.add_trace(go.Candlestick(x=df["time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], increasing_line_color="#00FFAA", increasing_fillcolor="#00FFAA", decreasing_line_color="#FF3355", decreasing_fillcolor="#FF3355", name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["EMA200"], name="EMA 200", line=dict(color="#FFD700", width=2)), row=1, col=1)
    for i, name, sig in patterns:
        color = {"buy": "#00FFAA", "sell": "#FF3355", "neutral": "#FFCC00"}[sig]
        y = df.loc[i, "high"] if sig != "buy" else df.loc[i, "low"]
        fig.add_trace(go.Scatter(x=[df.loc[i, "time"]], y=[y], mode="markers+text", text=[name.split()[0]], textposition="top center", marker=dict(symbol="star", size=12, color=color), textfont=dict(color=color, size=9), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["RSI"], name="RSI", line=dict(color="#FFCC00", width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#FF3355", row=2, col=1); fig.add_hline(y=30, line_dash="dash", line_color="#00FFAA", row=2, col=1)
    fig.add_trace(go.Bar(x=df["time"], y=df["MACD_Hist"], name="MACD Hist", marker_color=np.where(df["MACD_Hist"] > 0, "#00FFAA", "#FF3355")), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["MACD"], name="MACD", line=dict(color="#00AAFF", width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["Signal_Line"], name="Signal", line=dict(color="#FF8800", width=1.5)), row=3, col=1)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,14,23,0.6)", xaxis_rangeslider_visible=False, height=700, margin=dict(l=20, r=20, t=40, b=20), font=dict(family="Cairo", color="#CCCCCC"), hovermode="x unified", showlegend=False)
    fig.update_xaxes(gridcolor="#1F2A3C"); fig.update_yaxes(gridcolor="#1F2A3C", side="right")
    return fig

def export_chart_image(fig, symbol):
    # التوليد عند الطلب فقط (kaleido بطيء ولا يجب تشغيله مع كل تحديث)
    if st.button("📸 تجهيز صورة الرسم البياني", key="prep_img", use_container_width=True):
        try:
            st.session_state['chart_png'] = (symbol, fig.to_image(format="png", width=1200, height=700, scale=2))
        except Exception:
            st.session_state.pop('chart_png', None)
            st.info("لتحميل الصورة، تأكد من تثبيت مكتبة kaleido: py -m pip install kaleido")
    saved = st.session_state.get('chart_png')
    if saved:
        sym, img_bytes = saved
        st.download_button(
            label="📥 تحميل الرسم البياني كصورة (PNG)",
            data=img_bytes,
            file_name=f"{sym}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
            use_container_width=True
        )

# ============================================================
# 9. العداد التنازلي + تنبيه قبل الدخول (يعمل كل ثانية بدون تجميد الصفحة)
# ============================================================
def fmt_mmss(sec):
    sec = max(0, int(math.ceil(sec)))
    return f"{sec // 60:02d}:{sec % 60:02d}"

def schedule_trade(df, signal, strength, reason, stake):
    current_price = float(df['close'].iloc[-1])
    entry_ts = (int(time.time()) // period + 1) * period  # بداية الشمعة القادمة
    log_trade(symbol, signal, strength, current_price, period, stake, entry_ts)
    st.session_state['active_trade'] = {
        "symbol": symbol, "signal": signal, "strength": strength, "stake": stake, "period": period,
        "entry_ts": entry_ts, "expiry_ts": entry_ts + period, "pre_alerted": False, "entered_alerted": False,
    }
    st.session_state.pop('last_result_msg', None)
    entry_clock = datetime.fromtimestamp(entry_ts).strftime("%H:%M:%S")
    msg = (f"👑 <b>ELZOGHEIR VIP: {signal}</b>\n💰 {symbol}\n💵 السعر: {current_price:.5f}\n"
           f"💪 قوة الإشارة: {strength}%\n📊 RSI: {df['RSI'].iloc[-1]:.1f}\n💸 حجم الدخول: ${stake}\n"
           f"⏰ موعد الدخول: {entry_clock}\n📝 {reason}")
    play_sound("signal")
    if enable_telegram:
        ok, err = send_telegram_alert(msg)
        if not ok and err:
            st.toast(f"تيليجرام: {err}", icon="⚠️")

@st.fragment(run_every=1)
def trade_timer():
    trade = st.session_state.get('active_trade')
    if not trade:
        msg = st.session_state.get('last_result_msg')
        if msg:
            st.success(msg)
        return

    now = time.time()
    to_entry = trade['entry_ts'] - now
    to_exp = trade['expiry_ts'] - now
    side = "شراء ▲" if "BUY" in trade['signal'] else "بيع ▼"
    info = f"{trade['symbol']} — {side} • قوة {trade['strength']}% • ${trade['stake']}"

    if to_entry > 0:
        if to_entry <= pre_alert_seconds and not trade['pre_alerted']:
            trade['pre_alerted'] = True
            notify(f"⏰ الدخول بعد {int(to_entry)} ثانية: {trade['symbol']} {side}",
                   f"⏰ <b>تنبيه قبل الدخول</b>\n💰 {trade['symbol']}\n📌 {trade['signal']} ({trade['strength']}%)\n"
                   f"⌛ الدخول بعد {int(to_entry)} ثانية\n💸 ${trade['stake']}", "pre")
        urgent = " urgent" if to_entry <= pre_alert_seconds else ""
        entry_clock = datetime.fromtimestamp(trade['entry_ts']).strftime("%H:%M:%S")
        st.markdown(f"""
        <div class="countdown-box{urgent}">
            <div class="countdown-label">⏳ موعد الدخول — {info}</div>
            <div class="countdown-time">{fmt_mmss(to_entry)}</div>
            <div class="countdown-label">الدخول عند {entry_clock}</div>
        </div>
        """, unsafe_allow_html=True)
    elif to_exp > 0:
        if not trade['entered_alerted']:
            trade['entered_alerted'] = True
            notify(f"🚀 ادخل الآن: {trade['symbol']} {side}",
                   f"🚀 <b>ادخل الآن</b>\n💰 {trade['symbol']}\n📌 {trade['signal']}\n💸 ${trade['stake']}", "enter")
        st.markdown(f"""
        <div class="countdown-box">
            <div class="countdown-label">🔥 الصفقة جارية — {info}</div>
            <div class="countdown-time">{fmt_mmss(to_exp)}</div>
            <div class="countdown-label">الوقت المتبقي لإغلاق الصفقة</div>
        </div>
        """, unsafe_allow_html=True)
    elif now < trade['expiry_ts'] + 3:
        st.markdown('<div class="countdown-box"><div class="countdown-label">⌛ جاري إغلاق الصفقة...</div></div>', unsafe_allow_html=True)
    else:
        with st.spinner("جاري تقييم الصفقة..."):
            evaluate_trades()
        log_df = load_log()
        row = log_df[(log_df["Symbol"] == trade['symbol']) & (log_df["EntryTS"] == trade['entry_ts'])]
        result = row.iloc[-1]["Result"] if len(row) else "PENDING"
        icon = {"WIN": "🏆 ربح", "LOSS": "❌ خسارة", "DRAW": "➖ تعادل"}.get(result)
        if icon:
            st.session_state['last_result_msg'] = f"✅ انتهت صفقة {trade['symbol']} — النتيجة: {icon}"
        else:
            st.session_state['last_result_msg'] = f"✅ انتهت مدة صفقة {trade['symbol']} — سيتم تقييمها عند الجلب التالي."
        st.session_state['active_trade'] = None
        st.success(st.session_state['last_result_msg'])

# ============================================================
# 10. العرض الرئيسي
# ============================================================
def render_analysis(auto_mode=False):
    cache = st.session_state.get('analysis')
    cache_ok = bool(cache) and cache['symbol'] == symbol and cache['period'] == period
    force = st.session_state.pop('do_fetch', False)
    stale = auto_mode and (not cache_ok or time.time() - cache['fetched_at'] >= 55)
    fresh = force or stale

    if fresh:
        slot = st.empty()
        show_loader(slot, f"جاري جلب صفقة {symbol}", "اتصال آمن • 200 شمعة • تحليل متعدد الأطر الزمنية")
        results, errors = fetch_many([(symbol, period, max_candles), (symbol, higher_tf, max_candles)])
        df = results.get((symbol, period))
        if df is None:
            slot.empty()
            err = errors.get((symbol, period)) or errors.get("connection") or errors.get("error") or "سبب غير معروف"
            st.error(f"تعذر جلب بيانات {symbol}: {err}")
            return
        higher_df = results.get((symbol, higher_tf))
        show_loader(slot, "جاري تحليل الأنماط والمؤشرات", "RSI • MACD • EMA200 • ATR • الأنماط الشمعية")
        df = calculate_indicators(df)
        if higher_df is not None:
            higher_df = calculate_indicators(higher_df)
        patterns = detect_patterns(df)
        signal, buys, sells, reason, strength = generate_signal(patterns, df, higher_df)
        slot.empty()
        cache = dict(symbol=symbol, period=period, fetched_at=time.time(), df=df, higher_df=higher_df,
                     patterns=patterns, signal=signal, buys=buys, sells=sells, reason=reason, strength=strength)
        st.session_state['analysis'] = cache
        if higher_df is None:
            st.warning("تعذر جلب الإطار الأكبر، لذلك لن تُصنَّف الإشارة كـ STRONG.")
        evaluate_trades()
    elif cache_ok:
        df, patterns = cache['df'], cache['patterns']
        signal, reason, strength = cache['signal'], cache['reason'], cache['strength']
    else:
        st.info("👈 اضغط **جلب صفقة** في الشريط الجانبي لتحليل هذا الزوج والإطار.")
        return

    current_price = df['close'].iloc[-1]
    current_stake = compute_stake(base_stake, martingale_mode, martingale_max_steps)

    # معالجة الإشارة الجديدة (مرة واحدة لكل شمعة/زوج/اتجاه)
    if fresh and signal in ["STRONG BUY", "STRONG SELL"]:
        key = (symbol, signal, int(df['ts'].iloc[-1]))
        if key != st.session_state.get('last_signal_key'):
            st.session_state['last_signal_key'] = key
            if st.session_state.get('active_trade') or has_pending(symbol):
                st.warning("توجد صفقة نشطة/معلّقة بالفعل، لم تُجدول صفقة جديدة.")
            else:
                schedule_trade(df, signal, strength, reason, current_stake)

    # عرض البطاقات
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">السعر</div><div class="metric-value">{current_price:,.5f}</div></div>', unsafe_allow_html=True)
    with c2:
        rsi_val = df['RSI'].iloc[-1]
        cls = "sell-signal" if rsi_val > 70 else "buy-signal" if rsi_val < 30 else ""
        st.markdown(f'<div class="metric-card"><div class="metric-label">RSI</div><div class="metric-value {cls}">{rsi_val:.1f}</div></div>', unsafe_allow_html=True)
    with c3:
        trend = "صاعد ↗" if current_price > df['EMA200'].iloc[-1] else "هابط ↘"
        t_cls = "buy-signal" if "صاعد" in trend else "sell-signal"
        st.markdown(f'<div class="metric-card"><div class="metric-label">الاتجاه</div><div class="metric-value {t_cls}">{trend}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">حجم الدخول</div><div class="metric-value" style="color:#FFD700">${current_stake}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig = plot_chart(df, patterns, symbol)
    st.plotly_chart(fig, use_container_width=True)
    export_chart_image(fig, symbol)

    # عرض الإشارة + نسبة القوة بجانبها
    sig_color = "buy-signal" if "BUY" in signal else "sell-signal" if "SELL" in signal else "neutral-signal"
    emoji = "🟢" if "BUY" in signal else "🔴" if "SELL" in signal else "🟡"
    sc = strength_color(strength)
    st.markdown(f"""
    <div class="metric-card" style="margin-bottom: 10px; border-color: #FFD700;">
        <div class="metric-label">الإشارة النهائية</div>
        <div class="signal-row">
            <div class="metric-value {sig_color}" style="font-size: 1.8rem;">{emoji} {signal}</div>
            <div class="strength-badge" style="color:{sc}; border-color:{sc};">💪 {strength}%</div>
        </div>
        <div class="strength-track"><div class="strength-fill" style="width:{strength}%; background:{sc};"></div></div>
        <div style="color:#8899AA; font-size:0.9rem;">{reason}</div>
    </div>
    """, unsafe_allow_html=True)

    # لوحة التحليلات
    log_df = load_log()
    if len(log_df) > 0:
        with st.expander("📊 لوحة التحليلات وإدارة رأس المال"):
            col1, col2 = st.columns(2)
            with col1:
                wins = len(log_df[log_df['Result'] == 'WIN'])
                losses = len(log_df[log_df['Result'] == 'LOSS'])
                if wins + losses > 0:
                    st.metric("نسبة النجاح", f"{wins / (wins + losses) * 100:.1f}%")
                    pie_fig = go.Figure(data=[go.Pie(labels=['Wins', 'Losses'], values=[wins, losses], hole=.4, marker_colors=['#00FFAA', '#FF3355'])])
                    pie_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=300, margin=dict(t=10, b=10))
                    st.plotly_chart(pie_fig, use_container_width=True)
            with col2:
                st.markdown("### أفضل الأزواج (Top Pairs)")
                completed = log_df[log_df['Result'].isin(['WIN', 'LOSS'])]
                if len(completed) > 0:
                    pair_stats = completed.groupby('Symbol')['Result'].value_counts().unstack(fill_value=0)
                    st.dataframe(pair_stats, use_container_width=True)
                st.download_button("📥 تحميل السجل (CSV)", log_df.to_csv(index=False).encode('utf-8'), "elzogheir_log.csv", "text/csv", use_container_width=True)

render_analysis_auto = st.fragment(run_every=60)(render_analysis)

def run_scanner():
    slot = st.empty()
    reqs = []
    for p in PAIRS:
        reqs.append((p, period, max_candles))
        reqs.append((p, higher_tf, max_candles))
    show_loader(slot, "جاري مسح السوق", f"فحص {len(PAIRS)} زوج • 200 شمعة لكل زوج", pct=0)

    def cb(n, total, sym):
        show_loader(slot, "جاري مسح السوق", f"{sym} ({n}/{total})", pct=n / total * 100)

    results, errors = fetch_many(reqs, cb)
    rows, failed = [], []
    for p in PAIRS:
        d = results.get((p, period))
        if d is None:
            failed.append(f"{p}: {errors.get((p, period), errors.get('connection', 'فشل'))}")
            continue
        d = calculate_indicators(d)
        h = results.get((p, higher_tf))
        if h is not None:
            h = calculate_indicators(h)
        sig, _, _, _, stren = generate_signal(detect_patterns(d), d, h)
        rows.append({"الزوج": p, "الإشارة": sig, "القوة %": stren, "السعر": f"{d['close'].iloc[-1]:.5f}"})
    slot.empty()
    st.session_state['scan_results'] = {"rows": rows, "failed": failed, "period": period}

def render_scan_results():
    sr = st.session_state.get('scan_results')
    if not sr:
        return False
    st.markdown("### 🔍 نتائج مسح السوق (Scanner)")
    if sr["rows"]:
        res = pd.DataFrame(sr["rows"]).sort_values("القوة %", ascending=False)
        st.dataframe(res, use_container_width=True, hide_index=True, column_config={
            "القوة %": st.column_config.ProgressColumn("القوة %", min_value=0, max_value=100, format="%d%%")
        })
    else:
        st.warning("لم يتم جلب أي زوج.")
    if sr["failed"]:
        with st.expander(f"⚠️ أزواج لم تُجلب ({len(sr['failed'])})"):
            for f in sr["failed"]:
                st.write(f)
    return True

# ---- التشغيل ----
trade_timer()

if st.session_state.pop('run_scanner', False):
    run_scanner()

shown = False
if st.session_state.get('run_scan') or enable_auto_refresh:
    shown = True
    if enable_auto_refresh:
        render_analysis_auto(True)
    else:
        render_analysis(False)

if render_scan_results():
    shown = True

if not shown:
    st.info("👈 اضغط **جلب صفقة** في الشريط الجانبي لبدء التحليل.")
