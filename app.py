import io
import os
from flask import Flask, Request, Response, jsonify, request, send_file
from pypdf.errors import PdfReadError
from ollama import ResponseError
from main import read_pdf_text, is_too_long, start_conversation, stream_answer, ollama_error_message

class MemoryRequest(Request):
    # Keep uploaded PDFs in memory only, so sensitive files are never written to disk
    def _get_file_stream(self, *args, **kwargs):
        return io.BytesIO()

app = Flask(__name__)
app.request_class = MemoryRequest
# Largest PDF you can upload (50 MB)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

@app.get("/")
def index():
    return send_file("index.html")

@app.post("/upload")
def upload():
    # Read the PDF text and send back a new conversation. Nothing is saved on the server,
    # the browser keeps the conversation and sends it with every question.
    try:
        text = read_pdf_text(request.files["pdf"].stream)
    except (KeyError, PdfReadError) as e:
        return jsonify(error=f"Could not read the PDF: {e}"), 400
    if not text.strip():
        return jsonify(error="No text found in this PDF (is it a scanned PDF?)."), 400
    warning = "This PDF is very long, the model may only read part of it." if is_too_long(text) else ""
    return jsonify(messages=start_conversation(text), warning=warning)

@app.post("/ask")
def ask():
    messages = request.get_json()["messages"]

    def generate():
        try:
            yield from stream_answer(messages)
        except (ConnectionError, ResponseError) as e:
            # The page knows an answer starting with ⚠ is an error and does not keep it
            yield "⚠ " + ollama_error_message(e)

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    # 127.0.0.1 means only this computer can open the app, not others on the network.
    # Docker sets HOST=0.0.0.0, and compose.yaml keeps the port limited to this computer.
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=5000)
