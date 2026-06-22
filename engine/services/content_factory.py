"""
22PM — Content Factory Service
================================
Takes 1 piece of content and generates 10+ platform-specific posts.
Powered by the unified LLM client.

API Endpoints:
    POST /api/content/generate      — Generate posts for all platforms
    POST /api/content/generate-one  — Generate for a single platform
    POST /api/content/repurpose     — Repurpose video/blog URL
"""

import logging
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from llm import llm

logger = logging.getLogger("22pm.content_factory")


# ===== Models =====

class ContentRequest(BaseModel):
    source_text: str = Field(..., min_length=50, description="Source blog/video content")
    brand_voice: str = ""
    platforms: list[str] = Field(
        default=["linkedin", "instagram", "twitter", "tiktok", "quote_card"],
        description="Target platforms"
    )

class SinglePlatformRequest(BaseModel):
    source_text: str = Field(..., min_length=50)
    platform: str = Field(..., pattern="^(linkedin|instagram|twitter|tiktok|quote_card)$")
    brand_voice: str = ""

class ContentResponse(BaseModel):
    platform: str
    content: str
    platform_specific: dict = {}

class BatchContentResponse(BaseModel):
    results: list[ContentResponse]
    source_word_count: int
    total_posts_generated: int
    provider_used: str
    cost: str = "$0 (free tier)"


# ===== Platform Prompts =====

PLATFORM_PROMPTS = {
    "linkedin": """
Write a LinkedIn post from this content.

STRUCTURE:
- Opening: Question or personal story (2-3 sentences)
- Body: 4 key insights as bullet points
- Closing: Discussion question + soft CTA
- Hashtags: 5 relevant ones

TONE: Professional thought leadership. First-person perspective.
""",
    "instagram": """
Create an Instagram carousel + caption from this content.

CAROUSEL (5 slides):
1. Hook + bold statement
2. Key insight #1
3. Key insight #2
4. Key insight #3
5. CTA

CAPTION: 3-4 sentences with 10 hashtags.

TONE: Inspirational + educational. Moderate emoji use.
""",
    "twitter": """
Create a 5-tweet thread from this content.

Tweet 1: Hook (max 200 chars)
Tweet 2: Key insight (max 240 chars)
Tweet 3: Key insight (max 240 chars)
Tweet 4: Key insight (max 240 chars)
Tweet 5: CTA + link (max 240 chars)

TONE: Conversational, direct. Use line breaks between tweets.
""",
    "tiktok": """
Write a 60-second TikTok script.

STRUCTURE:
- 0-3s: Hook (grab attention immediately)
- 3-30s: 3 quick facts presented fast
- 30-45s: Demonstration or example
- 45-60s: CTA ("Follow for more [topic] tips")

TONE: Energetic, conversational, Gen Z-friendly. Use casual language.
""",
    "quote_card": """
Extract 5 quotable sentences from this content.

Each quote must:
- Stand alone as powerful and shareable
- Be under 280 characters
- Have high potential for engagement
- Include attribution context

Format as: "Quote text" — Context
"""
}

SYSTEM_PROMPT = """You are an expert content repurposing specialist. Take long-form 
content and transform it into platform-optimized social media posts. Maintain the 
original tone and key messages while optimizing for each platform's format. 
Be specific and actionable."""

CHUNK_SYSTEM_PROMPT = """Analyze this content and extract the key elements needed 
for repurposing. Respond with a structured analysis."""

CHUNK_PROMPT_TEMPLATE = """
Analyze this content and extract:

1. Main topic and angle
2. 5 key takeaways or statistics
3. 3 quotable sentences
4. Target audience
5. Emotional hooks or themes

Content:
{text}
"""


# ===== Service =====

class ContentFactoryService:
    """AI-powered content repurposing engine."""

    async def chunk_content(self, text: str) -> str:
        """Extract key elements from source content."""
        prompt = CHUNK_PROMPT_TEMPLATE.format(text=text[:8000])
        result = await llm.generate(prompt, CHUNK_SYSTEM_PROMPT, temperature=0.3)
        return result.text

    async def generate_platform_post(self, text: str, platform: str,
                                     brand_voice: str = "") -> str:
        """Generate a post for a single platform."""
        platform_prompt = PLATFORM_PROMPTS.get(platform, PLATFORM_PROMPTS["linkedin"])
        
        full_prompt = f"""
SOURCE CONTENT:
{text[:7000]}

BRAND VOICE:
{brand_voice or 'Default professional tone'}

PLATFORM: {platform.upper()}

{platform_prompt}

Generate the post now:
"""
        result = await llm.generate(full_prompt, SYSTEM_PROMPT, temperature=0.7, max_tokens=1500)
        return result.text

    async def generate_all(self, request: ContentRequest) -> BatchContentResponse:
        """Generate posts for all requested platforms."""
        # Step 1: Chunk/analyze the source
        chunk = await self.chunk_content(request.source_text)
        
        # Step 2: Generate for each platform
        results = []
        for platform in request.platforms:
            try:
                post = await self.generate_platform_post(
                    chunk + "\n\n---\n\n" + request.source_text,
                    platform,
                    request.brand_voice
                )
                results.append(ContentResponse(
                    platform=platform,
                    content=post
                ))
                logger.info(f"✓ Generated {platform} post")
            except Exception as e:
                logger.error(f"✗ Failed {platform}: {e}")
                results.append(ContentResponse(
                    platform=platform,
                    content=f"Generation failed: {e}",
                    platform_specific={"error": str(e)}
                ))
        
        return BatchContentResponse(
            results=results,
            source_word_count=len(request.source_text.split()),
            total_posts_generated=len(results),
            provider_used="gemini/groq (auto-fallback)"
        )

    async def generate_single(self, request: SinglePlatformRequest) -> ContentResponse:
        """Generate a post for a single platform."""
        post = await self.generate_platform_post(
            request.source_text, request.platform, request.brand_voice
        )
        return ContentResponse(platform=request.platform, content=post)

    @staticmethod
    def format_content_calendar(results: list[ContentResponse]) -> str:
        """Generate a content calendar from results."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        calendar = "# 22PM Content Calendar\n\n"
        calendar += "| Day | Platform |\n|-----|----------|\n"
        
        for i, result in enumerate(results):
            if i < len(days):
                calendar += f"| {days[i]} | {result.platform.title()} |\n"
        
        calendar += "\n\n---\nGenerated by 22PM Content Factory — $0 per run"
        return calendar