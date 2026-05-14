import base64
import os
import streamlit as st

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets")


def _b64(filename: str) -> str:
    with open(os.path.join(ASSETS_DIR, filename), "rb") as f:
        return base64.b64encode(f.read()).decode()


def inject_sidebar_logo():
    """サイドバー内のフルロゴ（サイドバーのwithブロック内で呼ぶ）。"""
    logo_b64 = _b64("logo.png")
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 0.2rem !important;
    }}
    .logo-wrap {{
        padding: 0 0 0.6rem 0;
        margin-top: -0.8rem;
    }}
    </style>
    <div class="logo-wrap">
        <img src="data:image/png;base64,{logo_b64}" width="210">
    </div>
    """, unsafe_allow_html=True)


def inject_fixed_icon():
    """サイドバーが閉じたときにメイン画面左上に表示されるアイコン（メインコンテキストで呼ぶ）。"""
    icon_b64 = _b64("logo_icon.png")
    st.markdown(f"""
    <style>
    /* サイドバー展開中はアイコンを隠す */
    [data-testid="stSidebarCollapsedControl"] ~ * .main-logo-icon,
    .main-logo-icon {{
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 9999;
        display: none;
    }}
    /* サイドバーが閉じているときだけ表示 */
    [data-testid="stSidebarCollapsedControl"] ~ .main-logo-icon,
    body:has([data-testid="stSidebarCollapsedControl"]) .main-logo-icon {{
        display: block !important;
    }}
    </style>
    <img class="main-logo-icon" src="data:image/png;base64,{icon_b64}" width="40">
    """, unsafe_allow_html=True)
