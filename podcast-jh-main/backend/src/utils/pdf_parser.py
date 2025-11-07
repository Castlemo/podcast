"""
PDF에서 텍스트를 추출하는 모듈
"""
from PyPDF2 import PdfReader
import io
from loguru import logger


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    PDF 파일에서 텍스트를 추출합니다.

    Args:
        pdf_file: PDF 파일의 바이트 데이터

    Returns:
        추출된 텍스트

    Raises:
        ValueError: PDF를 읽을 수 없거나 텍스트가 너무 짧은 경우
    """
    try:
        # 바이트 데이터를 파일 객체로 변환
        pdf_stream = io.BytesIO(pdf_file)

        # PDF 리더 생성
        reader = PdfReader(pdf_stream)

        # 전체 텍스트 추출
        text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                logger.debug(f"페이지 {page_num + 1} 텍스트 추출 완료: {len(page_text)} 문자")
            except Exception as e:
                logger.warning(f"페이지 {page_num + 1} 텍스트 추출 실패: {str(e)}")
                continue

        # 텍스트 정리
        text = text.strip()

        # 텍스트 길이 검증
        if not text or len(text) < 100:
            raise ValueError("PDF에서 추출된 텍스트가 너무 짧습니다. 텍스트가 포함된 PDF인지 확인해주세요.")

        logger.info(f"PDF 텍스트 추출 완료: 총 {len(reader.pages)} 페이지, {len(text)} 문자")

        return text

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        logger.error(f"PDF 파싱 오류: {str(e)}")
        raise ValueError(f"PDF 파일을 읽을 수 없습니다: {str(e)}")


def validate_pdf_file(pdf_file: bytes, max_size_mb: int = 50) -> bool:
    """
    PDF 파일의 유효성을 검증합니다.

    Args:
        pdf_file: PDF 파일의 바이트 데이터
        max_size_mb: 최대 파일 크기 (MB)

    Returns:
        유효한 경우 True

    Raises:
        ValueError: 파일이 유효하지 않은 경우
    """
    # 파일 크기 검증
    file_size_mb = len(pdf_file) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValueError(f"PDF 파일이 너무 큽니다. 최대 {max_size_mb}MB까지 업로드 가능합니다. (현재: {file_size_mb:.2f}MB)")

    # PDF 매직 넘버 검증
    if not pdf_file.startswith(b'%PDF'):
        raise ValueError("유효한 PDF 파일이 아닙니다.")

    return True
