from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static", "uploads")

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    if "file" not in request.files:

        return "파일이 전달되지 않았습니다."


    file = request.files["file"]


    if file.filename == "":

        return "파일을 선택해주세요."


    filename = secure_filename(
        file.filename
    )


    save_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    file.save(
        save_path
    )


    # 모델 연결 전 임시값
    prediction = "Normal"

    confidence = 93.2


    image_path = (
        "/"
        + save_path.replace("\\", "/")
    )


    return render_template(
        "result.html",
        image=image_path,
        filename=filename,
        prediction=prediction,
        confidence=confidence
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )