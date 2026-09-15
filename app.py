from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import requests


app = Flask(__name__)


# ============================================
# 백엔드 API 주소
# ============================================

BACKEND_UPLOAD_URL = (
    "https://sinusitis-backend.onrender.com/api/images"
)


# ============================================
# 업로드 허용 확장자
# ============================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================
# 메인 페이지
# ============================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================
# 이미지 분석 요청
# ============================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    # ----------------------------------------
    # 1. 브라우저에서 이미지 받기
    # ----------------------------------------

    if "file" not in request.files:

        return (
            "이미지 파일이 전달되지 않았습니다.",
            400
        )


    file = request.files["file"]


    if file.filename == "":

        return (
            "이미지를 선택해주세요.",
            400
        )


    if not allowed_file(file.filename):

        return (
            "JPG, JPEG, PNG 파일만 "
            "업로드할 수 있습니다.",
            400
        )


    original_filename = secure_filename(
        file.filename
    )


    # ----------------------------------------
    # 2. 백엔드 서버에 전달
    #
    # 중요:
    # 백엔드에서 요구하는 파일 필드명이
    # "image"이므로 반드시 image 사용
    # ----------------------------------------

    files = {

        "image": (
            original_filename,
            file.stream,
            file.mimetype
        )

    }


    try:

        backend_response = requests.post(

            BACKEND_UPLOAD_URL,

            files=files,

            timeout=60

        )


    except requests.RequestException as error:

        print(
            "백엔드 연결 오류:",
            error
        )

        return (
            "백엔드 서버에 연결할 수 없습니다.",
            502
        )


    # ----------------------------------------
    # 3. 백엔드 HTTP 응답 확인
    # ----------------------------------------

    if not backend_response.ok:

        print(
            "백엔드 응답 오류:",
            backend_response.status_code
        )

        print(
            backend_response.text
        )

        return (
            "이미지 업로드 중 오류가 발생했습니다.",
            502
        )


    # ----------------------------------------
    # 4. JSON 응답 받기
    # ----------------------------------------

    try:

        data = backend_response.json()


    except ValueError:

        print(
            "백엔드 JSON 오류:",
            backend_response.text
        )

        return (
            "백엔드 응답 형식이 올바르지 않습니다.",
            502
        )


    print(
        "백엔드 응답:",
        data
    )


    # ----------------------------------------
    # 5. 백엔드가 반환한 이미지 URL 가져오기
    # ----------------------------------------

    image_data = data.get(
        "image"
    ) or {}


    image_url = image_data.get(
        "imageUrl"
    )


    if not image_url:

        return (
            "업로드된 이미지 주소를 "
            "받지 못했습니다.",
            502
        )


    # ----------------------------------------
    # 6. AI 결과 확인
    #
    # 현재 AI 모델 미연결 상태에서는
    # result가 null일 수 있음
    # ----------------------------------------

    result = data.get(
        "result"
    )


    # ----------------------------------------
    # 7. 모델 연결 전 화면용 값
    #
    # 가짜 진단값을 표시하지 않고
    # 준비 중 상태로 표시
    # ----------------------------------------

    if result is None:

        prediction = "분석 준비 중"

        normal_prob = 0
        left_prob = 0
        right_prob = 0
        both_prob = 0


    else:

        # ------------------------------------
        # 모델 API가 완성된 후
        # 실제 JSON 구조에 맞게 수정할 부분
        # ------------------------------------

        prediction = result.get(
            "prediction",
            "결과 없음"
        )

        probabilities = result.get(
            "probabilities",
            {}
        )

        normal_prob = probabilities.get(
            "Normal",
            0
        )

        left_prob = probabilities.get(
            "Left",
            0
        )

        right_prob = probabilities.get(
            "Right",
            0
        )

        both_prob = probabilities.get(
            "Both",
            0
        )


    # ----------------------------------------
    # 8. 결과 페이지 출력
    # ----------------------------------------

    return render_template(

        "result.html",

        image=image_url,

        filename=original_filename,

        prediction=prediction,

        normal_prob=normal_prob,

        left_prob=left_prob,

        right_prob=right_prob,

        both_prob=both_prob

    )


# ============================================
# 로컬 실행
# ============================================

if __name__ == "__main__":

    app.run(
        debug=True
    )