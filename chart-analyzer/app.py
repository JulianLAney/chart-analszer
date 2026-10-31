import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import io

# Page Setup
st.set_page_config(
    page_title="Scanner Terminal",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom High-End Trading UI CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #080c0d !important;
        color: #f1f5f9;
    }

    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 480px !important;
    }

    /* Top Floating Pill */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(18, 28, 26, 0.9);
        border: 1px solid rgba(34, 197, 94, 0.25);
        color: #4ade80;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 5px 14px;
        border-radius: 9999px;
        margin-bottom: 14px;
    }

    /* Viewport / Reticle Frame */
    .viewport-box {
        position: relative;
        background: #0f1618;
        border-radius: 20px;
        padding: 10px;
        border: 1px solid #1a2729;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
        margin-bottom: 16px;
    }
    .viewport-box::before, .viewport-box::after {
        content: "";
        position: absolute;
        width: 18px;
        height: 18px;
        border-color: #22c55e;
        border-style: solid;
        pointer-events: none;
    }
    .viewport-box::before {
        top: -2px; left: -2px;
        border-width: 2.5px 0 0 2.5px;
        border-top-left-radius: 6px;
    }
    .viewport-box::after {
        bottom: -2px; right: -2px;
        border-width: 0 2.5px 2.5px 0;
        border-bottom-right-radius: 6px;
    }

    /* Primary Decision Card */
    .signal-card {
        background: #111718;
        border: 1px solid #1d2729;
        border-radius: 22px;
        padding: 22px;
        margin-bottom: 14px;
    }
    .signal-label {
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        font-weight: 800;
        color: #fb923c;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .signal-main-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .signal-action {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .badge-icon {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 800;
    }
    .badge-hold { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(2
