"""
22PM AI Engine — Unified LLM Client
======================================
Abstracts Groq and Gemini APIs behind a single interface.
Auto-fallback: tries primary provider, falls back to secondary.

Usage:
    llm = LLMClient()
    response = await llm.generate("Write an email...")
"""

import time
import asyncio
import logging
from typing import Optional, AsyncIterator
from dataclasses import dataclass

from config import settings

logger = logging.getLogger("22pm.llm")


@dataclass
class LLMResponse:
    """Standard response from any LLM provider."""
    text: str
    provider: str
    model: str
    latency_ms: int
    tokens_used: int = 0
    error: Optional[str] = None


class RateLimiter:
    """Simple token-bucket rate limiter for free tier compliance."""

    def __init__(self, rpm: int):
        self.max_requests = rpm
        self.tokens = rpm
        self.last_refill = time.monotonic()
        self.refill_interval = 60.0 / rpm

    async def acquire(self):
        """Wait for a token if needed."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_requests, self.tokens + elapsed * self.max_requests / 60.0)
        self.last_refill = now

        if self.tokens < 1:
            wait = self.refill_interval
            logger.debug(f"Rate limited, waiting {wait:.2f}s")
            await asyncio.sleep(wait)
            self.tokens = 0
        else:
            self.tokens -= 1


class GeminiProvider:
    """Google Gemini API — 60 requests/minute free."""

    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.rate_limiter = RateLimiter(settings.GEMINI_RATE_LIMIT_RPM)
        self.provider_name = "gemini"
        self.model_name = settings.GEMINI_MODEL

    async def generate(self, prompt: str, system_prompt: str = "",
                       temperature: float = 0.7, max_tokens: int = 2048) -> LLMResponse:
        """Generate text using Gemini."""
        await self.rate_limiter.acquire()
        start = time.monotonic()

        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    }
                )
            )
            latency = int((time.monotonic() - start) * 1000)
            return LLMResponse(
                text=response.text,
                provider=self.provider_name,
                model=self.model_name,
                latency_ms=latency,
                tokens_used=getattr(response, 'usage_metadata', {}).get('total_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            )
        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            logger.error(f"Gemini error: {e}")
            return LLMResponse(
                text="", provider=self.provider_name, model=self.model_name,
                latency_ms=latency, error=str(e)
            )


class GroqProvider:
    """Groq API — 30 requests/minute, 6000 tokens/min free."""

    def __init__(self):
        from groq import Groq, AsyncGroq
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.async_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.rate_limiter = RateLimiter(settings.GROQ_RATE_LIMIT_RPM)
        self.provider_name = "groq"
        self.model_name = settings.GROQ_MODEL

    async def generate(self, prompt: str, system_prompt: str = "",
                       temperature: float = 0.7, max_tokens: int = 2048) -> LLMResponse:
        """Generate text using Groq."""
        await self.rate_limiter.acquire()
        start = time.monotonic()

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            latency = int((time.monotonic() - start) * 1000)
            return LLMResponse(
                text=response.choices[0].message.content,
                provider=self.provider_name,
                model=self.model_name,
                latency_ms=latency,
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            logger.error(f"Groq error: {e}")
            return LLMResponse(
                text="", provider=self.provider_name, model=self.model_name,
                latency_ms=latency, error=str(e)
            )


class LLMClient:
    """
    Unified LLM Client with auto-fallback.
    Primary: Gemini (60 req/min free, generous limits).
    Fallback: Groq (30 req/min free, faster inference).
    """

    def __init__(self):
        self.primary: Optional[GeminiProvider] = None
        self.fallback: Optional[GroqProvider] = None
        self._init_providers()

    def _init_providers(self):
        """Initialize available providers."""
        if settings.GEMINI_API_KEY:
            try:
                self.primary = GeminiProvider()
                logger.info("Gemini provider initialized")
            except Exception as e:
                logger.warning(f"Failed to init Gemini: {e}")

        if settings.GROQ_API_KEY:
            try:
                self.fallback = GroqProvider()
                logger.info("Groq provider initialized")
            except Exception as e:
                logger.warning(f"Failed to init Groq: {e}")

        if not self.primary and not self.fallback:
            logger.warning("No LLM providers configured. Set GEMINI_API_KEY or GROQ_API_KEY.")

    async def generate(self, prompt: str, system_prompt: str = "",
                       temperature: float = 0.7, max_tokens: int = 2048,
                       prefer: str = "auto") -> LLMResponse:
        """
        Generate text with automatic provider selection.
        
        Args:
            prompt: The user prompt
            system_prompt: System instructions
            temperature: 0.0-1.0
            max_tokens: Max response tokens
            prefer: "gemini", "groq", or "auto" (tries primary, falls back)
        
        Returns:
            LLMResponse with text and metadata
        """
        providers = []
        if prefer == "gemini" and self.primary:
            providers = [self.primary, self.fallback]
        elif prefer == "groq" and self.fallback:
            providers = [self.fallback, self.primary]
        else:
            providers = [self.primary, self.fallback]

        errors = []
        for provider in providers:
            if provider is None:
                continue
            result = await provider.generate(prompt, system_prompt, temperature, max_tokens)
            if result.error:
                errors.append(result.error)
                logger.warning(f"{provider.provider_name} failed, trying fallback...")
                continue
            return result

        error_msg = "; ".join(errors) if errors else "No LLM providers configured"
        return LLMResponse(text="", provider="none", model="none",
                           latency_ms=0, error=error_msg)

    async def generate_json(self, prompt: str, system_prompt: str = "",
                            prefer: str = "auto") -> dict:
        """Generate a JSON response. Provider must support JSON mode."""
        json_system = system_prompt + "\n\nRespond ONLY with valid JSON. No markdown."
        result = await self.generate(prompt, json_system, temperature=0.3, prefer="groq")
        
        if result.error:
            return {"error": result.error}
        
        import json
        try:
            # Try to parse JSON from response
            text = result.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"raw": result.text, "error": "Failed to parse JSON"}


# Global LLM client instance
llm = LLMClient()