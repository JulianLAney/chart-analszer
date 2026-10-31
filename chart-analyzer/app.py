import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json

# Page Setup
st.set_page_config(
    page_title="Chart Co-Pilot",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Dark Terminal Theme)
st.markdown("""
<style>
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }
    .metric-card {
        background-color: #151b26;
        border: 1px solid #232d3f;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-bullish {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-bearish {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-neutral {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stat-box {
        background-color: #1a2232;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #8b9bb4;
        text-transform: uppercase;
    }
    .stat-val {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ AI Market Co-Pilot")
st.caption("Upload a chart screenshot to extract structure, key levels, and probabilistic scenarios.")

api_key = st.secrets.get("AQ.Ab8RN6J-Ny6IeUZ5pDiZ9StDNP1B3SU8cJCHO1WhbQ93bOvAlQ", "")
if not api_key:
    api_key = st.text_input("AQ.Ab8RN6J-Ny6IeUZ5pDiZ9StDNP1B3SU8cJCHO1WhbQ93bOvAlQ", type="password")

uploaded_file = st.file_uploader("Upload Chart", type=["png", "jpg", "jpeg"])

JSON_PROMPT = """
You are an expert technical analysis system. Analyze the chart image and return ONLY a valid JSON object (no markdown wrappers, no backticks).

Strict JSON Schema:
{
  "ticker": "Asset or Unknown",
  "timeframe": "Timeframe or Unknown",
  "bias": "BULLISH" | "BEARISH" | "NEUTRAL",
  "current_price": "Price or Unknown",
  "structure": "Description of trend and swing highs/lows",
  "pattern_detected": "Name of pattern or None",
  "support_level": "Key support price or area",
  "resistance_level": "Key resistance price or area",
  "invalidation_price": "Level where bias becomes invalid",
  "primary_scenario": "Most likely market trajectory",
  "alt_scenario": "Trajectory if invalidation is breached",
  "risk_reward": "Estimated R:R ratio for a standard setup (e.g. 1:2.5)"
}
"""

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    if st.button("Analyze Structure", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please provide a Gemini API Key to continue.")
        else:
            with st.spinner("Decoding price action..."):
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=[image, JSON_PROMPT]
                    )
                    
                    # Parse clean JSON
                    clean_text = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(clean_text)

                    # Bias Badge
                    bias = data.get("bias", "NEUTRAL").upper()
                    badge_class = "badge-bullish" if bias == "BULLISH" else ("badge-bearish" if bias == "BEARISH" else "badge-neutral")

                    # Primary Overview Card
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h3 style="margin: 0;">{data.get('ticker', 'Asset')} ({data.get('timeframe', 'TF')})</h3>
                            <span class="{badge_class}">{bias}</span>
                        </div>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.95rem;"><strong>Pattern:</strong> {data.get('pattern_detected', 'None')}</p>
                        <p style="margin: 4px 0 0 0; color: #cbd5e1; font-size: 0.9rem;">{data.get('structure', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Key Levels Row
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-label">Support</div>
                            <div class="stat-val" style="color: #4ade80;">{data.get('support_level', '-')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-label">Resistance</div>
                            <div class="stat-val" style="color: #f87171;">{data.get('resistance_level', '-')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-label">Invalidation</div>
                            <div class="stat-val" style="color: #fbbf24;">{data.get('invalidation_price', '-')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Scenario Breakdown Card
                    st.markdown(f"""
                    <div class="metric-card" style="margin-top: 14px;">
                        <h4 style="margin: 0 0 8px 0; color: #f1f5f9;">Playbook</h4>
                        <p style="font-size: 0.9rem; margin-bottom: 6px;"><strong>Primary Path:</strong> {data.get('primary_scenario', '')}</p>
                        <p style="font-size: 0.9rem; margin-bottom: 6px; color: #94a3b8;"><strong>Alternative Path:</strong> {data.get('alt_scenario', '')}</p>
                        <p style="font-size: 0.85rem; margin: 0; color: #64748b;"><strong>Target R:R:</strong> {data.get('risk_reward', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Failed to parse analysis: {e}")
