# 22PM — AI Content Factory Workflow

## Overview
Takes 1 long-form video/blog and automatically spins out 10 platform-specific social posts, captions, and graphics — using only free-tier AI tools.

## Architecture

```
[YouTube Video / Blog Article / Podcast]
            ↓
    [YouTube Transcript API / Paste Text]
            ↓
    [Google Gemini API FREE - Content Chunking]
            ↓
    [Make.com FREE Scenario - Multi-Format Generation]
            ↓
    [Canva FREE - Auto-Design via API]
            ↓
    [Buffer FREE / Later FREE - Social Scheduling]
            ↓
    [Instagram / LinkedIn / Twitter / TikTok]
```

## Free-Tier Tools Required

| Tool             | Free Tier Limit                    | Purpose                          |
|------------------|------------------------------------|----------------------------------|
| Google Gemini API | 60 req/min FREE                    | Content repurposing engine       |
| Canva            | Free (250k+ templates)             | Auto-generate graphics           |
| Buffer           | Free (3 channels, 10 posts/channel)| Social media scheduling          |
| Make.com         | 2 active scenarios, 1k ops/month   | Orchestration                    |
| YouTube API      | 10k units/day FREE                 | Fetch transcripts                |
| Claude Free      | Limited messages                   | Refinement & editing             |

## Step-by-Step Build (No-Code / Low-Code)

### Step 1: Fetch Source Content
**Option A — YouTube Video:**
- Use [YouTube Transcript API](https://console.cloud.google.com/apis/library/youtube.googleapis.com) (free tier)
- Fetch auto-captions/subtitles
- Send transcript to Make.com webhook

**Option B — Blog/Article:**
- Use a free scraping tool or simply paste the URL
- Extract main content via [Outline.com](https://outline.com) or [Reader Mode](https://reader.mozilla.org)

### Step 2: Content Processing Pipeline (Make.com)

1. **Create scenario:** "22PM Content Factory"
2. **Trigger:** Webhook receiving source content
3. **Content Chunk Module (Gemini API):**
```
PROMPT:
Analyze this content and identify:
1. Main topic & angle
2. 5 key takeaways / statistics
3. 3 quotable sentences
4. Target audience
5. Emotional hooks

Content: {{source_text}}
```
4. **Splitter Module:** Break into 10 platform-specific formats

### Step 3: Generate Platform-Specific Posts

**Instagram (Carousel + Caption):**
```
PROMPT:
Create an Instagram carousel post from this content:
- Slide 1: Hook + bold statement
- Slide 2-4: Key insights (1 per slide)
- Slide 5: CTA
Generate caption with 10 relevant hashtags.
Emoji usage: moderate. Tone: inspirational + educational.
Content: {{chunk}}
```

**LinkedIn (Long-form Post):**
```
PROMPT:
Write a LinkedIn post using this content:
- Opening: Personal story or question (2-3 sentences)
- Body: 4 bullet points of key insights
- Closing: Discussion question + CTA
- Add 5 relevant hashtags
Tone: professional thought leadership.
Content: {{chunk}}
```

**Twitter/X (Thread):**
```
PROMPT:
Create a 5-tweet thread from this content:
Tweet 1: Hook (max 200 chars)
Tweet 2-4: Key insights (max 240 chars each)
Tweet 5: CTA + link to original content
Content: {{chunk}}
```

**TikTok (Script):**
```
PROMPT:
Write a 60-second TikTok script:
- Hook (first 3 seconds)
- Body: 3 quick facts
- CTA: "Follow for more"
Tone: Energetic, conversational.
Content: {{chunk}}
```

### Step 4: Auto-Design Graphics (Canva API)

1. Connect Canva to Make.com via API
2. Use Canva template: "Social Media Post" (free)
3. Map fields:
   - Title → Key takeaway from content
   - Body → Quote or statistic
   - Brand color → Client's brand color
4. Export as PNG/JPG
5. Send to Buffer for scheduling

### Step 5: Schedule (Buffer FREE)

1. Create Buffer account (free tier: 3 channels)
2. Connect Instagram, LinkedIn, Twitter
3. Buffer API receives from Make.com:
```json
{
  "text": "{{generated_caption}}",
  "media": ["{{canva_image_url}}"],
  "scheduled_at": "{{optimized_time}}"
}
```

## Full Prompt Library (Copy-Paste)

### Headline Generator
```
Generate 10 headline variations for this content:
- 3 curiosity-gap headlines
- 3 how-to headlines
- 2 listicle headlines
- 2 controversial headlines
Content: {{source_content}}
```

### Hashtag Research
```
Generate 20 hashtags for this content category:
- 5 broad (500k+ posts)
- 5 medium (100k-500k posts)
- 5 niche (10k-100k posts)
- 5 trending this week
Category: {{topic}}
```

### Repurpose Short Form
```
From this 10-minute video transcript, extract:
- 3 Reel hooks (15 words each)
- 2 quote cards (1 sentence each)
- 3 "Did you know?" text overlays
Transcript: {{transcript}}
```

## Deliverable to Client

**What the client receives:**
- ✅ 10 platform-specific posts from 1 source piece
- ✅ Auto-designed graphics per post
- ✅ Scheduled 2 weeks out on Buffer
- ✅ Caption + hashtag sets per platform
- ✅ 7-day trial: If not 10x content output, they owe nothing

## Outsourcing Spec for Scale

Post on Upwork/Fiverr:
> **"Build a Make.com → Gemini API → Canva API → Buffer automation. Takes 1 YouTube URL, generates 10 social posts with graphics, and schedules them. Must use free tiers only. Budget $500."**

## Content Calendar Template

| Day | Platform  | Post Type    | Source Content        |
|-----|-----------|--------------|-----------------------|
| Mon | LinkedIn  | Long-form    | Blog article #1       |
| Tue | Instagram | Carousel     | Blog article #1       |
| Wed | Twitter   | Thread       | Blog article #1       |
| Thu | TikTok    | Script       | Blog article #1       |
| Fri | LinkedIn  | Short tip    | Blog article #2       |
| Sat | Instagram | Reel hook    | Blog article #2       |

## Metrics

| Metric                  | Target          |
|-------------------------|-----------------|
| Posts generated/week    | 10              |
| Hours saved/week        | 15+             |
| Avg engagement rate     | >3%             |
| Time to first post      | <2 hours setup  |