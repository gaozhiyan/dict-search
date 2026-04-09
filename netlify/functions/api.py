import os
import sys

# In the deployed Netlify environment, files are usually in the same directory or `/var/task`.
# We add both the current directory and the original ROOT_DIR to be safe.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, ROOT_DIR)

try:
    from mangum import Mangum
    from main import app
    handler = Mangum(app, api_gateway_base_path="/.netlify/functions/api")
except Exception as e:
    # Fallback to handle import errors gracefully and see them in logs
    def handler(event, context):
        return {
            "statusCode": 500,
            "body": f"Function initialization error: {str(e)}\nPaths: {sys.path}"
        }