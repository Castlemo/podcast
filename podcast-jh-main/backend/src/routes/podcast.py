from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pathlib import Path
import os
import uuid
import json

from src.models.podcast import PodcastRequest, PodcastResponse
from src.podcast.generator import PodcastGenerator
from src.utils.pdf_parser import extract_text_from_pdf, validate_pdf_file


router = APIRouter(prefix="/podcasts", tags=["podcasts"])
podcast_generator = PodcastGenerator()


@router.post("/generate", response_model=PodcastResponse)
async def generate_podcast(request: PodcastRequest):
    """다중 화자 대화형 팟캐스트 생성 요청 (동기식 처리)

    LLM이 자동으로 2~3명의 진행자가 대화하는 스크립트를 생성하고,
    사용자가 선택한 화자 음성을 사용하여 자연스러운 대화형 팟캐스트를 생성합니다.

    팟캐스트 생성이 완료될 때까지 대기한 후 완성된 결과를 반환합니다.

    Args:
        request: 팟캐스트 생성 요청
            - topic: 주제 (topic 또는 url 중 하나 필수)
            - url: URL (topic 또는 url 중 하나 필수)
            - language: 언어 (ko, en)
            - tts_engine: TTS 엔진 (elevenlabs)
            - num_speakers: 화자 수 (2 또는 3, 기본값: 2)
            - custom_voices: 화자 음성 매핑 (필수)
                예: {"화자A": "rachel", "화자B": "adam"}
    """
    # topic 또는 url 중 하나는 필수
    if not request.topic and not request.url:
        raise HTTPException(
            status_code=400,
            detail="topic 또는 url 중 하나는 필수입니다."
        )

    # 화자 선택 필수 검증
    if not request.custom_voices:
        raise HTTPException(
            status_code=400,
            detail="화자 선택은 필수입니다. custom_voices를 제공해야 합니다."
        )

    # 화자 수에 맞는 음성 매핑 검증
    num_speakers = request.num_speakers or 2
    expected_speakers = [f"화자{chr(65+i)}" for i in range(num_speakers)]  # 화자A, 화자B, ...

    for speaker in expected_speakers:
        if speaker not in request.custom_voices:
            raise HTTPException(
                status_code=400,
                detail=f"화자 '{speaker}'에 대한 음성이 필요합니다. {num_speakers}명 모드에서는 {', '.join(expected_speakers)}에 대한 음성을 모두 지정해야 합니다."
            )

    podcast_id = str(uuid.uuid4())

    try:
        # duration_minutes를 turns로 변환 (1분 = 8 turns)
        duration_minutes = request.duration_minutes or 2
        turns = duration_minutes * 8

        # 팟캐스트 생성이 완료될 때까지 대기
        result = await podcast_generator.generate_podcast(
            podcast_id=podcast_id,
            topic=request.topic,
            url=request.url,
            language=request.language or "ko",
            tts_engine=request.tts_engine or "elevenlabs",
            num_speakers=request.num_speakers or 2,
            custom_voices=request.custom_voices,
            turns=turns,
            style=request.style or "casual"
        )

        # 생성 완료 후 결과 반환
        return PodcastResponse(
            podcast_id=podcast_id,
            status="completed",
            message="팟캐스트 생성이 완료되었습니다.",
            script_path=f"/podcasts/download/{podcast_id}/script",
            audio_path=f"/podcasts/download/{podcast_id}/audio",
            title=result.get("title"),
            dialogue_count=result.get("dialogue_count"),
            speakers_used=result.get("speakers_used")
        )

    except Exception as e:
        # 에러 발생 시 에러 응답 반환
        raise HTTPException(
            status_code=500,
            detail=f"팟캐스트 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/generate-from-pdf", response_model=PodcastResponse)
async def generate_podcast_from_pdf(
    pdf_file: UploadFile = File(..., description="PDF 파일"),
    duration_minutes: int = Form(2),
    language: str = Form("ko"),
    tts_engine: str = Form("elevenlabs"),
    num_speakers: int = Form(2),
    custom_voices: str = Form(..., description="JSON 형식의 화자 매핑"),
    style: str = Form("casual", description="팟캐스트 스타일 (casual, professional, educational, storytelling)")
):
    """PDF 파일 업로드를 통한 팟캐스트 생성

    PDF 파일의 내용을 추출하고, OpenAI를 통해 핵심 내용을 요약한 후
    팟캐스트 스크립트를 생성하여 음성으로 변환합니다.

    Args:
        pdf_file: 업로드된 PDF 파일
        duration_minutes: 팟캐스트 길이 (분)
        language: 언어 (ko, en)
        tts_engine: TTS 엔진 (elevenlabs)
        num_speakers: 화자 수 (2 또는 3)
        custom_voices: 화자 음성 매핑 (JSON 문자열)
            예: '{"화자A": "rachel", "화자B": "adam"}'
    """
    # PDF 파일 검증
    if not pdf_file.filename or not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="PDF 파일만 업로드 가능합니다."
        )

    # custom_voices JSON 파싱
    try:
        custom_voices_dict = json.loads(custom_voices)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="custom_voices는 유효한 JSON 형식이어야 합니다."
        )

    # 화자 수에 맞는 음성 매핑 검증
    expected_speakers = [f"화자{chr(65+i)}" for i in range(num_speakers)]

    for speaker in expected_speakers:
        if speaker not in custom_voices_dict:
            raise HTTPException(
                status_code=400,
                detail=f"화자 '{speaker}'에 대한 음성이 필요합니다. {num_speakers}명 모드에서는 {', '.join(expected_speakers)}에 대한 음성을 모두 지정해야 합니다."
            )

    podcast_id = str(uuid.uuid4())

    try:
        # PDF 파일 읽기
        pdf_content = await pdf_file.read()

        # PDF 파일 유효성 검증
        validate_pdf_file(pdf_content)

        # PDF에서 텍스트 추출
        pdf_text = extract_text_from_pdf(pdf_content)

        # duration_minutes를 turns로 변환 (1분 = 8 turns)
        turns = duration_minutes * 8

        # 팟캐스트 생성 (PDF 텍스트를 content로 전달)
        result = await podcast_generator.generate_podcast_from_content(
            podcast_id=podcast_id,
            content=pdf_text,
            content_type="pdf",
            original_filename=pdf_file.filename,
            language=language,
            tts_engine=tts_engine,
            num_speakers=num_speakers,
            custom_voices=custom_voices_dict,
            turns=turns,
            style=style
        )

        # 생성 완료 후 결과 반환
        return PodcastResponse(
            podcast_id=podcast_id,
            status="completed",
            message="PDF 기반 팟캐스트 생성이 완료되었습니다.",
            script_path=f"/podcasts/download/{podcast_id}/script",
            audio_path=f"/podcasts/download/{podcast_id}/audio",
            title=result.get("title"),
            dialogue_count=result.get("dialogue_count"),
            speakers_used=result.get("speakers_used")
        )

    except ValueError as e:
        # PDF 파싱 에러
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # 일반 에러
        raise HTTPException(
            status_code=500,
            detail=f"팟캐스트 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/status/{podcast_id}")
async def get_podcast_status(podcast_id: str):
    """팟캐스트 생성 상태 조회 (완전 비동기, 비블로킹)"""
    import json
    import time
    import aiofiles
    import aiofiles.os

    status_file = Path(f"output/{podcast_id}/status.txt")

    # 비동기로 파일 존재 확인 (블로킹 제거)
    try:
        file_exists = await aiofiles.os.path.exists(status_file)
    except Exception:
        file_exists = False

    # 파일이 없으면 404 대신 기본 응답 반환 (더 안정적)
    if not file_exists:
        return {
            "podcast_id": podcast_id,
            "status": "not_found",
            "message": "팟캐스트를 찾을 수 없습니다. ID를 확인해주세요.",
            "progress": 0,
            "updated_at": time.time()
        }

    # 비동기 파일 읽기 (완전히 비블로킹)
    try:
        async with aiofiles.open(status_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            status_data = json.loads(content)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 이전 형식으로 시도
        try:
            # content는 이미 읽혀있음
            old_status = content.strip()
            status_data = {
                "status": "processing" if old_status != "완료" and not old_status.startswith("오류") else ("completed" if old_status == "완료" else "failed"),
                "message": old_status,
                "progress": 0,
                "updated_at": time.time()
            }
        except Exception as read_err:
            # 파일 읽기 완전 실패 시에도 응답 반환
            return {
                "podcast_id": podcast_id,
                "status": "error",
                "message": f"상태 파일 읽기 오류: {str(read_err)}",
                "progress": 0,
                "updated_at": time.time()
            }
    except Exception as e:
        # 기타 예외 처리
        return {
            "podcast_id": podcast_id,
            "status": "error",
            "message": f"상태 확인 중 오류: {str(e)}",
            "progress": 0,
            "updated_at": time.time()
        }

    # 비동기로 스크립트 및 오디오 파일 존재 확인
    script_path = Path(f"output/{podcast_id}/script.txt")
    audio_path = Path(f"output/{podcast_id}/podcast.mp3")

    response_data = {
        "podcast_id": podcast_id,
        "status": status_data.get("status", "processing"),
        "message": status_data.get("message", "처리 중..."),
        "progress": status_data.get("progress", 0),
        "updated_at": status_data.get("updated_at", time.time())
    }

    # 비동기 파일 존재 체크 (블로킹 완전 제거)
    try:
        if await aiofiles.os.path.exists(script_path):
            response_data["script_path"] = f"/static/{podcast_id}/script.txt"

        if await aiofiles.os.path.exists(audio_path):
            response_data["audio_path"] = f"/static/{podcast_id}/podcast.mp3"
    except Exception:
        # 파일 체크 실패해도 기본 응답은 반환
        pass

    return response_data


@router.get("/download/{podcast_id}/{file_type}")
async def download_file(podcast_id: str, file_type: str):
    """팟캐스트 파일 다운로드 (스크립트, 오디오, 메타데이터)"""
    if file_type == "script":
        file_path = f"output/{podcast_id}/script.txt"
        media_type = "text/plain"
        filename = f"{podcast_id}_script.txt"
    elif file_type == "audio":
        file_path = f"output/{podcast_id}/podcast.mp3"
        media_type = "audio/mpeg"
        filename = f"{podcast_id}_audio.mp3"
    elif file_type == "metadata":
        file_path = f"output/{podcast_id}/dialogue_metadata.json"
        media_type = "application/json"
        filename = f"{podcast_id}_metadata.json"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


@router.get("/list")
async def list_podcasts():
    """팟캐스트 목록 조회"""
    output_dir = Path("output")
    podcasts = []

    if output_dir.exists():
        for podcast_dir in output_dir.iterdir():
            if podcast_dir.is_dir():
                status_file = podcast_dir / "status.txt"
                if status_file.exists():
                    with open(status_file, 'r', encoding='utf-8') as f:
                        status = f.read().strip()

                    podcasts.append({
                        "podcast_id": podcast_dir.name,
                        "status": status,
                        "created_at": podcast_dir.stat().st_ctime
                    })

    return {"podcasts": podcasts}
