import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image
from io import BytesIO


def run_code(code: str) -> tuple[object, str | None]:
    """コードを実行してfigを返す。エラー時は (None, エラーメッセージ) を返す。"""
    local_ns = {
        "plt": plt, "matplotlib": matplotlib,
        "np": np, "numpy": np,
        "requests": requests, "Image": Image, "BytesIO": BytesIO,
    }
    try:
        exec(code, local_ns)
        fig = local_ns.get("fig") or plt.gcf()
        plt.close("all")
        return fig, None
    except Exception as e:
        plt.close("all")
        return None, str(e)
