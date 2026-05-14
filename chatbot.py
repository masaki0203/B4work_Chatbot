import re
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "IPAexGothic"
load_dotenv()

st.set_page_config(page_title="チャットボット", page_icon="💬")
st.title("💬 チャットボット")

# APIキー：.envから読み込み、なければサイドバーで入力
env_key = os.getenv("GEMINI_API_KEY", "")
if env_key and env_key != "ここにAPIキーを貼り付ける":
    api_key = env_key
    st.sidebar.success("APIキー: .envから読み込み済み")
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# モデル一覧を取得してキャッシュ
@st.cache_data(show_spinner="モデル一覧を取得中...")
def fetch_models(key):
    client = genai.Client(api_key=key)
    return [
        m.name.removeprefix("models/")
        for m in client.models.list()
        if "generateContent" in (m.supported_actions or [])
    ]

if api_key:
    try:
        model_list = fetch_models(api_key) + ["その他（直接入力）"]
        default_idx = model_list.index("gemini-2.0-flash") if "gemini-2.0-flash" in model_list else 0
        selected = st.sidebar.selectbox("Gemini モデル", model_list, index=default_idx)
        if selected == "その他（直接入力）":
            model = st.sidebar.text_input("モデル名を入力", value="gemini-1.5-flash")
        else:
            model = selected
    except Exception as e:
        st.sidebar.error(f"モデル取得エラー: {e}")
        model = st.sidebar.text_input("Gemini モデル名", value="gemini-2.0-flash")
else:
    model = st.sidebar.text_input("Gemini モデル名（APIキー入力後に自動取得）", value="gemini-2.0-flash")

system_prompt = st.sidebar.text_area(
    "システムプロンプト",
    value=(
        "あなたは親切なアシスタントです。ユーザーの質問に日本語で丁寧に答えてください。\n"
        "グラフや図表の生成を求められた場合は、matplotlib を使った Python コードを ```python ``` のコードブロックのみで返してください。"
        "コードの説明や前置き・補足は一切不要です。コードブロック以外のテキストを返さないでください。"
        "コードは plt.show() を呼ばずに、plt.savefig() も不要です。fig オブジェクトを最後に残してください。"
    ),
    height=180,
)

if st.sidebar.button("会話をリセット", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_message(msg):
    with st.chat_message(msg["role"]):
        parts = re.split(r"(```python.*?```)", msg["content"], flags=re.DOTALL)
        for part in parts:
            m = re.match(r"```python\n(.*?)```", part, re.DOTALL)
            if m:
                code = m.group(1)
                try:
                    import numpy as np
                    import requests
                    from PIL import Image
                    from io import BytesIO
                    local_ns = {
                        "plt": plt, "matplotlib": matplotlib,
                        "np": np, "numpy": np,
                        "requests": requests, "Image": Image, "BytesIO": BytesIO,
                    }
                    exec(code, local_ns)
                    fig = local_ns.get("fig") or plt.gcf()
                    st.pyplot(fig)
                    plt.close("all")
                except Exception as e:
                    st.warning(f"コード実行エラー: {e}")
                    st.code(code, language="python")
            elif part.strip():
                st.write(part)


for msg in st.session_state.messages:
    render_message(msg)

if prompt := st.chat_input("メッセージを入力..."):
    if not api_key:
        st.error("サイドバーに Gemini API Key を入力してください。")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    client = genai.Client(api_key=api_key)

    history = [
        types.Content(
            role="model" if msg["role"] == "assistant" else msg["role"],
            parts=[types.Part(text=msg["content"])]
        )
        for msg in st.session_state.messages[:-1]
    ]

    with st.spinner("返答を生成中..."):
        try:
            response = client.models.generate_content(
                model=model,
                contents=history + [types.Content(role="user", parts=[types.Part(text=prompt)])],
                config=types.GenerateContentConfig(system_instruction=system_prompt),
            )
            reply = response.text
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.session_state.messages.pop()
            st.stop()

    st.session_state.messages.append({"role": "assistant", "content": reply})
    render_message({"role": "assistant", "content": reply})
