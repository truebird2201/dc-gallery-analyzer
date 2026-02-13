import re
from collections import Counter

# 부정적 키워드 사전
NEGATIVE_KEYWORDS = {
    "욕설": [
        "시발", "씨발", "ㅅㅂ", "시바", "씨바", "개새끼", "ㄱㅅㄲ",
        "병신", "ㅂㅅ", "지랄", "ㅈㄹ", "꺼져", "닥쳐",
        "미친", "ㅁㅊ", "좆", "ㅈ같", "존나", "ㅈㄴ",
        "새끼", "ㅅㄲ", "멍청", "바보", "등신", "찐따",
    ],
    "비판": [
        "쓰레기", "최악", "실망", "별로", "짜증", "화남", "싫다",
        "싫어", "후회", "망했", "노답", "답없", "답이없",
        "구리다", "구림", "별로임", "개판", "엉망", "형편없",
        "불만", "불쾌", "짜증남", "짜증나", "열받", "빡침",
        "빡치", "어이없", "한심", "못한다", "못함", "무능",
        "거지같", "쓸모없", "폐급", "하자", "결함", "고장",
    ],
    "혐오": [
        "혐오", "역겹", "구역질", "토나", "꼴불견", "더럽",
        "추하", "징그럽", "소름", "끔찍", "최악",
        "불쾌", "메스껍", "욕나오", "치떨",
    ],
}

# 모든 키워드를 하나의 리스트로 펼침
ALL_KEYWORDS = []
KEYWORD_CATEGORY = {}
for category, words in NEGATIVE_KEYWORDS.items():
    for w in words:
        ALL_KEYWORDS.append(w)
        KEYWORD_CATEGORY[w] = category

# 부정 판정 임계값 (매칭 키워드 수)
THRESHOLD = 2


def analyze_post(post):
    """
    개별 게시글의 부정 점수를 계산한다.

    Returns:
        dict: 원본 post + negative_score, matched_keywords
    """
    text = (post.get("title", "") + " " + post.get("body", "")).lower()
    matched = []

    for keyword in ALL_KEYWORDS:
        count = text.count(keyword.lower())
        if count > 0:
            matched.extend([keyword] * count)

    return {
        **post,
        "negative_score": len(matched),
        "matched_keywords": matched,
    }


def analyze_posts(posts, threshold=THRESHOLD):
    """
    게시글 목록을 분석하여 부정적 게시글을 필터링하고 요약을 생성한다.

    Returns:
        dict: {
            "total": 전체 게시글 수,
            "negative_count": 부정 게시글 수,
            "negative_ratio": 부정 비율 (%),
            "top_keywords": [(키워드, 빈도), ...],
            "negative_posts": [분석된 부정 게시글 목록],
        }
    """
    analyzed = [analyze_post(p) for p in posts]
    negative_posts = [p for p in analyzed if p["negative_score"] >= threshold]

    # 부정 게시글을 점수 내림차순 정렬
    negative_posts.sort(key=lambda x: x["negative_score"], reverse=True)

    # 키워드 빈도 집계
    all_matched = []
    for p in negative_posts:
        all_matched.extend(p["matched_keywords"])

    keyword_counts = Counter(all_matched).most_common(15)

    # 카테고리별 집계
    category_counts = Counter()
    for kw, cnt in keyword_counts:
        cat = KEYWORD_CATEGORY.get(kw, "기타")
        category_counts[cat] += cnt

    total = len(posts)
    neg_count = len(negative_posts)
    ratio = round((neg_count / total * 100), 1) if total > 0 else 0

    # 본문 미리보기 (200자)
    for p in negative_posts:
        body = p.get("body", "")
        p["body_preview"] = body[:200] + "..." if len(body) > 200 else body

    return {
        "total": total,
        "negative_count": neg_count,
        "negative_ratio": ratio,
        "top_keywords": keyword_counts,
        "category_summary": dict(category_counts),
        "negative_posts": negative_posts,
    }
