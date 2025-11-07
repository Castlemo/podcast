"""
URL에서 HTML을 가져와 텍스트를 추출하는 모듈
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
import re


def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    """
    URL에서 HTML을 가져옵니다.

    Args:
        url: 가져올 URL
        timeout: 요청 타임아웃 (초)

    Returns:
        HTML 문자열 또는 None
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


def clean_html_text(html: str) -> str:
    """
    HTML에서 텍스트를 추출하고 정리합니다.

    Args:
        html: HTML 문자열

    Returns:
        정리된 텍스트
    """
    soup = BeautifulSoup(html, 'html.parser')

    # 스크립트, 스타일 태그 제거
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()

    # 텍스트 추출
    text = soup.get_text()

    # 공백 정리
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def parse_url_to_text(url: str) -> str:
    """
    URL에서 HTML을 가져와 텍스트를 추출합니다.

    Args:
        url: 파싱할 URL

    Returns:
        추출된 텍스트

    Raises:
        ValueError: URL을 가져오거나 파싱할 수 없는 경우
    """
    # HTML 가져오기
    html = fetch_html(url)
    if not html:
        raise ValueError(f"URL에서 내용을 가져올 수 없습니다: {url}")

    # 텍스트 정리
    text = clean_html_text(html)
    if not text or len(text) < 100:
        raise ValueError("추출된 텍스트가 너무 짧습니다")

    return text
