import streamlit as st
from core.gemini import fetch_models
from core.history import save_history, load_history, list_histories
from ui.logo import inject_sidebar_logo

DEFAULT_SYSTEM_PROMPT = (
    "あなたは親切なアシスタントです。ユーザーの質問に日本語で丁寧に答えてください。\n"
    "グラフや図表の生成を求められた場合は、matplotlib を使った Python コードを ```python ``` のコードブロックのみで返してください。"
    "コードの説明や前置き・補足は一切不要です。コードブロック以外のテキストを返さないでください。"
    "コードは plt.show() を呼ばずに、plt.savefig() も不要です。fig オブジェクトを最後に残してください。"
)


@st.cache_data(show_spinner="モデル一覧を取得中...")
def _fetch_models_cached(api_key: str) -> list[str]:
    return fetch_models(api_key)


def render_sidebar() -> tuple[str, str, str]:
    """サイドバーを描画し、(api_key, model, system_prompt) を返す。"""
    with st.sidebar:
        inject_sidebar_logo()

    api_key = st.sidebar.text_input("Gemini API Key", type="password")

    if api_key:
        try:
            model_list = _fetch_models_cached(api_key) + ["その他（直接入力）"]
            default_idx = model_list.index("gemini-2.0-flash") if "gemini-2.0-flash" in model_list else 0
            selected = st.sidebar.selectbox("Gemini モデル", model_list, index=default_idx)
            model = st.sidebar.text_input("モデル名を入力", value="gemini-1.5-flash") if selected == "その他（直接入力）" else selected
        except Exception as e:
            st.sidebar.error(f"モデル取得エラー: {e}")
            model = st.sidebar.text_input("Gemini モデル名", value="gemini-2.0-flash")
    else:
        model = st.sidebar.text_input("Gemini モデル名（APIキー入力後に自動取得）", value="gemini-2.0-flash")

    system_prompt = st.sidebar.text_area("システムプロンプト", value=DEFAULT_SYSTEM_PROMPT, height=180)

    st.sidebar.divider()

    # 履歴の保存
    st.sidebar.subheader("会話履歴")
    save_name = st.sidebar.text_input("保存名（空欄で日時自動命名）", placeholder="例: python勉強")
    if st.sidebar.button("現在の会話を保存", use_container_width=True):
        if st.session_state.get("messages"):
            filename = save_history(st.session_state.messages, save_name)
            st.sidebar.success(f"保存しました: {filename}")
        else:
            st.sidebar.warning("会話がありません。")

    # 履歴の読み込み
    history_files = list_histories()
    if history_files:
        selected_file = st.sidebar.selectbox("過去の会話を読み込む", ["選択してください"] + history_files)
        if selected_file != "選択してください":
            if st.sidebar.button("読み込む", use_container_width=True):
                st.session_state.messages = load_history(selected_file)
                st.rerun()

    st.sidebar.divider()

    if st.sidebar.button("会話をリセット", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    return api_key, model, system_prompt
