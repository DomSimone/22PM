# 22PM — Automated Lead Nurturing Workflow

## Overview
Scrapes local leads, drafts hyper-personalized outreach emails using LLMs, and pushes them to a CRM — all on free-tier AI tools.

## Architecture

```
[Google Maps / Yelp / Yellow Pages]
            ↓
    [Apify FREE Tier - Web Scraper]
            ↓
    [Make.com FREE Scenario - Data Processor]
            ↓
    [Groq FREE API / Google Gemini API - Personalization Engine]
            ↓
    [HubSpot FREE CRM / Trello - Pipeline Manager]
            ↓
    [Gmail FREE / SendGrid FREE - Email Dispatch]
```

## Free-Tier Tools Required

| Tool          | Free Tier Limit                     | Purpose                        |
|---------------|-------------------------------------|--------------------------------|
| Apify         | $5 free credits (no CC needed)      | Scrape local business leads    |
| Make.com      | 2 active scenarios, 1k ops/month    | Workflow orchestration          |
| Groq API      | 30 req/min free tier                | Hyper-personalized email drafts |
| Google Gemini API | 60 req/min free tier            | Fallback LLM engine             |
| HubSpot CRM   | Free forever (1,000 contacts)       | Pipeline management             |
| Gmail API     | Free (500 emails/day)               | Email dispatch                  |

## Step-by-Step Build (No-Code / Low-Code)

### Step 1: Scrape Local Leads (Apify)
1. Go to [Apify Store](https://apify.com/store)
2. Use **"Google Maps Scraper"** (free tier included)
3. Input search terms: `"plumber in [city]"`, `"real estate agent [city]"`, etc.
4. Export data: Name, Website, Phone, Email, Rating, Reviews
5. Set up webhook to push data to Make.com

### Step 2: Process & Enrich (Make.com)
1. Create new scenario: **"Webhook → Filter → LLM Enrich"**
2. **Trigger:** Webhook from Apify
3. **Filter:** Remove duplicates by email/phone
4. **LLM Module:** Connect Groq/Gemini API
5. **Prompt template:**
```
You are a B2B outreach specialist. Given this lead data:
- Company: {{company.name}}
- Industry: {{company.industry}}
- Location: {{company.city}}

Generate 3 personalized email subject lines and 2 outreach email drafts that:
1. Reference their specific business type
2. Mention a pain point relevant to their industry
3. Offer a specific time-saving solution
4. Keep tone professional but warm
```
6. **Output format:** JSON with subject_line_1, subject_line_2, draft_1, draft_2

### Step 3: Push to CRM (Make.com → HubSpot)
1. Add HubSpot module to scenario
2. **Action:** Create/Update Contact
3. **Map fields:**
   - Email → Lead email
   - Custom Property "personalized_draft" → LLM output
   - Custom Property "lead_source" → "22PM Automated Outreach"
4. **Pipeline:** Set deal stage to "Cold Outreach"

### Step 4: Send Emails (Make.com → Gmail)
1. Add Gmail module
2. **Action:** Send Email
3. **To:** Lead email
4. **Subject:** LLM-generated subject line
5. **Body:** LLM-generated draft (with tracking pixel)
6. **Schedule:** Send 10 emails/day to avoid spam flags

## Automation Blueprint (Copy-Paste into Make.com)

```json
{
  "scenarioName": "22PM Lead Nurturing Pipeline",
  "triggers": [
    {
      "type": "webhook",
      "source": "apify_scraper",
      "dataFields": ["name", "email", "phone", "website", "city", "rating"]
    }
  ],
  "modules": [
    {
      "type": "filter",
      "condition": "email IS NOT EMPTY AND email NOT IN CRM"
    },
    {
      "type": "llm_prompt",
      "provider": "groq",
      "model": "llama3-70b-8192",
      "prompt": "Generate personalized outreach for {{name}} at {{company}} in {{city}}..."
    },
    {
      "type": "crm_action",
      "provider": "hubspot",
      "action": "create_contact",
      "mappings": {
        "email": "{{email}}",
        "firstname": "{{first_name}}",
        "custom_draft": "{{llm_output}}"
      }
    },
    {
      "type": "email_dispatch",
      "provider": "gmail",
      "send_delay_days": 1,
      "max_per_day": 10
    }
  ]
}
```

## Deliverable to Client

**What the client receives:**
- ✅ Working lead scraping pipeline (10+ leads/day)
- ✅ Personalized email drafts generated per lead
- ✅ CRM populated with enriched lead data
- ✅ Automated email dispatch (10/day to avoid spam)
- ✅ 7-day trial: If not 10x outreach volume, they owe nothing

## Freelancer Outsourcing Spec

When scaling, post on Upwork/Fiverr:
> **"Need to set up a Make.com workflow that connects Apify (Google Maps scraper) → Groq API (personalization) → HubSpot CRM (contact creation) → Gmail (auto-send). Budget $500. Must use only free tiers."**

## Metrics to Track

| Metric              | Target                |
|---------------------|-----------------------|
| Leads scraped/day   | 50+                   |
| Emails sent/day     | 10                    |
| Open rate           | >35%                  |
| Reply rate          | >5%                   |
| Client time saved   | 10+ hours/week        |