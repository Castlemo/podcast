from openai import AsyncOpenAI
from src.utils.config import Settings

class OpenAIClient:
    def __init__(self):
        self.settings = Settings()
        self.client = AsyncOpenAI(
            api_key=self.settings.openai_api_key
        )

    async def generate_podcast_script(
        self,
        topic: str,
        language: str = "ko",
        num_speakers: int = 2,
        turns: int = 8,
        style: str = "casual"
    ) -> str:

        # 언어별, 스타일별 가이드라인
        if language == "ko":
            style_guidelines = {
                "casual": """
스타일: 친근하고 편안한 대화
- 친구들끼리 이야기하듯 자연스럽고 가벼운 톤
- 농담, 감탄사, 공감 표현을 자주 사용
- "진짜?", "대박!", "그렇구나!" 같은 자연스러운 반응
- 전문 용어보다는 쉬운 표현 사용""",
                "professional": """
스타일: 전문적이고 신뢰감 있는 대화
- 정중하고 체계적인 어조
- 정확한 정보 전달에 초점
- 전문 용어 사용 시 간단한 설명 추가
- 논리적인 흐름으로 주제를 깊이 있게 다룸""",
                "educational": """
스타일: 교육적이고 설명 중심의 대화
- 복잡한 개념을 쉽게 풀어서 설명
- 예시와 비유를 적극 활용
- 청취자가 배울 수 있도록 단계적으로 설명
- "예를 들면...", "쉽게 말하면..." 같은 표현 사용
- 배경 지식이 없어도 이해할 수 있도록 친절하게 설명""",
                "storytelling": """
스타일: 이야기를 들려주듯 흥미진진한 대화
- 극적이고 생동감 있는 표현
- 장면 묘사와 감정 표현이 풍부
- 호기심을 유발하는 질문과 반전
- 이야기의 기승전결 구조 활용"""
            }
        else:  # English
            style_guidelines = {
                "casual": """
Style: Friendly and relaxed conversation
- Natural and light tone, like talking with friends
- Use humor, exclamations, and empathetic expressions
- Natural reactions like "Really?", "Wow!", "I see!"
- Use simple expressions over technical jargon""",
                "professional": """
Style: Professional and credible conversation
- Polite and systematic tone
- Focus on accurate information delivery
- Brief explanations when using technical terms
- Deep dive into topics with logical flow""",
                "educational": """
Style: Educational and explanatory conversation
- Break down complex concepts into simple terms
- Use examples and analogies actively
- Explain step-by-step for listener understanding
- Use phrases like "For example...", "In simple terms..."
- Explain kindly so anyone can understand without background knowledge""",
                "storytelling": """
Style: Engaging and narrative conversation
- Dramatic and vivid expressions
- Rich in scene descriptions and emotional expressions
- Questions and twists that spark curiosity
- Use narrative structure with introduction, development, climax, and conclusion"""
            }

        style_guide = style_guidelines.get(style, style_guidelines["casual"])

        # 화자 수에 따른 프롬프트 조정
        turns_per_speaker = turns // num_speakers

        if language == "ko":
            if num_speakers == 2:
                speaker_info = f"""
조건:
1. 2명의 진행자가 등장하며, 서로 농담도 하고, 질문/답변을 오가면서 실제 녹음 상황처럼 대화할 것
2. 각 화자는 "화자A:", "화자B:" 형식으로 구분 (화자C는 사용하지 않음)
3. **중요**: 정확히 총 {turns}개의 대사로 구성해야 함 (화자A와 화자B가 각각 약 {turns_per_speaker}번씩 발언)
4. 각 대사는 2-3문장으로 짧고 자연스럽게 작성하되, 주제와 관련된 흥미로운 정보와 개인적인 반응이 섞여 있어야 함
5. 문어체가 아닌 구어체 한국어로 작성
6. 대화의 흐름이 청취자가 집중할 수 있도록 오프닝 → 주제 심화 → 정리/마무리로 이어질 것

{style_guide}

예시 형식:
화자A: 안녕하세요, 오늘 팟캐스트 시작해 볼게요.
화자B: 네, 오늘은 제가 기다리던 주제예요. 너무 흥미로워요.
"""
            else:  # 3명
                speaker_info = f"""
조건:
1. 3명의 진행자가 등장하며, 서로 농담도 하고, 질문/답변을 오가면서 실제 녹음 상황처럼 대화할 것
2. 각 화자는 "화자A:", "화자B:", "화자C:" 형식으로 구분
3. **중요**: 정확히 총 {turns}개의 대사로 구성해야 함 (화자A, B, C가 각각 약 {turns_per_speaker}번씩 발언)
4. 각 대사는 2-3문장으로 짧고 자연스럽게 작성하되, 주제와 관련된 흥미로운 정보와 개인적인 반응이 섞여 있어야 함
5. 문어체가 아닌 구어체 한국어로 작성
6. 대화의 흐름이 청취자가 집중할 수 있도록 오프닝 → 주제 심화 → 정리/마무리로 이어질 것

{style_guide}

예시 형식:
화자A: 안녕하세요, 오늘 팟캐스트 시작해 볼게요.
화자B: 네, 오늘은 제가 기다리던 주제예요. 너무 흥미로워요.
화자C: 맞아요, 저도 준비하면서 새롭게 알게 된 게 많더라고요.
"""

            prompt = f"""
당신은 팟캐스트 대본 작가입니다.
아래 조건을 충족하는 **실제 사람들이 나누는 것처럼 자연스러운 대화 대본**을 작성하세요.

주제 설명: {topic}
총 대화 턴 수: {turns}

{speaker_info}
"""
        else:  # English
            if num_speakers == 2:
                speaker_info = f"""
Requirements:
1. 2 hosts having a conversation, joking with each other, asking/answering questions like a real recording situation
2. Each speaker is identified as "Speaker A:", "Speaker B:" format (do NOT use Speaker C)
3. **IMPORTANT**: Must consist of exactly {turns} dialogue turns total (Speaker A and Speaker B each speaking approximately {turns_per_speaker} times)
4. Each dialogue should be 2-3 sentences, short and natural, mixing interesting information about the topic with personal reactions
5. Write in conversational spoken English, not formal written language
6. The conversation flow should keep listeners engaged: Opening → Topic Deep Dive → Summary/Closing

{style_guide}

Example format:
Speaker A: Hello everyone, let's start today's podcast.
Speaker B: Yes, I've been looking forward to this topic. It's so interesting.
"""
            else:  # 3명
                speaker_info = f"""
Requirements:
1. 3 hosts having a conversation, joking with each other, asking/answering questions like a real recording situation
2. Each speaker is identified as "Speaker A:", "Speaker B:", "Speaker C:" format
3. **IMPORTANT**: Must consist of exactly {turns} dialogue turns total (Speaker A, B, and C each speaking approximately {turns_per_speaker} times)
4. Each dialogue should be 2-3 sentences, short and natural, mixing interesting information about the topic with personal reactions
5. Write in conversational spoken English, not formal written language
6. The conversation flow should keep listeners engaged: Opening → Topic Deep Dive → Summary/Closing

{style_guide}

Example format:
Speaker A: Hello everyone, let's start today's podcast.
Speaker B: Yes, I've been looking forward to this topic. It's so interesting.
Speaker C: Right, I learned a lot while preparing for this.
"""

            prompt = f"""
You are a podcast script writer.
Write a **natural conversational script like real people talking** that meets the following requirements.

Topic Description: {topic}
Total Dialogue Turns: {turns}

{speaker_info}
"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )

            script = response.choices[0].message.content or ""

            return script

        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}")

    async def generate_title(self, script: str) -> str:
        system_prompt = """
주어진 팟캐스트 스크립트를 바탕으로 매력적인 제목을 생성해주세요.
제목은 간결하면서도 호기심을 유발해야 합니다.
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": script[:1000]}
                ],
                max_tokens=200,
                temperature=0.8
            )

            content = response.choices[0].message.content
            return content.strip() if content else ""

        except Exception as e:
            raise Exception(f"제목 생성 중 오류가 발생했습니다: {str(e)}")

    async def extract_key_content(self, text: str, max_tokens: int = 1500) -> str:
        """
        웹페이지 텍스트에서 핵심 내용을 추출합니다.

        Args:
            text: 원본 텍스트
            max_tokens: 최대 토큰 수

        Returns:
            추출된 핵심 내용
        """
        # 텍스트가 너무 길면 잘라내기 (약 16000 토큰 = 약 64000자)
        if len(text) > 64000:
            text = text[:64000]

        prompt = f"""다음 웹페이지 내용을 읽고 핵심 내용을 추출해주세요.

요구사항:
1. 주요 주제와 핵심 메시지를 파악하세요
2. 중요한 사실, 데이터, 인용구를 포함하세요
3. 불필요한 광고나 부가 정보는 제외하세요
4. 구조화된 형태로 정리하세요
5. 한국어로 작성하세요

웹페이지 내용:
{text}

핵심 내용:"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "당신은 웹 콘텐츠에서 핵심 정보를 추출하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )

            content = response.choices[0].message.content
            return content.strip() if content else ""

        except Exception as e:
            raise Exception(f"핵심 내용 추출 중 오류가 발생했습니다: {str(e)}")
