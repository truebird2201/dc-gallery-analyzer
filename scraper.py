import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://gall.dcinside.com/",
}

BASE_URL = "https://gall.dcinside.com"


def extract_gall_id(url):
    """DC갤러리 URL에서 갤러리 ID를 추출한다."""
    parsed = urlparse(url)
    # /board/lists/?id=xxx 형태
    qs = parse_qs(parsed.query)
    if "id" in qs:
        return qs["id"][0]
    # /mgallery/board/lists/?id=xxx (마이너 갤러리)
    # 또는 경로에서 추출: /board/lists/xxx
    path_parts = parsed.path.rstrip("/").split("/")
    if path_parts:
        return path_parts[-1]
    return None


def is_minor_gallery(url):
    """마이너 갤러리 여부를 확인한다."""
    return "mgallery" in url


def fetch_post_list(gall_id, page=1, minor=False):
    """갤러리 리스트 페이지에서 게시글 목록을 가져온다."""
    if minor:
        list_url = f"https://gall.dcinside.com/mgallery/board/lists/"
    else:
        list_url = f"https://gall.dcinside.com/board/lists/"

    params = {"id": gall_id, "page": page}
    resp = requests.get(list_url, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    posts = []

    rows = soup.select("tr.ub-content.us-post")
    for row in rows:
        # 공지 제외
        gall_num = row.select_one("td.gall_num")
        if gall_num and gall_num.get_text(strip=True) in ("공지", "설문", "AD"):
            continue

        title_tag = row.select_one("td.gall_tit a:not(.reply_numbox)")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        if href and not href.startswith("http"):
            href = BASE_URL + href

        writer_tag = row.select_one("td.gall_writer .nickname")
        writer = writer_tag.get_text(strip=True) if writer_tag else "익명"

        date_tag = row.select_one("td.gall_date")
        date = date_tag.get("title", date_tag.get_text(strip=True)) if date_tag else ""

        posts.append({
            "title": title,
            "url": href,
            "writer": writer,
            "date": date,
            "body": "",
        })

    return posts


def fetch_post_body(post_url):
    """개별 게시글의 본문 내용을 크롤링한다."""
    try:
        resp = requests.get(post_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        body_tag = soup.select_one("div.write_div")
        if body_tag:
            return body_tag.get_text(separator="\n", strip=True)
        return ""
    except Exception:
        return ""


def scrape_gallery(url, pages=3):
    """
    DC갤러리 URL을 받아 지정된 페이지 수만큼 게시글을 크롤링한다.

    Returns:
        list[dict]: 게시글 목록 (title, url, writer, date, body)
    """
    gall_id = extract_gall_id(url)
    if not gall_id:
        raise ValueError("갤러리 ID를 URL에서 추출할 수 없습니다.")

    minor = is_minor_gallery(url)
    all_posts = []

    for page in range(1, pages + 1):
        posts = fetch_post_list(gall_id, page=page, minor=minor)
        all_posts.extend(posts)
        time.sleep(0.5)

    # 각 게시글 본문 크롤링
    for post in all_posts:
        if post["url"]:
            post["body"] = fetch_post_body(post["url"])
            time.sleep(0.3)

    return all_posts
