# DC갤러리 부정적 게시글 분석기

DC인사이드 갤러리 URL을 입력하면 게시글을 크롤링하고, 부정적 키워드 기반으로 필터링하여 결과를 웹 UI에서 보여주는 프로그램입니다.

## 기능

- DC인사이드 일반/마이너 갤러리 크롤링
- 한국어 부정 키워드 기반 감성 분석 (욕설, 비판, 혐오 카테고리)
- 부정 게시글 필터링 및 점수 산출
- 주요 부정 키워드 빈도 집계 및 요약
- 다크 테마 웹 UI

## 스크린샷

![입력 화면](https://via.placeholder.com/800x400?text=DC+Gallery+Analyzer)

## 실행 방법

### exe 파일로 실행 (Python 설치 불필요)

[Releases](https://github.com/truebird2201/dc-gallery-analyzer/releases)에서 `DC갤러리분석기.exe`를 다운로드하고 더블클릭하면 자동으로 브라우저가 열립니다.

### 소스코드로 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

브라우저에서 `http://localhost:5000` 접속 후 DC갤러리 URL을 입력하면 분석이 시작됩니다.

## 사용법

1. DC갤러리 URL 입력 (예: `https://gall.dcinside.com/board/lists/?id=programming`)
2. 크롤링할 페이지 수 선택 (1~5페이지)
3. "분석 시작" 클릭
4. 결과 확인: 부정 비율, 주요 키워드, 부정 게시글 목록

## 프로젝트 구조

```
├── app.py              # Flask 웹 서버
├── scraper.py          # DC갤러리 크롤링 모듈
├── analyzer.py         # 부정 키워드 필터링 및 분석
├── templates/
│   └── index.html      # 웹 UI
└── requirements.txt    # 의존성
```

## 기술 스택

- Python 3
- Flask
- requests + BeautifulSoup4
- PyInstaller (exe 빌드)

## exe 빌드 방법

```bash
pip install pyinstaller
pyinstaller --onefile --console --name "DC갤러리분석기" --add-data "templates;templates" app.py
```

`dist/DC갤러리분석기.exe` 파일이 생성됩니다.

## 라이선스

MIT License
