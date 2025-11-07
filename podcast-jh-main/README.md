# AI 팟캐스트 자동 생성 시스템

LLM과 TTS를 활용하여 주제만 입력하면 자동으로 팟캐스트를 생성하는 FastAPI 기반 시스템입니다.

## 기능

- 🤖 **AI 스크립트 생성**: OpenAI GPT를 활용한 자연스러운 팟캐스트 대본 생성
- 🔊 **고품질 TTS**: ElevenLabs를 활용한 고품질 자연스러운 음성 합성
- 🎵 **오디오 후처리**: 음질 향상 및 배경음악 추가 기능
- 🌐 **REST API**: FastAPI 기반 RESTful API 제공
- 📱 **다국어 지원**: 한국어, 영어 지원
- 🎭 **다양한 음성**: 남성/여성 음성 선택 가능

## 프로젝트 구조

```
podcast/
├── src/
│   ├── llm/                # LLM 클라이언트 모듈
│   │   ├── __init__.py
│   │   └── openai_client.py
│   ├── tts/                # TTS 엔진 모듈
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── podcast/            # 팟캐스트 생성 로직
│   │   ├── __init__.py
│   │   └── generator.py
│   └── utils/              # 유틸리티 모듈
│       ├── __init__.py
│       └── config.py
├── output/                 # 생성된 팟캐스트 파일들
├── config/                 # 설정 파일들
├── examples/               # 예제 파일들
├── main.py                 # FastAPI 애플리케이션
├── requirements.txt        # 의존성 패키지
├── .env.example           # 환경변수 예제
├── CLAUDE.md              # Claude Code 설정
└── README.md              # 프로젝트 문서
```

## 설치 및 설정

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\\Scripts\\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집하여 API 키 설정
OPENAI_API_KEY=your_actual_openai_api_key
ELEVENLABS_API_KEY=your_actual_elevenlabs_api_key
```

### 3. 서버 실행

```bash
# 개발 서버 실행
python main.py

# 또는 uvicorn 직접 사용
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API 사용법

### 팟캐스트 생성

```bash
curl -X POST "http://localhost:8000/generate" \\
     -H "Content-Type: application/json" \\
     -d '{
       "topic": "인공지능의 미래",
       "duration_minutes": 5,
       "voice_type": "female",
       "language": "ko"
     }'
```

### 생성 상태 확인

```bash
curl "http://localhost:8000/status/{podcast_id}"
```

### 팟캐스트 목록 조회

```bash
curl "http://localhost:8000/list"
```

### 파일 다운로드

```bash
# 스크립트 다운로드
curl "http://localhost:8000/download/{podcast_id}/script"

# 오디오 다운로드
curl "http://localhost:8000/download/{podcast_id}/audio"
```

## 주요 특징

### AI 스크립트 생성
- OpenAI GPT-4를 활용한 자연스러운 대화체 스크립트 생성
- 주제에 맞는 구조화된 내용 (인트로-본문-아웃트로)
- 한국어/영어 다국어 지원

### 고품질 TTS
- ElevenLabs 고품질 음성 합성
- 다양한 프리미엄 음성 옵션 (남성/여성, 언어별)
- 자연스러운 감정 표현과 발음

### 오디오 후처리
- 음량 정규화 및 향상
- 페이드 인/아웃 효과
- 배경음악 추가 기능 (선택사항)

### 비동기 처리
- FastAPI의 백그라운드 태스크를 활용한 비동기 팟캐스트 생성
- 실시간 진행 상태 확인

## 개발 명령어

```bash
# 개발 서버 실행 (자동 재시작)
python main.py

# 또는
uvicorn main:app --reload

# 의존성 업데이트
pip freeze > requirements.txt
```

## 환경변수 설명

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | (필수) |
| `ELEVENLABS_API_KEY` | ElevenLabs API 키 | (필수) |
| `DEFAULT_VOICE_TYPE` | 기본 음성 타입 | `female` |
| `DEFAULT_LANGUAGE` | 기본 언어 | `ko` |
| `DEFAULT_DURATION` | 기본 팟캐스트 길이(분) | `5` |
| `OUTPUT_DIRECTORY` | 출력 디렉토리 | `output` |
| `MAX_SCRIPT_LENGTH` | 최대 스크립트 길이 | `10000` |

## 라이선스

MIT License

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의사항

프로젝트에 대한 문의나 제안사항이 있으시면 이슈를 생성해 주세요.