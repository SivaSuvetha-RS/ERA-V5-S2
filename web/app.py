from flask import Flask, request, jsonify, send_file, send_from_directory
from tokenizers import Tokenizer
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOKENIZER_PATH = os.path.join(
    BASE_DIR, "tokenizer", "tokenizer.json"
)

METRICS_PATH = os.path.join(
    BASE_DIR, "evaluation", "metrics.json"
)

WEB_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")

tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
tokenizer_mtime_ns = os.stat(TOKENIZER_PATH).st_mtime_ns


def get_tokenizer():
    global tokenizer, tokenizer_mtime_ns

    current_mtime_ns = os.stat(TOKENIZER_PATH).st_mtime_ns
    if current_mtime_ns != tokenizer_mtime_ns:
        tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
        tokenizer_mtime_ns = current_mtime_ns

    return tokenizer


def load_metrics():
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)



@app.route("/")
def home():
    return send_from_directory(WEB_DIR, "index.html")



@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "tokenizer": "loaded",
        "vocab_size": get_tokenizer().get_vocab_size(),
    })



@app.route("/api/metrics")
def get_metrics():
    return jsonify(load_metrics())


@app.route("/api/vocab")
def get_vocabulary():
    current_tokenizer = get_tokenizer()
    vocabulary = sorted(
        current_tokenizer.get_vocab().items(),
        key=lambda item: item[1],
    )
    response = jsonify({
        "vocab_size": len(vocabulary),
        "tokens": [
            {"id": token_id, "token": token}
            for token, token_id in vocabulary
        ],
    })
    if request.args.get("view") != "1":
        response.headers["Content-Disposition"] = (
            'attachment; filename="indiabpe-vocabulary.json"'
        )
    return response


@app.route("/api/tokenizer")
def download_tokenizer():
    return send_file(
        TOKENIZER_PATH,
        mimetype="application/json",
        as_attachment=True,
        download_name="tokenizer.json",
    )


@app.route("/api/tokenize", methods=["POST"])
def tokenize():
    data = request.get_json(silent=True) or {}

    text = data.get("text", "").strip()

    if not text:
        return jsonify({
            "error": "Please enter some text."
        }), 400

    current_tokenizer = get_tokenizer()
    encoding = current_tokenizer.encode(text)

    return jsonify({
        "text": text,
        "tokens": encoding.tokens,
        "ids": encoding.ids,
        "token_count": len(encoding.ids),
        "decoded": current_tokenizer.decode(encoding.ids)
    })



if __name__ == "__main__":
    print("=" * 50)
    print("IndiaBPE Multilingual Tokenizer")
    print("=" * 50)
    print("Tokenizer loaded successfully")
    print(f"Tokenizer: {TOKENIZER_PATH}")
    print("Server: http://127.0.0.1:8000")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        debug=True
    )