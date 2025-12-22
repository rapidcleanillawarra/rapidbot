# Configuration Constants
import os

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FOLDER = os.path.join(BASE_DIR, "products")

# Image paths
CHROME_IMAGE = os.path.join(BASE_DIR, "chrome_icon.png")
INPUT_FIELD_IMAGE = os.path.join(BASE_DIR, "input_field.png")
INPUT_FIELD_READY_IMAGE = os.path.join(BASE_DIR, "input_field_ready.png")
ACTIVE_TAB_IMAGE = os.path.join(BASE_DIR, "active_tab.png")
SUBMISSION_ANSWER_NOW_IMAGE = os.path.join(BASE_DIR, "submission_indicator_answer_now.png")
SUBMISSION_STOP_IMAGE = os.path.join(BASE_DIR, "submission_indicator_stop.png")
DOWNLOAD_JSON_IMAGE = os.path.join(BASE_DIR, "download_json.png")
AUTOMATE_JSON_IMAGE = os.path.join(BASE_DIR, "automate_json.png")

# API Configuration
BRANDS_API_URL = "https://default61576f99244849ec8803974b47673f.57.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/ef89e5969a8f45778307f167f435253c/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=pPhk80gODQOi843ixLjZtPPWqTeXIbIt9ifWZP6CJfY"

# ChatGPT URL
CHATGPT_URL = "https://chatgpt.com/g/g-69153998509481918156154b9ed0e00e-product-description-finder"

# UI Colors
COLORS = {
    "bg": "#1a1a2e",
    "card": "#16213e",
    "accent": "#0f3460",
    "highlight": "#e94560",
    "text": "#eaeaea",
    "success": "#00d26a",
    "warning": "#ffc107"
}

# Process settings
PROCESS_5_MAX_RETRIES = 10
PROCESS_5_WAIT_SECONDS = 5
IMAGE_CONFIDENCE = 0.8
DEFAULT_ACTIVE_TABS = 2

# Beep frequencies (Hz) for each process
BEEP_FREQUENCIES = {
    1: 800,
    2: 900,
    3: 1000,
    4: 1100,
    5: 1200,
    6: 1300,
    7: 1400
}
BEEP_DURATION = 200  # milliseconds
