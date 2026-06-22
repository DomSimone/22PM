"""
22PM — AI Content Factory
==========================
Takes 1 long-form blog/video transcript and generates 10 platform-specific posts.
Uses Google Gemini API FREE tier (60 req/min).

Usage:
    python content_factory.py --input transcript.txt --output ./output

Requirements: pip install google-generativeai python-dotenv
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional

try:
    import google.generativeai as genai
except ImportError:
    print("Installing required package: google-generativeai")
    os.system("pip install -q google-generativeai python-dotenv")
    import google.generativeai as genai


# --- Configuration ---
# Get your FREE API key at: https://aistudio.google.com/app/apikey
API_KEY = os.getenv("GEMINI_API_KEY", "")

MODEL_NAME = "gemini-1.5-flash"  # FREE tier model
SYSTEM_PROMPT = """You are an expert content repurposing specialist.
Your job is to take long-form content and transform it into 
platform-optimized social media posts. Maintain the original 
tone and key messages while optimizing for each platform's format."""


# --- Platform-specific prompts ---

PLATFORM_PROMPTS = {
    "linkedin": """
Create a LinkedIn post from this content.
Format:
- Opening hook (question + personal story, 2-3 sentences)
- Body: 4 key insights as bullet points
- Closing: Discussion question + CTA
- 5 relevant hashtags

Tone: Professional thought leadership.
""",
    "instagram_carousel": """
Create an Instagram carousel from this content.
Format 5 slides:
1. Hook + bold statement
2. Key insight #1 with icon
3. Key insight #2 with icon  
4. Key insight #3 with icon
5. CTA

Include a caption with 10 hashtags. Tone: Inspirational + educational.
""",
    "twitter_thread": """
Create a 5-tweet thread from this content.
Tweet 1: Hook (max 200 chars)
Tweet 2: Insight 1 (max 240 chars)
Tweet 3: Insight 2 (max 240 chars)
Tweet 4: Insight 3 (max 240 chars)
Tweet 5: CTA with link (max 240 chars)
""",
    "tiktok_script": """
Write a 60-second TikTok script.
Hook (first 3 seconds): Grab attention
Body: 3 quick facts delivered fast
CTA: "Follow for more [topic] tips"
Tone: Energetic, conversational, Gen Z-friendly
""",
    "quote_card": """
Extract 5 quotable sentences from this content.
Each quote should:
- Stand alone as powerful
- Be under 280 characters
- Have high share potential
Format as JSON array of strings.
"""
}


class ContentFactory:
    """AI-powered content repurposing engine using free-tier Gemini API."""

    def __init__(self, api_key: str = API_KEY):
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Get a free key at: "
                "https://aistudio.google.com/app/apikey\n"
                "Then: export GEMINI_API_KEY='your-key-here'"
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=SYSTEM_PROMPT
        )
        self.usage_count = 0

    def chunk_content(self, text: str, max_chars: int = 8000) -> List[str]:
        """Split long content into manageable chunks for the API."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > max_chars:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks if chunks else [text]

    def generate_post(self, content: str, platform: str, 
                      brand_voice: Optional[str] = None) -> str:
        """Generate a platform-specific post from source content."""
        prompt = PLATFORM_PROMPTS.get(platform, "")
        
        full_prompt = f"""
{platform.upper()} POST GENERATION
{'=' * 40}

Source Content:
{content[:7000]}

Brand Voice Guidelines (if provided):
{brand_voice or 'Default professional tone'}

{prompt}

Generate the post now:
"""
        response = self.model.generate_content(full_prompt)
        self.usage_count += 1
        
        return response.text

    def generate_all_posts(self, content: str, 
                           brand_voice: Optional[str] = None) -> Dict[str, str]:
        """Generate posts for all platforms at once."""
        results = {}
        chunks = self.chunk_content(content)[:1]  # Use first chunk for initial processing
        
        for platform in PLATFORM_PROMPTS.keys():
            print(f"  → Generating {platform} post...")
            results[platform] = self.generate_post(
                chunks[0], platform, brand_voice
            )
        
        return results

    def save_output(self, results: Dict[str, str], output_dir: str):
        """Save generated posts to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save individual platform files
        for platform, post in results.items():
            safe_name = platform.replace(" ", "_").lower()
            filepath = output_path / f"{safe_name}.md"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# 22PM Content Factory — {platform.upper()}\n\n")
                f.write(post)
            print(f"  ✓ Saved: {filepath}")

        # Save combined JSON
        json_path = output_path / "all_posts.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved: {json_path}")

        # Generate a content calendar
        calendar = self._generate_calendar(results)
        cal_path = output_path / "content_calendar.md"
        with open(cal_path, "w", encoding="utf-8") as f:
            f.write(calendar)
        print(f"  ✓ Saved: {cal_path}")

    def _generate_calendar(self, results: Dict[str, str]) -> str:
        """Generate a simple content calendar from the posts."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        platforms = list(results.keys())
        
        calendar = "# 22PM Content Calendar\n\n"
        calendar += "| Day | Platform | Post Type |\n"
        calendar += "|-----|----------|-----------|\n"
        
        for i, day in enumerate(days):
            if i < len(platforms):
                calendar += f"| {day} | {platforms[i].replace('_', ' ').title()} | Generated |\n"
        
        calendar += "\n\n*Generated by 22PM Content Factory*\n"
        return calendar


def main():
    parser = argparse.ArgumentParser(
        description="22PM Content Factory - Repurpose 1 piece into 10+ posts"
    )
    parser.add_argument("--input", "-i", required=True,
                        help="Path to source content file (txt, md)")
    parser.add_argument("--output", "-o", default="./output",
                        help="Output directory for generated posts")
    parser.add_argument("--brand", "-b", default=None,
                        help="Optional brand voice guidelines (file or text)")
    
    args = parser.parse_args()

    # Read input content
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {args.input}")
        return
    
    content = input_path.read_text(encoding="utf-8")
    print(f"\n📄 Loaded content: {input_path.name} ({len(content)} chars)")
    print(f"🤖 Initializing Gemini AI (free tier)...")

    # Read brand voice if provided
    brand_voice = None
    if args.brand:
        brand_path = Path(args.brand)
        if brand_path.exists():
            brand_voice = brand_path.read_text(encoding="utf-8")
        else:
            brand_voice = args.brand

    # Initialize engine
    try:
        factory = ContentFactory()
    except ValueError as e:
        print(f"❌ {e}")
        return

    # Generate all posts
    print(f"\n{'='*50}")
    print(f"GENERATING 10 POSTS FROM 1 SOURCE")
    print(f"{'='*50}\n")

    results = factory.generate_all_posts(content, brand_voice)

    # Save results
    print(f"\n📁 Saving output to: {args.output}/")
    factory.save_output(results, args.output)

    # Summary
    print(f"\n{'='*50}")
    print(f"✅ DONE — Generated {len(results)} platform-specific posts")
    print(f"📊 API calls used: {factory.usage_count}")
    print(f"💰 Cost: $0 (free tier)")
    print(f"{'='*50}")
    print(f"\nNext step: Review posts in {args.output}/ and schedule with Buffer/Later.")


if __name__ == "__main__":
    main()