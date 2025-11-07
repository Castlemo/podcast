from elevenlabs import VoiceSettings, save
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from src.utils.config import Settings
from loguru import logger
import asyncio

class TTSEngine:
    def __init__(self):
        self.settings = Settings()

        # 다중 화자를 위한 음성 매핑 (팟캐스트 대화 지원)
        # 각 화자는 고유한 voice_id를 가지며, 성별 구분 없이 사용 가능
        self.podcast_voices = {
            # 여성 음성들
            "rachel": {
                "id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "gender": "female",
                "description": "범용성이 좋은 여성 목소리",
                "suitable_for": "메인 호스트, 진행자"
            },
            "elli": {
                "id": "AZnzlk1XvdvUeBnXmlld",
                "name": "Elli",
                "gender": "female",
                "description": "자연스럽고 부드러운 여성 목소리",
                "suitable_for": "게스트, 보조 진행자"
            },
            "bella": {
                "id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Bella",
                "gender": "female",
                "description": "따뜻하고 친근한 여성 목소리",
                "suitable_for": "스토리텔러, 인터뷰어"
            },
            "lily": {
                "id": "MF3mGyEYCl7XYWbV9V6O",
                "name": "Lily",
                "gender": "female",
                "description": "전문적이고 명확한 여성 목소리",
                "suitable_for": "뉴스, 전문 해설"
            },
            # 남성 음성들
            "adam": {
                "id": "pNInz6obpgDQGcFmaJgB",
                "name": "Adam",
                "gender": "male",
                "description": "범용성이 좋은 남성 목소리",
                "suitable_for": "메인 호스트, 진행자"
            },
            "antoni": {
                "id": "ErXwobaYiN019PkySvjV",
                "name": "Antoni",
                "gender": "male",
                "description": "깊고 중후한 남성 목소리",
                "suitable_for": "내레이터, 전문가"
            },
            "arnold": {
                "id": "VR6AewLTigWG4xSOukaG",
                "name": "Arnold",
                "gender": "male",
                "description": "젊고 활기찬 남성 목소리",
                "suitable_for": "에너지 넘치는 진행자"
            },
            "sam": {
                "id": "yoZ06aMxZJJ28mfd3POQ",
                "name": "Sam",
                "gender": "male",
                "description": "권위있고 신뢰감 있는 남성 목소리",
                "suitable_for": "뉴스 앵커, 전문 해설"
            }
        }

        # 기본 화자 조합 (대화형 팟캐스트용)
        self.default_speaker_combinations = {
            "duo_mixed": ["rachel", "adam"],      # 여성+남성 듀오
            "duo_female": ["rachel", "elli"],     # 여성 듀오
            "duo_male": ["adam", "antoni"],       # 남성 듀오
            "interview": ["bella", "sam"],        # 인터뷰 형식
            "news": ["lily", "sam"]               # 뉴스 형식
        }

    async def generate_dialogue_podcast(
        self,
        dialogue_script: list[dict],
        language: str = "ko",
        tts_engine: str = "elevenlabs",
        output_path: str = "podcast.mp3"
    ) -> tuple[str, list[dict]]:
        """다중 화자 대화형 팟캐스트 오디오 생성

        Args:
            dialogue_script: 대화 스크립트 리스트
                예: [
                    {"speaker": "rachel", "text": "안녕하세요!"},
                    {"speaker": "adam", "text": "반갑습니다."}
                ]
            language: 언어 코드 (ko, en)
            tts_engine: TTS 엔진 (elevenlabs)
            output_path: 출력 파일 경로

        Returns:
            tuple: (생성된 오디오 파일 경로, 타임스탬프 메타데이터)
        """
        import tempfile
        import os

        logger.info(f"다중 화자 대화형 팟캐스트 생성 시작 - 대화 수: {len(dialogue_script)}")

        if not dialogue_script:
            raise Exception("대화 스크립트가 비어있습니다")

        temp_files = []
        dialogue_metadata = []  # 타임스탬프 메타데이터
        current_time = 0  # 현재 누적 시간 (밀리초)

        try:
            # 각 대사를 개별적으로 TTS 처리
            for i, dialogue in enumerate(dialogue_script):
                speaker = dialogue.get("speaker", "rachel")
                text = dialogue.get("text", "")

                if not text.strip():
                    logger.warning(f"대화 {i+1}: 빈 텍스트, 건너뜀")
                    continue

                # 화자 정보 가져오기
                voice_info = self.podcast_voices.get(speaker)
                if not voice_info:
                    logger.warning(f"알 수 없는 화자 '{speaker}', 기본값 'rachel' 사용")
                    voice_info = self.podcast_voices["rachel"]

                logger.info(f"대화 {i+1}/{len(dialogue_script)} - 화자: {voice_info['name']}")

                # 임시 파일 생성
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_dialogue_{i}.mp3")
                temp_files.append(temp_file.name)
                temp_file.close()

                # TTS 변환
                voice_id = voice_info["id"]
                if language == "ko":
                    await self.text_to_speech_korean_optimized(text, voice_id, temp_file.name)
                else:
                    await self.text_to_speech(text, voice_id, temp_file.name)

            # 모든 대사 오디오를 하나로 병합하면서 타임스탬프 기록
            logger.info("대화 오디오 파일 병합 중...")
            combined_audio = None
            for i, temp_file in enumerate(temp_files):
                dialogue_audio = AudioSegment.from_mp3(temp_file)
                duration_ms = len(dialogue_audio)  # 오디오 길이 (밀리초)

                # 현재 대사의 화자 정보
                dialogue = dialogue_script[i]
                speaker = dialogue.get("speaker", "rachel")
                text = dialogue.get("text", "")

                # 타임스탬프 메타데이터 기록
                voice_info = self.podcast_voices.get(speaker, self.podcast_voices["rachel"])
                dialogue_metadata.append({
                    "index": i,
                    "speaker": speaker,
                    "speaker_name": voice_info["name"],
                    "gender": voice_info["gender"],
                    "text": text,
                    "start_time": current_time / 1000,  # 초 단위로 변환
                    "end_time": (current_time + duration_ms) / 1000,  # 초 단위로 변환
                    "duration": duration_ms / 1000  # 초 단위로 변환
                })

                if combined_audio is None:
                    combined_audio = dialogue_audio
                else:
                    # 대사 사이에 약간의 무음 추가 (자연스러운 대화 흐름)
                    silence = AudioSegment.silent(duration=500)  # 500ms 무음
                    combined_audio = combined_audio + silence + dialogue_audio
                    current_time += 500  # 무음 시간 추가

                current_time += duration_ms

            # 최종 파일로 내보내기
            if combined_audio:
                combined_audio.export(output_path, format="mp3", bitrate="192k")
                logger.info(f"다중 화자 팟캐스트 생성 완료: {output_path}")
                logger.info(f"타임스탬프 메타데이터 {len(dialogue_metadata)}개 생성")
            else:
                raise Exception("병합할 오디오가 없습니다")

            return output_path, dialogue_metadata

        finally:
            # 임시 파일 정리
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"임시 파일 삭제 실패 {temp_file}: {str(e)}")

    async def text_to_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default voice (Rachel ID)
        output_path: str = "output.mp3"
    ) -> str:
        """ElevenLabs를 사용한 텍스트 음성 변환"""
        try:
            client = ElevenLabs(api_key=self.settings.elevenlabs_api_key)

            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.5,      # 안정성 증가로 더 자연스러운 음성
                    similarity_boost=0.8, # 음성 유사성 증가
                    style=0.1,           # 약간의 스타일 추가로 생동감 향상
                    use_speaker_boost=True
                )
            )

            save(audio, output_path)
            return output_path
        except Exception as e:
            raise Exception(f"ElevenLabs TTS 변환 중 오류: {str(e)}")

    async def text_to_speech_korean_optimized(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        output_path: str = "output.mp3",
        max_retries: int = 3
    ) -> str:
        """한국어에 최적화된 텍스트 음성 변환 (재시도 로직 포함)"""

        # 한국어 발음에 최적화된 설정
        # 팟캐스트 특성상 자연스러운 억양과 감정 표현이 중요
        korean_optimized_settings = VoiceSettings(
            stability=0.5,         # 자연스러운 억양 변화를 위해 안정성 낮춤
            similarity_boost=0.75,  # 원본 음성 특성 유지하면서 유연성 확보
            style=0.0,            # 팟캐스트 특성상 더 풍부한 표현력 필요
            use_speaker_boost=True  # 명확한 한국어 발음을 위한 부스트
        )

        # 한국어 텍스트 전처리
        processed_text = self._preprocess_korean_text(text)

        logger.info(f"한국어 TTS 변환 시작 - 음성: {voice_id}, 텍스트 길이: {len(processed_text)}")

        # 재시도 로직
        last_error = None
        for attempt in range(max_retries):
            try:
                client = ElevenLabs(api_key=self.settings.elevenlabs_api_key)

                audio = client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=processed_text,
                    voice_settings=korean_optimized_settings,
                    model_id="eleven_turbo_v2_5"
                )

                save(audio, output_path)
                logger.info(f"한국어 TTS 변환 성공: {output_path}")
                return output_path

            except Exception as e:
                last_error = e
                logger.warning(f"TTS 변환 시도 {attempt + 1}/{max_retries} 실패: {str(e)}")

                if attempt < max_retries - 1:
                    # 지수 백오프 전략으로 재시도 대기
                    wait_time = 2 ** attempt
                    logger.info(f"{wait_time}초 후 재시도...")
                    await asyncio.sleep(wait_time)

        # 모든 재시도 실패
        logger.error(f"한국어 TTS 변환 최종 실패 (모든 재시도 소진): {str(last_error)}")
        raise Exception(f"한국어 최적화 TTS 변환 중 오류 (재시도 {max_retries}회 실패): {str(last_error)}")

    def _preprocess_korean_text(self, text: str) -> str:
        """한국어 텍스트 전처리 (발음 개선)"""
        # 숫자를 한글로 변환하는 기본적인 처리
        import re

        # 영어 단어 앞뒤에 적절한 공백 추가
        text = re.sub(r'([\가-\힣])([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])([\가-\힣])', r'\1 \2', text)

        # 문장 끝 쉼표와 마침표 뒤에 적절한 간격 추가
        text = re.sub(r'([,.])([^\s])', r'\1 \2', text)

        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def enhance_audio(self, input_path: str, output_path: str, apply_speed_adjustment: bool = False) -> str:
        """오디오 품질 향상 처리

        Args:
            input_path: 입력 오디오 파일 경로
            output_path: 출력 오디오 파일 경로
            apply_speed_adjustment: 속도 조정 적용 여부 (기본값: False, ElevenLabs는 이미 최적화됨)
        """
        try:
            audio = AudioSegment.from_mp3(input_path)

            # 1. 오디오 레벨 정규화 (너무 작거나 큰 소리 방지)
            audio = audio.normalize()

            # 2. 속도 조정 (선택적, 한국어는 보통 적용하지 않음)
            if apply_speed_adjustment:
                # 2% 속도 감소로 더 명확한 발음
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * 0.98)
                }).set_frame_rate(audio.frame_rate)

            # 3. 볼륨 부스트 (명확성 향상, 너무 크지 않게)
            audio = audio + 1.5

            # 4. 자연스러운 시작/끝을 위한 페이드 인/아웃
            # 페이드 시간을 더 길게 하여 부드러운 전환
            audio = audio.fade_in(800).fade_out(1000)

            # 5. 고품질로 내보내기
            # 팟캐스트 표준 비트레이트 192k (320k는 과도하게 큰 파일 크기)
            audio.export(output_path, format="mp3", bitrate="192k",
                        parameters=["-q:a", "0"])  # 최고 품질 인코딩

            return output_path

        except Exception as e:
            raise Exception(f"오디오 향상 중 오류: {str(e)}")

    def add_background_music(
        self,
        speech_path: str,
        music_path: str,
        output_path: str,
        music_volume: float = 0.1
    ) -> str:
        try:
            speech = AudioSegment.from_mp3(speech_path)
            music = AudioSegment.from_mp3(music_path)

            music = music - (20 - (music_volume * 20))

            if len(music) < len(speech):
                loops_needed = (len(speech) // len(music)) + 1
                music = music * loops_needed

            music = music[:len(speech)]

            combined = speech.overlay(music)
            combined.export(output_path, format="mp3", bitrate="320k")

            return output_path

        except Exception as e:
            raise Exception(f"배경음악 추가 중 오류: {str(e)}")

    def get_podcast_voices(self) -> dict:
        """팟캐스트용 음성 목록 반환"""
        return self.podcast_voices

    async def get_available_voices(self) -> list:
        """ElevenLabs에서 사용 가능한 음성 목록 조회"""
        try:
            client = ElevenLabs(api_key=self.settings.elevenlabs_api_key)
            voices_response = client.voices.get_all()

            voice_list = []
            for voice in voices_response.voices:
                voice_info = {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category if hasattr(voice, 'category') else "general",
                    "settings": voice.settings.__dict__ if hasattr(voice, 'settings') else {},
                    "is_podcast_voice": self._is_podcast_voice(voice.voice_id)
                }
                voice_list.append(voice_info)

            return voice_list
        except Exception as e:
            raise Exception(f"ElevenLabs 음성 목록 조회 중 오류: {str(e)}")

    def _is_podcast_voice(self, voice_id: str) -> bool:
        """음성이 팟캐스트용 음성인지 확인"""
        for speaker_info in self.podcast_voices.values():
            if voice_id == speaker_info["id"]:
                return True
        return False
