"""
22PM — Automated Lead Nurturing Engine
=======================================
Scrapes local leads, generates hyper-personalized outreach, and pushes to CRM.
Uses free-tier Groq API for LLM inference.

Usage:
    python lead_nurturing.py --input leads.csv --output ./outreach --api-key YOUR_GROQ_KEY

Requirements: pip install groq python-dotenv
"""

import os
import json
import csv
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    from groq import Groq
except ImportError:
    print("Installing required package: groq")
    os.system("pip install -q groq python-dotenv")
    from groq import Groq


API_KEY = os.getenv("GROQ_API_KEY", "")
DEFAULT_MODEL = "llama3-70b-8192"  # FREE tier - 30 req/min, 6000 tokens/min


PERSONALIZATION_PROMPT = """You are a B2B outreach specialist. Given lead data below, 
generate personalized email outreach. Be specific to their industry and business type.

LEAD DATA:
- Company: {company}
- Industry: {industry}
- Location: {city}
- Website: {website}
- Pain Points Observed: {pain_points}

Generate a JSON response with:
1. subject_line_1: Curiosity-based subject
2. subject_line_2: Value-based subject
3. email_draft_1: Professional outreach (3-4 sentences)
4. email_draft_2: Shorter version (2-3 sentences)
5. follow_up_subject: Subject for 3-day follow-up
6. follow_up_body: Follow-up email body

Rules:
- Reference their specific business type
- Mention a relevant pain point
- Offer a specific time-saving solution
- Keep tone professional but warm
- No spammy language
- Include a low-friction CTA (reply, call link, etc.)
"""


class LeadNurturingEngine:
    """Lead nurturing automation using free-tier Groq API."""

    def __init__(self, api_key: str = API_KEY):
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not set. Get a free key at: https://console.groq.com\n"
                "Then: export GROQ_API_KEY='your-key-here'"
            )
        self.client = Groq(api_key=api_key)
        self.model = DEFAULT_MODEL
        self.usage_count = 0
        self.rate_limit_sleep = 2  # Respect free tier rate limits

    def generate_outreach(self, lead: Dict[str, str]) -> Dict[str, str]:
        """Generate personalized outreach for a single lead."""
        prompt = PERSONALIZATION_PROMPT.format(
            company=lead.get("company", "Unknown"),
            industry=lead.get("industry", "General Business"),
            city=lead.get("city", "Unknown"),
            website=lead.get("website", ""),
            pain_points=lead.get("pain_points", "Manual processes, slow response times")
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You generate B2B outreach emails. Respond ONLY with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        self.usage_count += 1
        time.sleep(self.rate_limit_sleep)  # Rate limit protection

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "subject_line_1": f"Quick question for {lead.get('company', 'your business')}",
                "email_draft_1": response.choices[0].message.content
            }

    def bulk_generate(self, leads: List[Dict[str, str]], 
                      limit_per_day: int = 30) -> List[Dict[str, str]]:
        """Generate outreach for multiple leads with rate limiting."""
        results = []
        total = min(len(leads), limit_per_day)
        
        print(f"\n🤖 Generating outreach for {total} leads...")
        print(f"   (Rate-limited to {limit_per_day}/day for free tier)\n")

        for i, lead in enumerate(leads[:limit_per_day], 1):
            print(f"  [{i}/{total}] {lead.get('company', 'Unknown')}...", end=" ")
            try:
                outreach = self.generate_outreach(lead)
                results.append({
                    **lead,
                    "generated_at": datetime.now().isoformat(),
                    **outreach
                })
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")
                results.append({**lead, "error": str(e)})

        return results

    def save_outreach(self, results: List[Dict], output_dir: str):
        """Save generated outreach to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save individual outreach files
        outreach_dir = output_path / "emails"
        outreach_dir.mkdir(exist_ok=True)

        for lead in results:
            safe_name = lead.get("company", "unknown").replace(" ", "_").lower()
            filepath = outreach_dir / f"{safe_name}_outreach.md"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Outreach for {lead.get('company', 'Unknown')}\n\n")
                f.write(f"**Contact:** {lead.get('email', 'N/A')}\n")
                f.write(f"**Industry:** {lead.get('industry', 'N/A')}\n")
                f.write(f"**Location:** {lead.get('city', 'N/A')}\n\n")
                
                f.write("## Email Draft 1\n")
                f.write(f"**Subject:** {lead.get('subject_line_1', 'N/A')}\n")
                f.write(f"{lead.get('email_draft_1', 'N/A')}\n\n")
                
                f.write("## Email Draft 2\n")
                f.write(f"**Subject:** {lead.get('subject_line_2', 'N/A')}\n")
                f.write(f"{lead.get('email_draft_2', 'N/A')}\n\n")
                
                f.write("## Follow-up (3 days later)\n")
                f.write(f"**Subject:** {lead.get('follow_up_subject', 'N/A')}\n")
                f.write(f"{lead.get('follow_up_body', 'N/A')}\n")

        # Save master CSV for CRM import
        csv_path = output_path / "outreach_master.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        print(f"\n  ✓ Saved {len(results)} outreach files to {outreach_dir}/")
        print(f"  ✓ Saved master CSV to {csv_path}")

    def generate_crm_import(self, results: List[Dict], output_dir: str):
        """Generate HubSpot-ready CSV import."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        crm_rows = []
        for lead in results:
            crm_rows.append({
                "email": lead.get("email", ""),
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "company": lead.get("company", ""),
                "phone": lead.get("phone", ""),
                "website": lead.get("website", ""),
                "city": lead.get("city", ""),
                "lead_source": "22PM Automated Outreach",
                "personalized_draft_1": lead.get("email_draft_1", ""),
                "personalized_draft_2": lead.get("email_draft_2", ""),
                "follow_up_draft": lead.get("follow_up_body", ""),
                "outreach_status": "Ready to Send",
                "notes": f"Generated by 22PM on {datetime.now().date()}"
            })
        
        csv_path = output_path / "crm_import_ready.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            if crm_rows:
                writer = csv.DictWriter(f, fieldnames=crm_rows[0].keys())
                writer.writeheader()
                writer.writerows(crm_rows)
        
        print(f"  ✓ CRM-ready CSV saved to {csv_path}")
        print(f"  → Import this file directly into HubSpot (free tier)")


def load_leads(filepath: str) -> List[Dict[str, str]]:
    """Load leads from CSV or JSON file."""
    path = Path(filepath)
    
    if path.suffix == ".csv":
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    elif path.suffix == ".json":
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .csv or .json")


def main():
    parser = argparse.ArgumentParser(
        description="22PM Lead Nurturing Engine - Personalized outreach at scale"
    )
    parser.add_argument("--input", "-i", required=True,
                        help="Path to leads CSV/JSON file")
    parser.add_argument("--output", "-o", default="./outreach",
                        help="Output directory")
    parser.add_argument("--api-key", "-k", default=API_KEY,
                        help="Groq API key (or set GROQ_API_KEY env var)")
    parser.add_argument("--limit", "-l", type=int, default=30,
                        help="Max leads to process per day")
    
    args = parser.parse_args()

    # Load leads
    try:
        leads = load_leads(args.input)
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ {e}")
        return

    print(f"\n📊 Loaded {len(leads)} leads from {args.input}")
    print(f"🤖 Initializing Groq AI (free tier)...")

    # Initialize engine
    try:
        engine = LeadNurturingEngine(api_key=args.api_key)
    except ValueError as e:
        print(f"❌ {e}")
        return

    # Generate outreach
    results = engine.bulk_generate(leads, limit_per_day=args.limit)

    # Save results
    print(f"\n📁 Saving output to: {args.output}/")
    engine.save_outreach(results, args.output)
    engine.generate_crm_import(results, args.output)

    # Summary
    success_count = sum(1 for r in results if "error" not in r)
    print(f"\n{'='*50}")
    print(f"✅ DONE — Generated outreach for {success_count}/{len(results)} leads")
    print(f"📊 API calls used: {engine.usage_count}")
    print(f"💰 Cost: $0 (Groq free tier)")
    print(f"{'='*50}")
    
    # Sample output
    if results and "email_draft_1" in results[0]:
        print(f"\n📝 Sample outreach for {results[0].get('company', 'Lead')}:")
        print(f"   Subject: {results[0]['subject_line_1']}")
        print(f"   Body: {results[0]['email_draft_1'][:200]}...")

    print(f"\n📋 Next steps:")
    print(f"   1. Review emails in {args.output}/emails/")
    print(f"   2. Import CRM CSV into HubSpot")
    print(f"   3. Set up Make.com to auto-send 10/day")


if __name__ == "__main__":
    main()