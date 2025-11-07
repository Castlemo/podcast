import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
        self.default_voice_type: str = os.getenv("DEFAULT_VOICE_TYPE", "female")
        self.default_language: str = os.getenv("DEFAULT_LANGUAGE", "ko")
        self.default_duration: int = int(os.getenv("DEFAULT_DURATION", "5"))
        self.output_directory: str = os.getenv("OUTPUT_DIRECTORY", "output")
        self.max_script_length: int = int(os.getenv("MAX_SCRIPT_LENGTH", "10000"))

    def validate(self) -> bool:
        """설정 유효성 검사"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        if not self.elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY가 설정되지 않았습니다.")

        output_path = Path(self.output_directory)
        output_path.mkdir(exist_ok=True)

        return True
