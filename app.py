import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import asyncio
import requests
import os
from datetime import datetime, timedelta
from streamlit_js_eval import streamlit_js_eval
from pocketoptionapi_async import AsyncPocketOptionClient
from io import BytesIO

# ============================================================
# 1. إعدادات الصفحة والتصميم (CSS) - ELZOGHEIR VIP
# ============================================================
st.set_page_config(page_title="ELZOGHEIR CANDLE-VIP", page_icon="👑", layout="wide")

# ---------- اللغة / Language ----------
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'ar'

TEXTS = {
 "ar": {
  "settings": "⚙️ إعدادات VIP", "pair": "الزوج / الأصل (40 زوج)", "tf": "الإطار الزمني",
  "p15": "15 ثانية", "p30": "30 ثانية", "p60": "دقيقة", "p180": "3 دقائق",
  "p300": "5 دقائق", "p900": "15 دقيقة", "p1800": "30 دقيقة",
  "risk": "🛡️ إدارة المخاطر", "stake": "حجم الدخول الأساسي ($)", "mart": "تفعيل المضاعفة (Martingale)",
  "feat": "🔔 الميزات", "tg": "إشعارات تيليجرام", "snd": "تنبيه صوتي",
  "pre": "تنبيه قبل الدخول بـ 30 ثانية", "auto": "تحديث تلقائي (60 ث)",
  "b_sync": "🚀 مزامنة وتحليل", "b_chart": "📡 سكنر الشارت", "b_market": "🔍 مسح السوق (Scanner)",
  "b_clear": "🗑️ مسح الذاكرة", "price": "السعر", "trend": "الاتجاه", "up": "صاعد ↗", "down": "هابط ↘",
  "stake_card": "حجم الدخول", "final": "الإشارة النهائية",
  "cd": "⏳ الوقت المتبقي لإغلاق صفقة", "cd_unit": "(ثانية)",
  "done": "✅ انتهت مدة الصفقة! تم تقييمها في السجل.",
  "pre_msg": "⚠️ استعد! الدخول بعد", "pre_unit": "ثانية",
  "analytics": "📊 لوحة التحليلات وإدارة رأس المال", "top": "أفضل الأزواج (Top Pairs)",
  "dl_log": "📥 تحميل السجل (CSV)", "dl_chart": "📥 تحميل الرسم البياني كصورة (PNG)",
  "scan_title": "### 🔍 نتائج مسح السوق (Scanner)", "scan_spin": "جاري فحص 10 أزواج...",
  "c_pair": "الزوج", "c_sig": "الإشارة", "c_price": "السعر",
  "info": "👈 اضغط **مزامنة وتحليل** في الشريط الجانبي لبدء التحليل.",
  "r_full": "توافق كامل (أنماط + RSI + MACD + EMA + إطار أكبر + جلسة)",
  "r_buy": "أنماط شراء فقط", "r_sell": "أنماط بيع فقط", "r_noconf": "بدون تأكيد",
  "r_inactive": "⚠️ جلسة غير نشطة", "r_none": "لا توجد إشارة", "lang_btn": "🌐 English",
 },
 "en": {
  "settings": "⚙️ VIP Settings", "pair": "Pair / Asset (40 pairs)", "tf": "Timeframe",
  "p15": "15 sec", "p30": "30 sec", "p60": "1 min", "p180": "3 min",
  "p300": "5 min", "p900": "15 min", "p1800": "30 min",
  "risk": "🛡️ Risk Management", "stake": "Base stake ($)", "mart": "Enable Martingale",
  "feat": "🔔 Features", "tg": "Telegram alerts", "snd": "Sound alert",
  "pre": "Alert 30s before entry", "auto": "Auto refresh (60s)",
  "b_sync": "🚀 Sync & Analyze", "b_chart": "📡 Chart Scanner", "b_market": "🔍 Market Scan",
  "b_clear": "🗑️ Clear Memory", "price": "Price", "trend": "Trend", "up": "Bullish ↗", "down": "Bearish ↘",
  "stake_card": "Stake", "final": "Final Signal",
  "cd": "⏳ Time left to close trade", "cd_unit": "(sec)",
  "done": "✅ Trade expired! It was evaluated in the log.",
  "pre_msg": "⚠️ Get ready! Entry in", "pre_unit": "sec",
  "analytics": "📊 Analytics & Capital Management", "top": "Top Pairs",
  "dl_log": "📥 Download log (CSV)", "dl_chart": "📥 Download chart as image (PNG)",
  "scan_title": "### 🔍 Market Scan Results", "scan_spin": "Scanning 10 pairs...",
  "c_pair": "Pair", "c_sig": "Signal", "c_price": "Price",
  "info": "👈 Press **Sync & Analyze** in the sidebar to start.",
  "r_full": "Full confluence (patterns + RSI + MACD + EMA + higher TF + session)",
  "r_buy": "Buy patterns only", "r_sell": "Sell patterns only", "r_noconf": "no confirmation",
  "r_inactive": "⚠️ Inactive session", "r_none": "No signal", "lang_btn": "🌐 العربية",
 },
}
def t(k): return TEXTS[st.session_state['lang']][k]
def toggle_lang():
    st.session_state['lang'] = 'en' if st.session_state['lang'] == 'ar' else 'ar'

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

    /* ===== لمسات VIP إضافية ===== */
    .main-header {
        background: linear-gradient(90deg, #FFD700, #FFF4B0, #FFD700, #B8860B);
        background-size: 300% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: shine 5s linear infinite;
        letter-spacing: 2px;
    }
    @keyframes shine { to { background-position: 300% center; } }

    .metric-card {
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative; overflow: hidden;
    }
    .metric-card::before {
        content: ""; position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
        background: linear-gradient(120deg, transparent, rgba(255,215,0,0.08), transparent);
        transition: left 0.7s ease;
    }
    .metric-card:hover::before { left: 150%; }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #FFD700;
        box-shadow: 0 8px 30px rgba(255,215,0,0.18);
    }

    .buy-signal, .sell-signal { animation: pulse 1.8s ease-in-out infinite; }
    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.65; } }

    .countdown-box { animation: glow 2s ease-in-out infinite alternate; }
    @keyframes glow {
        from { box-shadow: 0 0 15px rgba(255,215,0,0.3); }
        to   { box-shadow: 0 0 40px rgba(255,215,0,0.7); }
    }

    div[data-baseweb="select"] > div {
        background: #0F1522 !important; border: 1px solid #1F2A3C !important; border-radius: 10px !important;
    }
    div[data-baseweb="select"] > div:hover { border-color: #FFD700 !important; }

    .stButton>button { transition: all 0.25s ease; letter-spacing: 0.5px; }
    .stButton>button:active { transform: scale(0.97); }

    div[data-testid="stExpander"] {
        border: 1px solid #1F2A3C; border-radius: 12px; background: rgba(18,24,38,0.6);
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #050810; }
    ::-webkit-scrollbar-thumb { background: #B8860B; border-radius: 10px; }

    /* تنبيه ما قبل الدخول */
    .pre-alert { border-color: #FF8800; animation: warn 0.8s ease-in-out infinite alternate; }
    @keyframes warn {
        from { box-shadow: 0 0 15px rgba(255,136,0,0.4); }
        to   { box-shadow: 0 0 45px rgba(255,51,85,0.9); }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">👑 ELZOGHEIR CANDLE-VIP</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">ULTIMATE TRADING SYSTEM • 40 PAIRS • MULTI-TIMEFRAME</div>', unsafe_allow_html=True)

# ============================================================
# 2. بيانات الاعتماد والإعدادات
# ============================================================
SSID = '42["auth",{"session":"bchtvth5m3bmdovlva3i5t59nq","isDemo":1,"uid":136934681,"platform":2,"isFastHistory":true,"isOptimized":true}]'
TELEGRAM_TOKEN = "8531787721:AAH6dmi42q9BGw7rsdJYW7Ux3gfJj7iZ51E"
TELEGRAM_CHAT_ID = "8758991455"
CSV_FILE = "elzogheir_vip_log.csv"

PAIRS = [
    # --- الأزواج الأصلية (20) ---
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "USDCAD_otc",
    "USDCHF_otc", "NZDUSD_otc", "EURGBP_otc", "EURJPY_otc", "GBPJPY_otc",
    "AUDCAD_otc", "AUDJPY_otc", "CADJPY_otc", "CHFJPY_otc", "EURCAD_otc",
    "EURAUD_otc", "GBPAUD_otc", "GBPCAD_otc", "XAUUSD_otc", "BTCUSD_otc",
    # --- الأزواج الجديدة (20) ---
    "AUDCHF_otc", "AUDNZD_otc", "CADCHF_otc", "EURCHF_otc", "EURNZD_otc",
    "GBPCHF_otc", "GBPNZD_otc", "NZDCAD_otc", "NZDCHF_otc", "NZDJPY_otc",
    "USDMXN_otc", "USDSGD_otc", "USDINR_otc", "USDBRL_otc", "USDTHB_otc",
    "USDIDR_otc", "USDPHP_otc", "USDEGP_otc", "USDCNH_otc", "USDARS_otc",
]

# ============================================================
# 3. الشريط الجانبي
# ============================================================
with st.sidebar:
    st.button(t("lang_btn"), on_click=toggle_lang, use_container_width=True)
    st.markdown(f"### {t('settings')}")
    symbol = st.selectbox(t("pair"), PAIRS, key="symbol")
    period = st.selectbox(t("tf"),
        [15, 30, 60, 180, 300, 900, 1800],
        format_func=lambda x: t(f"p{x}"),
        index=2, key="period"
    )
    max_candles = 200

    st.markdown("---")
    st.markdown(f"### {t('risk')}")
    base_stake = st.number_input(t("stake"), min_value=1.0, value=1.0, step=1.0, key="stake")
    martingale_mode = st.checkbox(t("mart"), value=False, key="mart")

    st.markdown("---")
    st.markdown(f"### {t('feat')}")
    enable_telegram = st.checkbox(t("tg"), value=False, key="tg")
    enable_sound = st.checkbox(t("snd"), value=True, key="snd")
    enable_pre_alert = st.checkbox(t("pre"), value=True, key="pre")
    enable_auto_refresh = st.checkbox(t("auto"), value=False, key="auto")

    st.markdown("---")
    if st.button(t("b_sync"), use_container_width=True):
        st.session_state['run_scan'] = True
        st.session_state['trade_opened_time'] = None

    if st.button(t("b_chart"), use_container_width=True):
        st.session_state['run_scan'] = True
        st.session_state['trade_opened_time'] = None
        st.session_state['laser_pending'] = True

    if st.button(t("b_market"), use_container_width=True):
        st.session_state['run_scanner'] = True

    if st.button(t("b_clear"), use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ============================================================
# 4. دوال مساعدة
# ============================================================
def play_sound(key="sound_alert"):
    if enable_sound:
        streamlit_js_eval(js_expressions="new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg').play()", key=key)

def send_telegram_alert(message):
    if not enable_telegram or TELEGRAM_TOKEN == "ضع_التوكن_هنا": return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try: requests.post(url, json=payload, timeout=5)
    except: pass

async def fetch_data_async(symbol, period, max_candles):
    client = AsyncPocketOptionClient(SSID, is_demo=True)
    await client.connect()
    candles = await client.get_candles(asset=symbol, timeframe=period, count=max_candles)
    await client.disconnect()
    return candles

def get_otc_data(symbol, period, max_candles):
    try:
        candles = asyncio.run(fetch_data_async(symbol, period, max_candles))
        if not candles: return None
        data = [{'time': c.timestamp, 'open': c.open, 'high': c.high, 'low': c.low, 'close': c.close} for c in candles]
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df.tail(max_candles).reset_index(drop=True)
    except Exception as e:
        return None

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
# 6. منطق الإشارة (مع فلترة الجلسات والاتجاه)
# ============================================================
def generate_signal(patterns, df, higher_tf_df):
    buys = sum(1 for _, _, s in patterns if s == "buy")
    sells = sum(1 for _, _, s in patterns if s == "sell")
    
    last_rsi = df['RSI'].iloc[-1]; last_macd = df['MACD_Hist'].iloc[-1]
    last_close = df['close'].iloc[-1]; last_ema = df['EMA200'].iloc[-1]
    
    # فلترة الجلسة (تجنب أوقات السيولة المنخفضة)
    current_hour = datetime.utcnow().hour
    is_active_session = 7 <= current_hour <= 21 # جلسات لندن ونيويورك
    
    # الاتجاه في الإطار الأكبر
    higher_trend = "UP"
    if higher_tf_df is not None and len(higher_tf_df) > 0:
        higher_close = higher_tf_df['close'].iloc[-1]
        higher_ema = higher_tf_df['close'].ewm(span=200, adjust=False).mean().iloc[-1]
        higher_trend = "UP" if higher_close > higher_ema else "DOWN"
    
    reason = ""
    if not is_active_session: reason = t("r_inactive")
    
    if buys > sells and last_rsi < 70 and last_macd > 0 and last_close > last_ema and higher_trend == "UP" and is_active_session:
        return "STRONG BUY", buys, sells, t("r_full")
    elif sells > buys and last_rsi > 30 and last_macd < 0 and last_close < last_ema and higher_trend == "DOWN" and is_active_session:
        return "STRONG SELL", buys, sells, t("r_full")
    elif buys > sells:
        return "WEAK BUY", buys, sells, f"{t('r_buy')} ({reason if reason else t('r_noconf')})"
    elif sells > buys:
        return "WEAK SELL", buys, sells, f"{t('r_sell')} ({reason if reason else t('r_noconf')})"
    return "NEUTRAL", buys, sells, t("r_none")

# ============================================================
# 7. إدارة السجل والتحليلات
# ============================================================
def log_trade(symbol, signal, entry_price, timeframe, stake):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    expiry_time = (datetime.now() + timedelta(seconds=timeframe)).strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([{"Time": timestamp, "Symbol": symbol, "Signal": signal, "Entry": entry_price, "Expiry": expiry_time, "Stake": stake, "Result": "PENDING"}])
    if os.path.exists(CSV_FILE): new_data.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else: new_data.to_csv(CSV_FILE, mode='w', header=True, index=False)

def evaluate_trades(current_price):
    if not os.path.exists(CSV_FILE): return
    df = pd.read_csv(CSV_FILE)
    updated = False
    now = datetime.now()
    for index, row in df.iterrows():
        if row['Result'] == 'PENDING':
            expiry = datetime.strptime(row['Expiry'], "%Y-%m-%d %H:%M:%S")
            if now >= expiry:
                result = "WIN" if ("BUY" in row['Signal'] and current_price > row['Entry']) or ("SELL" in row['Signal'] and current_price < row['Entry']) else "LOSS"
                df.at[index, 'Result'] = result
                updated = True
    if updated: df.to_csv(CSV_FILE, index=False)

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
    try:
        img_bytes = fig.to_image(format="png", width=1200, height=700, scale=2)
        st.download_button(
            label=t("dl_chart"),
            data=img_bytes,
            file_name=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
            use_container_width=True
        )
    except:
        st.info("لتحميل الصورة، تأكد من تثبيت مكتبة kaleido: py -m pip install kaleido")

# ============================================================
# 9. العرض الرئيسي
# ============================================================
if st.session_state.get('run_scan') or enable_auto_refresh:
    df = get_otc_data(symbol, period, max_candles)
    
    if df is not None and len(df) > 0:
        df = calculate_indicators(df)
        
        # سحب الإطار الأكبر للتحليل المتعدد
        higher_tf = 300 if period < 300 else 900
        higher_df = get_otc_data(symbol, higher_tf, 50)
        if higher_df is not None: higher_df = calculate_indicators(higher_df)
        
        patterns = detect_patterns(df)
        signal, buys, sells, reason = generate_signal(patterns, df, higher_df)
        current_price = df['close'].iloc[-1]
        
        evaluate_trades(current_price)

        # إدارة المخاطر وحجم الدخول
        current_stake = base_stake
        if os.path.exists(CSV_FILE) and martingale_mode:
            log_df = pd.read_csv(CSV_FILE)
            completed = log_df[log_df['Result'].isin(['WIN', 'LOSS'])]
            if len(completed) > 0:
                last_result = completed.iloc[-1]['Result']
                last_stake = completed.iloc[-1]['Stake']
                if last_result == 'LOSS':
                    current_stake = last_stake * 2 # Martingale

        # معالجة الإشارة الجديدة
        last_signal = st.session_state.get('last_signal', None)
        if signal in ["STRONG BUY", "STRONG SELL"] and signal != last_signal:
            msg = f"👑 <b>ELZOGHEIR VIP: {signal}</b>\n💰 {symbol}\n💵 السعر: {current_price:.5f}\n📊 RSI: {df['RSI'].iloc[-1]:.1f}\n💸 حجم الدخول: ${current_stake}\n📝 {reason}"
            if enable_telegram: send_telegram_alert(msg)
            play_sound()
            log_trade(symbol, signal, current_price, period, current_stake)
            st.session_state['last_signal'] = signal
            st.session_state['trade_opened_time'] = time.time()
            st.session_state['active_stake'] = current_stake

        # عرض البطاقات
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">{t("price")}</div><div class="metric-value">{current_price:,.5f}</div></div>', unsafe_allow_html=True)
        with c2:
            rsi_val = df['RSI'].iloc[-1]
            cls = "sell-signal" if rsi_val > 70 else "buy-signal" if rsi_val < 30 else ""
            st.markdown(f'<div class="metric-card"><div class="metric-label">RSI</div><div class="metric-value {cls}">{rsi_val:.1f}</div></div>', unsafe_allow_html=True)
        with c3:
            is_up = current_price > df['EMA200'].iloc[-1]
            trend = t("up") if is_up else t("down")
            t_cls = "buy-signal" if is_up else "sell-signal"
            st.markdown(f'<div class="metric-card"><div class="metric-label">{t("trend")}</div><div class="metric-value {t_cls}">{trend}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{t("stake_card")}</div><div class="metric-value" style="color:#FFD700">${current_stake}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ليزر سكنر الشارت
        if st.session_state.pop('laser_pending', False):
            st.session_state['laser_until'] = time.time() + 6

        if time.time() < st.session_state.get('laser_until', 0):
            st.markdown("""
            <style>
            div[data-testid="stPlotlyChart"] { position: relative; overflow: hidden; border-radius: 12px; }
            div[data-testid="stPlotlyChart"]::after {
                content: ""; position: absolute; left: 0; right: 0; top: 0; height: 3px; z-index: 50;
                pointer-events: none;
                background: linear-gradient(90deg, transparent, #FF0033 20%, #FF6680 50%, #FF0033 80%, transparent);
                box-shadow: 0 0 12px 4px rgba(255,0,51,0.8), 0 0 60px 20px rgba(255,0,51,0.25);
                animation: laserMove 1.8s ease-in-out 3 alternate;
            }
            div[data-testid="stPlotlyChart"]::before {
                content: "◉ SCANNING..."; position: absolute; top: 8px; left: 14px; z-index: 50;
                color: #FF3355; font: 700 12px monospace; letter-spacing: 3px; pointer-events: none;
                text-shadow: 0 0 8px #FF0033; animation: blink 0.6s step-end infinite;
            }
            @keyframes laserMove { from { top: 0; } to { top: calc(100% - 3px); } }
            @keyframes blink { 50% { opacity: 0; } }
            </style>
            """, unsafe_allow_html=True)

        fig = plot_chart(df, patterns, symbol)
        st.plotly_chart(fig, use_container_width=True)
        export_chart_image(fig, symbol)

        # عرض الإشارة والعداد التنازلي
        sig_color = "buy-signal" if "BUY" in signal else "sell-signal" if "SELL" in signal else "neutral-signal"
        emoji = "🟢" if "BUY" in signal else "🔴" if "SELL" in signal else "🟡"
        
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 10px; border-color: #FFD700;">
            <div class="metric-label">{t("final")}</div>
            <div class="metric-value {sig_color}" style="font-size: 1.8rem;">{emoji} {signal}</div>
            <div style="color:#8899AA; font-size:0.9rem;">{reason}</div>
        </div>
        """, unsafe_allow_html=True)

        # تنبيه قبل الدخول بـ 30 ثانية
        if enable_pre_alert and period > 30 and signal in ["STRONG BUY", "STRONG SELL"]:
            candle_id = int(time.time() // period)
            to_entry = period - (int(time.time()) % period)
            if to_entry <= 30:
                st.markdown(f"""
                <div class="countdown-box pre-alert">
                    <div class="countdown-label">{t("pre_msg")} · {symbol} · {signal}</div>
                    <div class="countdown-time">{to_entry} {t("pre_unit")}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.session_state.get('pre_alert_candle') != candle_id:
                    st.session_state['pre_alert_candle'] = candle_id
                    play_sound(f"pre_alert_{candle_id}")
                    if enable_telegram:
                        send_telegram_alert(f"⏰ <b>{t('pre_msg')} {to_entry} {t('pre_unit')}</b>\n{symbol} · {signal}")

        # العداد التنازلي
        if st.session_state.get('trade_opened_time') and signal in ["STRONG BUY", "STRONG SELL"]:
            elapsed = time.time() - st.session_state['trade_opened_time']
            remaining = int(period - elapsed)
            if remaining > 0:
                st.markdown(f"""
                <div class="countdown-box">
                    <div class="countdown-label">{t("cd")} {symbol} {t("cd_unit")}</div>
                    <div class="countdown-time">{remaining}</div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                st.success(t("done"))
                st.session_state['trade_opened_time'] = None

        # لوحة التحليلات
        if os.path.exists(CSV_FILE):
            log_df = pd.read_csv(CSV_FILE)
            with st.expander(t("analytics")):
                col1, col2 = st.columns(2)
                with col1:
                    wins = len(log_df[log_df['Result'] == 'WIN'])
                    losses = len(log_df[log_df['Result'] == 'LOSS'])
                    if wins + losses > 0:
                        pie_fig = go.Figure(data=[go.Pie(labels=['Wins', 'Losses'], values=[wins, losses], hole=.4, marker_colors=['#00FFAA', '#FF3355'])])
                        pie_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=300, margin=dict(t=10, b=10))
                        st.plotly_chart(pie_fig, use_container_width=True)
                with col2:
                    st.markdown(f"### {t('top')}")
                    completed = log_df[log_df['Result'].isin(['WIN', 'LOSS'])]
                    if len(completed) > 0:
                        pair_stats = completed.groupby('Symbol')['Result'].value_counts().unstack(fill_value=0)
                        st.dataframe(pair_stats, use_container_width=True)
                    st.download_button(t("dl_log"), log_df.to_csv(index=False).encode('utf-8'), "elzogheir_log.csv", "text/csv", use_container_width=True)

# مسح السوق (Scanner)
if st.session_state.get('run_scanner'):
    st.markdown(t("scan_title"))
    with st.spinner(t("scan_spin")):
        scan_pairs = PAIRS[:10] # فحص أول 10 أزواج
        results = []
        for p in scan_pairs:
            d = get_otc_data(p, 60, 100)
            if d is not None:
                d = calculate_indicators(d)
                pats = detect_patterns(d)
                sig, _, _, _ = generate_signal(pats, d, None)
                results.append({t("c_pair"): p, t("c_sig"): sig, t("c_price"): f"{d['close'].iloc[-1]:.5f}"})
        st.table(pd.DataFrame(results))

else:
    st.info(t("info"))

if enable_auto_refresh:
    time.sleep(60)
    st.rerun()
