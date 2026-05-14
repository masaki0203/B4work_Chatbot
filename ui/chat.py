import io
import re
import streamlit as st
from core.code_runner import run_code


def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf.read()


def _render_code_block(code: str, show_download: bool = False):
    fig, error = run_code(code)
    if error:
        st.warning(f"コード実行エラー: {error}")
        st.code(code, language="python")
    else:
        st.pyplot(fig)
        if show_download:
            st.download_button(
                label="画像をダウンロード",
                data=_fig_to_bytes(fig),
                file_name="graph.png",
                mime="image/png",
            )


def render_message(msg: dict):
    with st.chat_message(msg["role"]):
        for img_bytes, _ in msg.get("images", []):
            st.image(img_bytes)
        parts = re.split(r"(```python.*?```)", msg.get("content", ""), flags=re.DOTALL)
        for part in parts:
            m = re.match(r"```python\n(.*?)```", part, re.DOTALL)
            if m:
                _render_code_block(m.group(1), show_download=True)
            elif part.strip():
                st.write(part)


def render_code_blocks(content: str):
    parts = re.split(r"(```python.*?```)", content, flags=re.DOTALL)
    for part in parts:
        m = re.match(r"```python\n(.*?)```", part, re.DOTALL)
        if m:
            _render_code_block(m.group(1), show_download=True)


def render_chat_history():
    for msg in st.session_state.messages:
        render_message(msg)
