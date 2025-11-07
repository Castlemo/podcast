from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys

from src.routes import podcast_router, voices_router
from src.utils.config import Settings

# Windows에서 ProactorEventLoop 관련 오류 방지
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(
    title="AI Podcast Generator",
    description="LLM과 TTS를 활용한 AI 팟캐스트 자동 생성 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # CORS preflight 캐싱 시간
)

settings = Settings()

# 라우터 등록
app.include_router(podcast_router)
app.include_router(voices_router)

# 정적 파일 서빙 설정 (오디오 파일 다운로드용)
app.mount("/output", StaticFiles(directory="output"), name="output")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # 포트 변경
        timeout_keep_alive=75,  # Keep-alive 타임아웃 (75초)
        timeout_graceful_shutdown=30,  # 정상 종료 타임아웃
        access_log=True,
        log_level="info"
    )