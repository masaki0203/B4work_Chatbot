import matplotlib
import streamlit as st
from ui.sidebar import render_sidebar
from ui.chat import render_message, render_chat_history, render_code_blocks
from ui.logo import inject_fixed_icon
from core.gemini import stream_reply
from core.imagen import generate_image

matplotlib.rcParams["font.family"] = "IPAexGothic"

st.set_page_config(page_title="チャットボット", page_icon="💬", layout="centered")
inject_fixed_icon()

api_key, model, system_prompt = render_sidebar()

if "messages" not in st.session_state:
    st.session_state.messages = []

render_chat_history()

st.caption("💡 `/image 犬が走っている` のように入力すると画像を生成します")

if chat_input := st.chat_input("メッセージを入力...", accept_file="multiple", file_type=["png", "jpg", "jpeg", "webp"]):
    prompt = chat_input.text
    uploaded_files = chat_input.files
else:
    prompt = None
    uploaded_files = []

if prompt is not None:
    if not api_key:
        st.error("サイドバーに Gemini API Key を入力してください。")
        st.stop()

    images = [(f.read(), f.type) for f in uploaded_files]
    user_msg = {"role": "user", "content": prompt or "", "images": images}
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        for img_bytes, _ in images:
            st.image(img_bytes)
        if prompt:
            st.write(prompt)

    # 画像生成モード
    if prompt.startswith("/image "):
        image_prompt = prompt[7:].strip()
        with st.chat_message("assistant"):
            with st.spinner("画像を生成中..."):
                try:
                    generated = generate_image(api_key, image_prompt)
                    for img_bytes in generated:
                        st.image(img_bytes)
                        st.download_button(
                            label="画像をダウンロード",
                            data=img_bytes,
                            file_name="generated.png",
                            mime="image/png",
                        )
                    reply = f"[生成画像: {image_prompt}]"
                except Exception as e:
                    st.error(f"画像生成エラー: {e}")
                    st.session_state.messages.pop()
                    st.stop()
        st.session_state.messages.append({"role": "assistant", "content": reply})

    # 通常チャットモード
    else:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            reply = ""
            try:
                for chunk in stream_reply(api_key, model, system_prompt, st.session_state.messages):
                    reply += chunk
                    placeholder.markdown(reply + "▌")
                placeholder.markdown(reply)
                render_code_blocks(reply)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.session_state.messages.pop()
                st.stop()
        st.session_state.messages.append({"role": "assistant", "content": reply})
