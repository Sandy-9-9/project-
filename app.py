from flask import Flask, request, render_template, flash
from PIL import Image
import requests
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = "change-this-secret"
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024  # 12 MB

# 🔗 YOUR NGROK / REMOTE API
REMOTE_API_URL = "http://e793-34-123-73-186.ngrok-free.app/api/transform"


# ================= HOME PAGE =================
@app.route('/', methods=['GET'])
def home():
    return render_template('try.html', op=None)


# ================= FORM SUBMIT =================
@app.route('/preds', methods=['POST'])
def submit():
    cloth = request.files.get('cloth')
    model = request.files.get('model')

    # ✅ Validation
    if not cloth or not model:
        flash("Please upload BOTH cloth and model images.")
        return render_template('try.html', op=None)

    cloth_bytes = cloth.read()
    model_bytes = model.read()

    files = {
        'cloth': (cloth.filename, BytesIO(cloth_bytes), cloth.mimetype),
        'model': (model.filename, BytesIO(model_bytes), model.mimetype),
    }

    try:
        # ⏱️ Heavy ML → long timeout
        resp = requests.post(REMOTE_API_URL, files=files, timeout=300)
        resp.raise_for_status()
    except Exception as e:
        flash(f"Remote API error: {e}")
        return render_template('try.html', op=None)

    # 🔍 Detect response type
    content_type = resp.headers.get("Content-Type", "")

    try:
        if "application/json" in content_type:
            # API returns base64 JSON
            data = resp.json()
            img_bytes = base64.b64decode(data['image'])
            out_img = Image.open(BytesIO(img_bytes)).convert("RGBA")
        else:
            # API returns raw image
            out_img = Image.open(BytesIO(resp.content)).convert("RGBA")
    except Exception:
        flash("Failed to decode image from API response.")
        return render_template('try.html', op=None)

    # Convert output → base64 for HTML
    buffer = BytesIO()
    out_img.save(buffer, format="PNG")
    op_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render_template('try.html', op=op_b64)


if __name__ == '__main__':
    app.run(debug=True)
