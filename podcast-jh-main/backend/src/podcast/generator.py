from pathlib import Path
from typing import Optional, List, Dict
import re
from loguru import logger

from src.llm.openai_client import OpenAIClient
from src.tts.engine import TTSEngine
from src.utils.config import Settings
from src.utils.url_parser import parse_url_to_text

class PodcastGenerator:
    def __init__(self):
        self.settings = Settings()
        self.llm_client = OpenAIClient()
        self.tts_engine = TTSEngine()

    def _parse_dialogue_script(
        self,
        script: str,
        num_speakers: int = 2,
        custom_voices: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """LLM이 생성한 대화 스크립트를 파싱하여 화자별 대사 리스트로 변환

        Args:
            script: "화자A: 안녕하세요\n화자B: 반갑습니다" 또는 "Speaker A: Hello\nSpeaker B: Hi" 형식의 스크립트
            num_speakers: 화자 수 (2 또는 3)
            custom_voices: 사용자 정의 화자 매핑 (우선순위가 더 높음)

        Returns:
            [{"speaker": "rachel", "text": "안녕하세요"}, ...] 형식의 리스트
        """
        dialogue_list: List[Dict[str, str]] = []

        if not custom_voices:
            raise ValueError("화자 선택은 필수입니다. custom_voices를 제공해야 합니다.")

        speaker_mapping = custom_voices
        logger.info(f"사용자 정의 화자 매핑 사용: {custom_voices}")

        # 정규식으로 화자 패턴 파싱 (한국어 "화자A" 또는 영어 "Speaker A" 모두 매칭)
        # 통합 패턴: 한국어와 영어 모두 매칭
        pattern = r'((?:화자|Speaker\s+)[A-C]):\s*(.+?)(?=\n(?:화자|Speaker\s+)[A-C]:|$)'
        matches = re.findall(pattern, script, re.DOTALL | re.IGNORECASE)

        logger.info(f"스크립트에서 {len(matches)}개의 대사 발견 (화자 수: {num_speakers})")

        for speaker_label, text in matches:
            text = text.strip()
            if not text:
                continue

            # "Speaker A" → "화자A" 로 변환 (custom_voices 키와 맞추기 위해)
            speaker_label = speaker_label.strip()
            if "speaker" in speaker_label.lower():
                # "Speaker A" 또는 "speaker a" → "화자A"
                letter = speaker_label.split()[-1].upper()
                speaker_label = f"화자{letter}"

            # 화자 레이블을 실제 음성 ID로 매핑
            actual_speaker = speaker_mapping.get(speaker_label)
            if not actual_speaker:
                raise ValueError(f"화자 '{speaker_label}'에 대한 음성이 매핑되지 않았습니다.")

            dialogue_list.append({
                "speaker": actual_speaker,
                "text": text
            })

            logger.debug(f"{speaker_label} ({actual_speaker}): {text[:50]}...")

        if not dialogue_list:
            raise ValueError("파싱된 대사가 없습니다. 스크립트 형식을 확인해주세요.")

        return dialogue_list

    async def generate_podcast_from_content(
        self,
        podcast_id: str,
        content: str,
        content_type: str = "pdf",
        original_filename: Optional[str] = None,
        language: str = "ko",
        tts_engine: str = "elevenlabs",
        num_speakers: int = 2,
        custom_voices: Optional[Dict[str, str]] = None,
        turns: int = 8,
        style: str = "casual"
    ) -> dict:
        """콘텐츠(PDF 텍스트 등)에서 팟캐스트 생성

        Args:
            podcast_id: 팟캐스트 ID
            content: 원본 텍스트 콘텐츠
            content_type: 콘텐츠 타입 (pdf, text 등)
            original_filename: 원본 파일명
            language: 언어 (ko, en)
            tts_engine: TTS 엔진
            num_speakers: 화자 수 (2 또는 3)
            custom_voices: 사용자 정의 화자 매핑
            turns: 대화 턴 수
        """
        try:
            output_dir = Path(f"output/{podcast_id}")
            output_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"콘텐츠 기반 팟캐스트 생성 시작: {podcast_id} - 타입: {content_type}, 길이: {len(content)} 문자")

            # 원본 콘텐츠 저장
            if content_type == "pdf":
                self._update_status(podcast_id, "PDF 내용 처리 중...", 5)
                content_path = output_dir / "pdf_content.txt"
                with open(content_path, 'w', encoding='utf-8') as f:
                    if original_filename:
                        f.write(f"원본 파일명: {original_filename}\n\n")
                    f.write("=== 추출된 PDF 내용 ===\n\n")
                    f.write(content)

            # OpenAI로 핵심 내용 추출
            self._update_status(podcast_id, "핵심 내용 추출 중...", 10)
            key_content = await self.llm_client.extract_key_content(content)
            logger.info(f"핵심 내용 추출 완료: {len(key_content)} 문자")

            # 추출된 핵심 내용 저장
            key_content_path = output_dir / "key_content.txt"
            with open(key_content_path, 'w', encoding='utf-8') as f:
                f.write(key_content)

            # 대화 스크립트 생성
            self._update_status(podcast_id, "대화 스크립트 생성 중...", 25)
            logger.info(f"팟캐스트 스크립트 생성 - 화자 수: {num_speakers}, 턴 수: {turns}")

            script = await self.llm_client.generate_podcast_script(
                topic=key_content,
                language=language,
                num_speakers=num_speakers,
                turns=turns,
                style=style
            )

            script_path = output_dir / "script.txt"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)

            self._update_status(podcast_id, "제목 생성 중...", 40)
            title = await self.llm_client.generate_title(script)

            title_path = output_dir / "title.txt"
            with open(title_path, 'w', encoding='utf-8') as f:
                f.write(title)

            # 스크립트 파싱
            self._update_status(podcast_id, "대화 스크립트 파싱 중...", 50)
            dialogue_list = self._parse_dialogue_script(script, num_speakers, custom_voices)

            logger.info(f"총 {len(dialogue_list)}개의 대사로 구성된 대화형 팟캐스트 생성")

            # 다중 화자 대화형 오디오 생성
            self._update_status(podcast_id, f"다중 화자 오디오 생성 중... (대사 {len(dialogue_list)}개)", 60)
            audio_path = output_dir / "podcast.mp3"

            audio_file, dialogue_metadata = await self.tts_engine.generate_dialogue_podcast(
                dialogue_script=dialogue_list,
                language=language,
                tts_engine=tts_engine,
                output_path=str(audio_path)
            )

            # 타임스탬프 메타데이터 저장
            metadata_path = output_dir / "dialogue_metadata.json"
            import json
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "podcast_id": podcast_id,
                    "content_type": content_type,
                    "original_filename": original_filename,
                    "total_duration": dialogue_metadata[-1]["end_time"] if dialogue_metadata else 0,
                    "dialogue_count": len(dialogue_metadata),
                    "dialogues": dialogue_metadata
                }, f, ensure_ascii=False, indent=2)

            self._update_status(podcast_id, "오디오 후처리 중...", 90)
            enhanced_path = output_dir / "podcast_enhanced.mp3"
            self.tts_engine.enhance_audio(str(audio_path), str(enhanced_path))

            if enhanced_path.exists():
                audio_path.unlink()
                enhanced_path.rename(audio_path)

            self._update_status(podcast_id, "완료", 100)

            logger.info(f"콘텐츠 기반 팟캐스트 생성 완료: {podcast_id}")

            return {
                "podcast_id": podcast_id,
                "status": "completed",
                "script_path": str(script_path),
                "audio_path": str(audio_path),
                "title": title,
                "dialogue_count": len(dialogue_list),
                "speakers_used": list(set(d["speaker"] for d in dialogue_list))
            }

        except Exception as e:
            self._update_status(podcast_id, f"오류: {str(e)}")
            logger.error(f"콘텐츠 기반 팟캐스트 생성 실패: {podcast_id} - {str(e)}")
            raise

    async def generate_podcast(
        self,
        podcast_id: str,
        topic: Optional[str] = None,
        url: Optional[str] = None,
        language: str = "ko",
        tts_engine: str = "elevenlabs",
        num_speakers: int = 2,
        custom_voices: Optional[Dict[str, str]] = None,
        turns: int = 8,
        style: str = "casual"
    ) -> dict:
        """다중 화자 대화형 팟캐스트 자동 생성

        LLM이 자동으로 2~3명의 진행자가 대화하는 스크립트를 생성하고,
        각 화자에게 자동으로 적절한 음성을 할당하여 팟캐스트를 생성합니다.

        Args:
            podcast_id: 팟캐스트 ID
            topic: 주제 (topic 또는 url 중 하나 필수)
            url: URL (topic 또는 url 중 하나 필수)
            language: 언어 (ko, en)
            tts_engine: TTS 엔진
            num_speakers: 화자 수 (2 또는 3, 기본값: 2)
            custom_voices: 사용자 정의 화자 매핑 (예: {"화자A": "rachel", "화자B": "adam"})
            turns: 대화 턴 수 (기본값: 8, 약 1분)
        """
        try:
            output_dir = Path(f"output/{podcast_id}")
            output_dir.mkdir(parents=True, exist_ok=True)

            # 팟캐스트 생성을 위한 컨텐츠 준비
            content_for_script = ""

            # URL 기반 팟캐스트 생성
            if url:
                self._update_status(podcast_id, "URL 콘텐츠 파싱 중...", 5)
                logger.info(f"URL 기반 팟캐스트 생성 - URL: {url}")

                try:
                    # 1. HTML에서 텍스트 추출
                    raw_text = parse_url_to_text(url)
                    logger.info(f"URL 텍스트 추출 완료: {len(raw_text)} 문자")

                    # 2. OpenAI로 핵심 내용 추출
                    self._update_status(podcast_id, "핵심 내용 추출 중...", 7)
                    key_content = await self.llm_client.extract_key_content(raw_text)
                    logger.info(f"핵심 내용 추출 완료: {len(key_content)} 문자")

                    # 추출된 내용을 파일로 저장
                    content_path = output_dir / "url_content.txt"
                    with open(content_path, 'w', encoding='utf-8') as f:
                        f.write(f"URL: {url}\n\n")
                        f.write("=== 추출된 핵심 내용 ===\n\n")
                        f.write(key_content)

                    # URL 내용을 스크립트 생성에 사용
                    content_for_script = key_content

                except Exception as e:
                    logger.error(f"URL 파싱 실패: {str(e)}")
                    raise ValueError(f"URL에서 내용을 추출할 수 없습니다: {str(e)}")

            # 주제 기반 팟캐스트 생성
            elif topic:
                logger.info(f"주제 기반 팟캐스트 생성 - 주제: {topic}")
                content_for_script = topic

            else:
                raise ValueError("topic 또는 url 중 하나는 필수입니다.")

            self._update_status(podcast_id, "대화 스크립트 생성 중...", 10)
            logger.info(f"팟캐스트 생성 시작: {podcast_id} - 컨텐츠: {content_for_script[:100]}..., 화자 수: {num_speakers}, 턴 수: {turns}")

            # LLM이 대화형 스크립트 생성 (화자A, 화자B, 화자C 형식)
            script = await self.llm_client.generate_podcast_script(
                topic=content_for_script,
                language=language,
                num_speakers=num_speakers,
                turns=turns,
                style=style
            )

            script_path = output_dir / "script.txt"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)

            self._update_status(podcast_id, "제목 생성 중...", 25)
            title = await self.llm_client.generate_title(script)

            title_path = output_dir / "title.txt"
            with open(title_path, 'w', encoding='utf-8') as f:
                f.write(title)

            # 스크립트 파싱: "화자A: 대사" → [{"speaker": "rachel", "text": "대사"}]
            self._update_status(podcast_id, "대화 스크립트 파싱 중...", 35)
            dialogue_list = self._parse_dialogue_script(script, num_speakers, custom_voices)

            logger.info(f"총 {len(dialogue_list)}개의 대사로 구성된 대화형 팟캐스트 생성")

            # 다중 화자 대화형 오디오 생성
            self._update_status(podcast_id, f"다중 화자 오디오 생성 중... (대사 {len(dialogue_list)}개)", 45)
            audio_path = output_dir / "podcast.mp3"

            audio_file, dialogue_metadata = await self.tts_engine.generate_dialogue_podcast(
                dialogue_script=dialogue_list,
                language=language,
                tts_engine=tts_engine,
                output_path=str(audio_path)
            )

            # 타임스탬프 메타데이터 저장
            metadata_path = output_dir / "dialogue_metadata.json"
            import json
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "podcast_id": podcast_id,
                    "total_duration": dialogue_metadata[-1]["end_time"] if dialogue_metadata else 0,
                    "dialogue_count": len(dialogue_metadata),
                    "dialogues": dialogue_metadata
                }, f, ensure_ascii=False, indent=2)

            self._update_status(podcast_id, "오디오 후처리 중...", 85)
            enhanced_path = output_dir / "podcast_enhanced.mp3"
            self.tts_engine.enhance_audio(str(audio_path), str(enhanced_path))

            if enhanced_path.exists():
                audio_path.unlink()
                enhanced_path.rename(audio_path)

            self._update_status(podcast_id, "완료", 100)

            logger.info(f"다중 화자 팟캐스트 생성 완료: {podcast_id}")

            return {
                "podcast_id": podcast_id,
                "status": "completed",
                "script_path": str(script_path),
                "audio_path": str(audio_path),
                "title": title,
                "dialogue_count": len(dialogue_list),
                "speakers_used": list(set(d["speaker"] for d in dialogue_list))
            }

        except Exception as e:
            self._update_status(podcast_id, f"오류: {str(e)}")
            logger.error(f"팟캐스트 생성 실패: {podcast_id} - {str(e)}")
            raise

    def _update_status(self, podcast_id: str, status: str, progress: int = 0):
        import json
        import time

        status_path = Path(f"output/{podcast_id}/status.txt")
        status_path.parent.mkdir(parents=True, exist_ok=True)

        status_data = {
            "status": "processing" if status != "완료" and not status.startswith("오류") else ("completed" if status == "완료" else "failed"),
            "message": status,
            "progress": progress,
            "updated_at": time.time()
        }

        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)

    def get_podcast_info(self, podcast_id: str) -> dict:
        output_dir = Path(f"output/{podcast_id}")

        if not output_dir.exists():
            return {"error": "팟캐스트를 찾을 수 없습니다."}

        info = {
            "podcast_id": podcast_id,
            "files": {}
        }

        status_path = output_dir / "status.txt"
        if status_path.exists():
            with open(status_path, 'r', encoding='utf-8') as f:
                info["status"] = f.read().strip()

        script_path = output_dir / "script.txt"
        if script_path.exists():
            info["files"]["script"] = str(script_path)

        audio_path = output_dir / "podcast.mp3"
        if audio_path.exists():
            info["files"]["audio"] = str(audio_path)
            info["files"]["audio_size"] = audio_path.stat().st_size

        title_path = output_dir / "title.txt"
        if title_path.exists():
            with open(title_path, 'r', encoding='utf-8') as f:
                info["title"] = f.read().strip()

        return info

    def list_podcasts(self) -> list:
        output_dir = Path("output")
        podcasts = []

        if not output_dir.exists():
            return podcasts

        for podcast_dir in output_dir.iterdir():
            if podcast_dir.is_dir():
                podcast_info = self.get_podcast_info(podcast_dir.name)
                if "error" not in podcast_info:
                    podcast_info["created_at"] = podcast_dir.stat().st_ctime
                    podcasts.append(podcast_info)

        return sorted(podcasts, key=lambda x: x.get("created_at", 0), reverse=True)

    def delete_podcast(self, podcast_id: str) -> bool:
        import shutil

        output_dir = Path(f"output/{podcast_id}")

        if not output_dir.exists():
            return False

        try:
            shutil.rmtree(output_dir)
            return True
        except Exception as e:
            logger.error(f"팟캐스트 삭제 실패: {podcast_id} - {str(e)}")
            return False
