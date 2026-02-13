import sys
import os
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify
from scraper import scrape_gallery
from analyzer import analyze_posts


def resource_path(relative_path):
    """PyInstaller 번들 환경에서 리소스 경로를 올바르게 찾는다."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


app = Flask(__name__, template_folder=resource_path("templates"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    url = data.get("url", "").strip()
    pages = int(data.get("pages", 3))

    if not url:
        return jsonify({"error": "URL을 입력해주세요."}), 400

    if "dcinside.com" not in url:
        return jsonify({"error": "DC인사이드 갤러리 URL을 입력해주세요."}), 400

    pages = max(1, min(pages, 10))

    try:
        posts = scrape_gallery(url, pages=pages)
        if not posts:
            return jsonify({"error": "게시글을 가져올 수 없습니다. URL을 확인해주세요."})

        result = analyze_posts(posts)

        # JSON 직렬화를 위해 top_keywords 튜플을 리스트로 변환
        result["top_keywords"] = [
            {"keyword": kw, "count": cnt} for kw, cnt in result["top_keywords"]
        ]
        # 불필요한 큰 데이터 제거 (matched_keywords 리스트는 요약만 전달)
        for p in result["negative_posts"]:
            p["matched_keywords_summary"] = list(set(p["matched_keywords"]))
            del p["matched_keywords"]
            del p["body"]  # 본문 전체 대신 preview만 전달

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"크롤링 중 오류가 발생했습니다: {str(e)}"}), 500


if __name__ == "__main__":
    is_frozen = getattr(sys, "frozen", False)

    if is_frozen:
        # exe 실행 시: 브라우저 자동 오픈, 콘솔 표시
        print("=" * 50)
        print("  DC갤러리 부정적 게시글 분석기")
        print("  브라우저에서 자동으로 열립니다...")
        print("  종료하려면 이 창을 닫으세요.")
        print("=" * 50)
        threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
        app.run(debug=False, host="127.0.0.1", port=5000)
    else:
        app.run(debug=True, host="0.0.0.0", port=5000)
