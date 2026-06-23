"""
22PM — Lead Nurturing Service
================================
Handles lead scraping, enrichment, personalization, and CRM push.
Powered by the unified LLM client (auto-fallback Gemini → Groq).

API Endpoints:
    POST /api/leads/enrich      — Enrich lead data with AI
    POST /api/leads/outreach    — Generate personalized outreach
    POST /api/leads/bulk        — Bulk process lead list
"""

import csv
import json
import io
import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from llm import llm
from config import settings

logger = logging.getLogger("22pm.lead_nurturing")


# ===== Pydantic Models =====

class Lead(BaseModel):
    email: str = ""
    company: str = ""
    industry: str = ""
    city: str = ""
    website: str = ""
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    pain_points: str = "Manual processes, slow response times"

class OutreachDraft(BaseModel):
    subject_line_1: str = ""
    subject_line_2: str = ""
    email_draft_1: str = ""
    email_draft_2: str = ""
    follow_up_subject: str = ""
    follow_up_body: str = ""

class BatchRequest(BaseModel):
    leads: list[Lead]
    limit_per_day: int = Field(default=30, le=50)

class BatchResponse(BaseModel):
    results: list[dict]
    total_processed: int
    errors: int
    provider_used: str
    cost: str = "$0 (free tier)"


# ===== System Prompts =====

OUTREACH_SYSTEM_PROMPT = """You are a B2B outreach specialist. Generate personalized 
cold email outreach. Be specific to their industry and business type.

Rules:
- Reference their specific business type
- Mention a relevant pain point
- Offer a specific time-saving solution
- Keep tone professional but warm
- No spammy language
- Include a low-friction CTA
- Respond ONLY with valid JSON. No markdown."""

ENRICH_SYSTEM_PROMPT = """You are a lead enrichment specialist. Given limited lead data, 
infer missing fields intelligently based on the company name and available information.
Respond ONLY with valid JSON. No markdown."""


# ===== Prompt Templates =====

OUTREACH_PROMPT_TEMPLATE = """
Generate personalized email outreach for this lead:

LEAD DATA:
- Company: {company}
- Industry: {industry}
- Location: {city}
- Website: {website}
- Pain Points: {pain_points}

Generate a JSON object with:
1. subject_line_1: Curiosity-based subject (max 8 words)
2. subject_line_2: Value-based subject (max 8 words)
3. email_draft_1: Professional outreach (3-4 sentences)
4. email_draft_2: Shorter version (2-3 sentences)
5. follow_up_subject: Subject for 3-day follow-up (max 10 words)
6. follow_up_body: Follow-up email body (2-3 sentences)
"""

ENRICH_PROMPT_TEMPLATE = """
Enrich this lead data with inferred fields:

Input: {lead_json}

Return a JSON with these fields enriched:
- company: {company}
- industry: (infer from company name)
- city: (infer from any available data)
- website: (infer URL if possible)
- pain_points: (generate 3 likely pain points for this type of business)
"""


# ===== Service =====

class LeadNurturingService:
    """AI-powered lead nurturing engine."""

    async def enrich_lead(self, lead: Lead) -> Lead:
        """Enrich a single lead with AI-inferred data."""
        prompt = ENRICH_PROMPT_TEMPLATE.format(
            lead_json=lead.model_dump_json(),
            company=lead.company
        )
        result = await llm.generate_json(prompt, ENRICH_SYSTEM_PROMPT)
        
        if "error" in result:
            logger.warning(f"Enrichment failed for {lead.company}: {result['error']}")
            return lead
        
        # Merge inferred data
        updated = lead.model_copy()
        for field in ["industry", "city", "pain_points"]:
            if result.get(field) and not getattr(lead, field):
                setattr(updated, field, result[field])
        
        return updated

    async def generate_outreach(self, lead: Lead) -> OutreachDraft:
        """Generate personalized outreach for a lead."""
        prompt = OUTREACH_PROMPT_TEMPLATE.format(
            company=lead.company or "Unknown",
            industry=lead.industry or "General Business",
            city=lead.city or "Unknown",
            website=lead.website or "",
            pain_points=lead.pain_points or "Manual processes"
        )
        result = await llm.generate_json(prompt, OUTREACH_SYSTEM_PROMPT)
        
        if "error" in result:
            logger.warning(f"Outreach failed for {lead.company}: {result['error']}")
            return OutreachDraft(
                subject_line_1=f"Quick question for {lead.company}",
                email_draft_1=result.get("raw", "AI generation failed. Please try again.")
            )
        
        return OutreachDraft(**result)

    async def process_batch(self, request: BatchRequest) -> BatchResponse:
        """Process multiple leads with rate limiting."""
        results = []
        errors = 0
        
        for i, lead in enumerate(request.leads[:request.limit_per_day]):
            try:
                # Step 1: Enrich
                enriched = await self.enrich_lead(lead)
                
                # Step 2: Generate outreach
                outreach = await self.generate_outreach(enriched)
                
                results.append({
                    "company": enriched.company,
                    "email": enriched.email,
                    **outreach.model_dump(),
                    "enriched_city": enriched.city,
                    "enriched_industry": enriched.industry,
                    "status": "success"
                })
                logger.info(f"[{i+1}/{min(len(request.leads), request.limit_per_day)}] {enriched.company} ✓")
                
            except Exception as e:
                errors += 1
                results.append({
                    "company": lead.company,
                    "email": lead.email,
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"[{i+1}] {lead.company} ✗ {e}")
        
        return BatchResponse(
            results=results,
            total_processed=len(results),
            errors=errors,
            provider_used="gemini/groq (auto-fallback)",
            cost="$0 (free tier)"
        )

    @staticmethod
    def parse_csv(csv_content: str) -> list[Lead]:
        """Parse CSV string into list of Leads."""
        reader = csv.DictReader(io.StringIO(csv_content))
        leads = []
        for row in reader:
            leads.append(Lead(**{k.lower().replace(" ", "_"): v for k, v in row.items()}))
        return leads

    @staticmethod
    def to_crm_csv(results: list[dict]) -> str:
        """Convert results to HubSpot-ready CSV."""
        output = io.StringIO()
        if not results:
            return "No results"
        
        fieldnames = [
            "email", "company", "first_name", "last_name", "phone",
            "lead_source", "subject_line_1", "email_draft_1",
            "follow_up_body", "outreach_status"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            writer.writerow({
                "email": r.get("email", ""),
                "company": r.get("company", ""),
                "first_name": "",
                "last_name": "",
                "phone": "",
                "lead_source": "22PM Automated Outreach",
                "subject_line_1": r.get("subject_line_1", ""),
                "email_draft_1": r.get("email_draft_1", ""),
                "follow_up_body": r.get("follow_up_body", ""),
                "outreach_status": r.get("status", "Ready to Send")
            })
        
        return output.getvalue()