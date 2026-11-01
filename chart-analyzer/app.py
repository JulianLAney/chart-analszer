import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import io
import time

st.set_page_config(
    page_title="Scanner Terminal",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Dark Trading UI CSS
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #080c0d !important; color: #f1f5f9; }
header[data-testid="stHeader"], footer { display: none; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2.5rem !important; max-width: 480px !important; }
.status-pill { display: inline-flex; align-items: center; gap: 6px; background: rgba(18,28,26,0.9); border: 1px solid rgba(34,197,94,0.25); color: #4ade80; font-size: 0.75rem; font-weight: 600; padding: 4px 14px; border-radius: 9999px; margin-bottom: 12px; }
.viewport-box { position: relative; background: #0f1618; border-radius: 20px; padding: 8px; border: 1px solid #1a2729; margin-bottom: 14px; }
.viewport-box::before { content: ""; position: absolute; width: 18px; height: 18px; border-color: #22c55e; border-style: solid; top: -2px; left: -2px; border-width: 2.5px 0 0 2.5px; border-top-left-radius: 6px; }
.viewport-box::after { content: ""; position: absolute; width: 18px; height: 18px; border-color: #22c55e; border-style: solid; bottom: -2px; right: -2px; border-width: 0 2.5px 2.5px 0; border-bottom-right-radius: 6px; }
.signal-card { background: #111718; border: 1px solid #1d2729; border-radius: 22px; padding: 20px; margin-bottom: 12px; }
.signal-label { font-size: 0.7rem; letter-spacing: 1.5px; font-weight: 800; color: #fb923c; text-transform: uppercase; margin-bottom: 4px; }
.signal-main-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.signal-action { font-size: 2.3rem; font-weight: 800; color: #ffffff; margin: 0; }
.badge-icon { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 800; }
.badge-hold { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.badge-buy { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.badge-sell { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.signal-desc { color: #94a3b8; font-size: 0.88rem; line-height: 1.4; margin: 0; }
.levels-card { background: #111718; border: 1px solid #1d2729; border-radius: 18px; padding: 14px 18px; margin-bottom: 12px; }
.level-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.88rem; padding: 3px 0; }
.level-title { color: #cbd5e1; display: flex; align-items: center; gap: 8px; font-weight: 500; }
.level-pill { background: #172123; border: 1px solid #27373a; padding: 3px 12px; border-radius: 8px; font-weight: 700; font-size: 0.85rem; }
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.grid-cell { background: #111718; border: 1px solid #1d2729; border-radius: 16px; padding: 12px 14px; }
.grid-label { color: #64748b; font-size: 0.72rem; font-weight: 600; margin-bottom: 2px; }
.grid-val { color: #ffffff; font-size: 1rem; font-weight: 700; }
div.stButton > button { background-color: #ffffff !important; color: #000000 !important; border-radius: 9999px !important; font-weight: 700 !important; font-size: 1rem !important; padding: 12px 24px !important; border: none !important; width: 100% !important; margin-top: 6px !important; }
</style>""", unsafe_allow_html=True)

st.markdown('<div style="text-align:center;"><span class="status-pill">● Pattern Engine Active</span></div>', unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")

uploaded_files = st.file_uploader("Upload Chart Screenshot(s)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

JSON_PROMPT = """Analyze the provided chart image(s) across all visible timeframes and return ONLY a valid JSON object matching this schema (no code blocks, no backticks, no markdown):
{
  "pattern_detected": "Identified pattern, structure, or setup name",
  "signal": "HOLD" or "BUY" or "SELL",
  "reasoning": "Clear 1-2 sentence breakdown of price behavior, multi-timeframe alignment, and the exact trigger/confirmation required.",
  "resistance": "Key resistance price or zone",
  "support": "Key support price or zone",
  "trend": "Bullish / Bearish / Sideways",
  "volatility": "Low / Medium / High",
  "volume": "Low / Average / High",
  "sentiment": "Bullish / Bearish / Neutral"
}"""

if uploaded_files:
    optimized_images = []
    
    st.markdown('<div class="viewport-box">', unsafe_allow_html=True)
    for idx, file in enumerate(uploaded_files):
        img = Image.open(file)
        st.image(img, caption=f"Chart {idx + 1}" if len(uploaded_files) > 1 else None, use_container_width=True)
        
        img_copy = img.copy()
        if max(img_copy.size) > 1280:
            img_copy.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img_copy.convert("RGB").save(buffer, format="JPEG", quality=80)
        optimized_images.append(Image.open(buffer))
    st.markdown('</div>', unsafe_allow_html=True)

    button_label = "Scan Charts" if len(uploaded_files) > 1 else "Scan Chart"
    if st.button(button_label, type="primary"):
        if not api_key:
            st.error("Please configure your GEMINI_API_KEY secret in settings.")
        else:
            with st.spinner("Scanning structure & multi-timeframe context..."):
                try:
                    client = genai.Client(api_key=api_key)
                    content_payload = optimized_images + [JSON_PROMPT]
                    
                    config = types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=800,
                        response_mime_type="application/json"
                    )

                    # Exclusively use gemini-3.8-flash with an automatic 2-second retry if busy
                    response = None
                    last_err = None
                    for attempt in range(2):
                        try:
                            response = client.models.generate_content(
                                model='gemini-3.8-flash',
                                contents=content_payload,
                                config=config
                            )
                            break
                        except Exception as e:
                            last_err = e
                            if attempt == 0:
                                time.sleep(2)
                            else:
                                raise last_err

                    clean = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(clean)

                    signal = str(data.get("signal", "HOLD")).upper()
                    if "BUY" in signal:
                        badge_style = "badge-buy"
                        icon_symbol = "↗"
                        display_signal = "Buy"
                    elif "SELL" in signal:
                        badge_style = "badge-sell"
                        icon_symbol = "↘"
                        display_signal = "Sell"
                    else:
                        badge_style = "badge-hold"
                        icon_symbol = "⏸"
                        display_signal = "Hold"

                    pattern = data.get("pattern_detected", "Structure Identified")
                    st.markdown(f'<div style="text-align:center; margin-bottom: 12px;"><span class="status-pill">✔ Pattern detected: {pattern}</span></div>', unsafe_allow_html=True)

                    # 1. Primary Signal Card
                    st.markdown(f"""<div class="signal-card">
                        <div class="signal-label">• CHART SIGNAL</div>
                        <div class="signal-main-row">
                            <h1 class="signal-action">{display_signal}</h1>
                            <div class="badge-icon {badge_style}">{icon_symbol}</div>
                        </div>
                        <p class="signal-desc">{data.get("reasoning", "")}</p>
                    </div>""", unsafe_allow_html=True)

                    # 2. Key Levels Card
                    st.markdown(f"""<div class="levels-card">
                        <div style="font-size: 0.7rem; letter-spacing: 1px; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Key Levels</div>
                        <div class="level-row">
                            <span class="level-title"><span style="color: #f87171;">●</span> Resistance</span>
                            <span class="level-pill" style="color: #f87171;">{data.get("resistance", "N/A")}</span>
                        </div>
                        <div class="level-row" style="margin-top: 6px;">
                            <span class="level-title"><span style="color: #4ade80;">●</span> Support</span>
                            <span class="level-pill" style="color: #4ade80;">{data.get("support", "N/A")}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                    # 3. 2x2 Metric Grid
                    st.markdown(f"""<div class="metric-grid">
                        <div class="grid-cell"><div class="grid-label">Trend</div><div class="grid-val">{data.get("trend", "N/A")}</div></div>
                        <div class="grid-cell"><div class="grid-label">Volatility</div><div class="grid-val">{data.get("volatility", "N/A")}</div></div>
                        <div class="grid-cell"><div class="grid-label">Volume</div><div class="grid-val">{data.get("volume", "N/A")}</div></div>
                        <div class="grid-cell"><div class="grid-label">Sentiment</div><div class="grid-val">{data.get("sentiment", "N/A")}</div></div>
                    </div>""", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Scan failed: {e}")
