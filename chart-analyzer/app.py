import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(
    page_title="Chart Co-Pilot",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📈 AI Chart Analyzer")
st.caption("Upload a chart screenshot to extract market structure, key zones, and scenario planning.")

# Reads API key from cloud secrets or manual input
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.text_input("Enter Gemini API Key:", type="password")

SYSTEM_PROMPT = """
You are an institutional Technical Analysis engine. Analyze the uploaded chart screenshot objectively.

Structure your analysis strictly into these sections:
1. Asset & Timeframe: Identify the ticker and timeframe if visible.
2. Market Structure: Current trend (Bullish/Bearish/Ranging), highs/lows sequence, and volume behavior.
3. Key Levels: Supply/Demand zones, key horizontal support/resistance, and liquidity pools.
4. Confluence Factors: Specific technical indicators (MAs, RSI), candlestick patterns, or imbalances (e.g. gaps/FVGs).
5. Scenario Playbook (Probabilistic):
   - Primary Outlook (Higher probability path + trigger)
   - Invalidation Level (Exact price that invalidates the primary outlook)
   - Alternative Scenario (What occurs if the invalidation level breaks)
6. Risk Framing: Example entry area, stop level, and conservative take-profit targets (maintaining a healthy risk-to-reward ratio).
"""

uploaded_file = st.file_uploader("Upload Chart Screenshot", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)

    if st.button("Analyze Chart", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please enter a valid Gemini API key to proceed.")
        else:
            with st.spinner("Decoding chart structure and key levels..."):
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image, SYSTEM_PROMPT]
                    )
                    st.success("Analysis Complete!")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error analyzing chart: {e}")