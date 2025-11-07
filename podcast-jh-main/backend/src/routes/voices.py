from fastapi import APIRouter

from src.tts.engine import TTSEngine


router = APIRouter(prefix="/voices", tags=["voices"])


@router.get("")
async def get_voices():
    """사용 가능한 음성(화자) 목록 조회"""
    tts_engine = TTSEngine()

    return {
        "speakers": tts_engine.get_podcast_voices(),
        "description": "팟캐스트 생성 시 speaker 파라미터에 화자 이름(예: 'rachel', 'adam')을 지정하세요"
    }
