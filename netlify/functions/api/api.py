import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from mangum import Mangum
    from main import app
    handler = Mangum(app, api_gateway_base_path="/.netlify/functions/api")
except Exception as e:
    # Capture the error message
    error_msg = str(e)
    path_msg = str(sys.path)
    # Fallback to handle import errors gracefully and see them in logs
    def handler(event, context):
        return {
            "statusCode": 500,
            "body": f"Function initialization error: {error_msg}\nPaths: {path_msg}"
        }