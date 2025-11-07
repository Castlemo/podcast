from pydantic import BaseModel
from typing import Optional, List, Dict, Literal


class PodcastRequest(BaseModel):
    """팟캐스트 생성 요청 모델"""
    topic: Optional[str] = None  # 주제 기반 팟캐스트 생성
    url: Optional[str] = None  # URL 기반 팟캐스트 생성
    # PDF 업로드는 FormData로 별도 처리됨
    duration_minutes: Optional[int] = 2
    language: Optional[str] = "ko"
    tts_engine: Optional[str] = "elevenlabs"
    num_speakers: Optional[int] = 2  # 화자 수 (2 또는 3)
    custom_voices: Optional[Dict[str, str]] = None  # 사용자 정의 화자 매핑 (예: {"화자A": "rachel", "화자B": "adam"})
    style: Optional[Literal["casual", "professional", "educational", "storytelling"]] = "casual"  # 팟캐스트 스타일


class PodcastResponse(BaseModel):
    """팟캐스트 생성 응답 모델"""
    podcast_id: str
    status: str
    message: str
    script_path: Optional[str] = None
    audio_path: Optional[str] = None
    title: Optional[str] = None
    dialogue_count: Optional[int] = None
    speakers_used: Optional[List[str]] = None
