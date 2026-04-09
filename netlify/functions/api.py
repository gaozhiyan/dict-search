import os
import sys

# 将项目根目录添加到 Python 路径中，以便能够导入 main.py 和 scraper.py
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from mangum import Mangum
from main import app

# Mangum 是一个适配器，用于在 AWS Lambda（Netlify 底层使用）中运行 ASGI 应用程序（FastAPI）
handler = Mangum(app)