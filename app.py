from flask import Flask, render_template, request, url_for
import os
from werkzeug.utils import secure_filename
from uuid import uuid4

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    if "file" not in request.files:
        return "이미지 파일이 전달되지 않았습니다.", 400

    file = request.files["file"]

    if file.filename == "":
        return "이미지를 선택해주세요.", 400

    if not allowed_file(file.filename):
        return "JPG, JPEG, PNG 파일만 업로드할 수 있습니다.", 400


    # 원래 파일명
    original_filename = secure_filename(file.filename)

    # 같은 이름의 이미지가 덮어쓰기 되는 것을 방지
    extension = original_filename.rsplit(".", 1)[1].lower()

    saved_filename = (
        f"{uuid4().hex}.{extension}"
    )

    save_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        saved_filename
    )

    file.save(save_path)


    # =====================================
    # 모델 연결 전 임시 분석 결과
    # =====================================
    #
    # 나중에 모델이 완성되면
    # 아래 부분을 model.predict() 결과로 교체
    #

    prediction = "Normal"
    confidence = 93.2

    probabilities = {
        "Normal": 93.2,
        "Left": 2.8,
        "Right": 2.5,
        "Both": 1.5
    }


    # 업로드 이미지 URL
    image_url = url_for(
        "static",
        filename=f"uploads/{saved_filename}"
    )


    return render_template(
        "result.html",

        image=image_url,
        filename=original_filename,

        prediction=prediction,
        confidence=confidence,

        normal_prob=probabilities["Normal"],
        left_prob=probabilities["Left"],
        right_prob=probabilities["Right"],
        both_prob=probabilities["Both"]
    )


if __name__ == "__main__":
    app.run(debug=True)