"""
22PM — Automated Proposal & Invoice Generator
==============================================
Generates professional client proposals, invoices, and contracts 
as markdown/PDF. Use with Wave Invoicing (free) or Bonsai.

Usage:
    python proposal_generator.py --client "ABC Corp" --service "Lead Nurturing" --price 1500
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta


CLIENT_SCOPE_TEMPLATES = {
    "lead_nurturing": {
        "name": "Automated Lead Nurturing Pipeline",
        "description": "Scrape local leads, generate hyper-personalized outreach, and push to CRM",
        "timeline": "5 days",
        "deliverables": [
            "Apify web scraper configured for local lead generation",
            "Make.com orchestration workflow (Webhook → Filter → LLM → CRM)",
            "Groq/Gemini API integration for personalized email drafting",
            "HubSpot CRM integration with custom lead properties",
            "Gmail auto-dispatch (10 emails/day, spam-safe)",
            "7-day monitoring period with performance report"
        ],
        "free_tier_breakdown": {
            "Apify": "$5 free credits",
            "Make.com": "2 scenarios free",
            "Groq API": "30 req/min free",
            "HubSpot": "1,000 contacts free",
            "Gmail": "500 emails/day free"
        }
    },
    "content_factory": {
        "name": "AI Content Factory",
        "description": "Turn 1 long-form piece into 10 platform-specific posts with auto-designed graphics",
        "timeline": "4 days",
        "deliverables": [
            "YouTube/blog content ingestion pipeline",
            "Gemini API multi-format generation (LinkedIn, IG, Twitter, TikTok)",
            "Canva auto-design integration for graphics",
            "Buffer scheduling (2 weeks of content)",
            "Content calendar template",
            "7-day monitoring period with engagement report"
        ],
        "free_tier_breakdown": {
            "Gemini API": "60 req/min free",
            "Canva": "250k+ free templates",
            "Buffer": "3 channels free",
            "Make.com": "2 scenarios free",
            "YouTube API": "10k units/day free"
        }
    },
    "support_agent": {
        "name": "Customer Support Agent Chatbot",
        "description": "Custom-trained chatbot handling 80% of FAQs with human escalation",
        "timeline": "3 days",
        "deliverables": [
            "Knowledge base parsing & structuring",
            "Dify.ai chatbot configuration with custom system prompt",
            "Website embed widget with brand customization",
            "Slack escalation webhook integration",
            "Training on up to 10 source documents",
            "7-day monitoring period with deflection rate report"
        ],
        "free_tier_breakdown": {
            "Dify.ai": "300 messages/month free",
            "Gemini API": "60 req/min free",
            "Slack": "Free workspace",
            "GitHub Pages": "Free hosting",
            "Chatwoot": "Self-hosted free"
        }
    }
}


def generate_proposal(client_name: str, service_key: str, price: int) -> str:
    """Generate a professional proposal document."""
    service = CLIENT_SCOPE_TEMPLATES.get(service_key)
    if not service:
        raise ValueError(f"Unknown service: {service_key}")

    deposit = price // 2
    completion = price - deposit

    proposal = f"""---
22PM PROPOSAL
Client: {client_name}
Service: {service['name']}
Date: {datetime.now().strftime('%B %d, %Y')}
Validity: 14 days
---

# Proposal for {client_name}

## Service Overview
**{service['name']}** — {service['description']}

22PM builds custom AI workflows using free-tier tools. You pay for the result, not the technology.

## What You'll Get
"""
    for d in service["deliverables"]:
        proposal += f"- ✅ {d}\n"

    proposal += f"""
## Timeline: {service['timeline']}

| Day | Activity |
|-----|----------|
| 1-2 | Build & configure workflow |
| 3-4 | Testing & refinement |
| 5-{3 + int(service['timeline'].split()[0]) - 2} | Live deployment & monitoring |
| {4 + int(service['timeline'].split()[0]) - 2} | Results review & handoff |

## Investment

| Item | Amount |
|------|--------|
| **Total Project Fee** | **${price:,}** |
| Deposit (50% — due now) | ${deposit:,} |
| Completion (50% — due after 7-day trial) | ${completion:,} |

**Risk-Free Guarantee:** If the workflow doesn't save measurable time within 7 days, your deposit is fully refunded.

## Tech Stack (All Free Tiers)

| Tool | Free Tier | Our Cost |
|------|-----------|----------|
"""
    for tool, limit in service["free_tier_breakdown"].items():
        proposal += f"| {tool} | {limit} | $0 |\n"

    proposal += f"""
## Why This Is a No-Brainer

You're getting a custom AI automation system that:
- **Costs you $0 to start** (7-day free trial)
- **Saves 10+ hours/week** of manual work
- **Uses enterprise-grade AI** (Gemini, Groq) at $0 cost
- **Requires no technical effort** from your team
- **Carries zero risk** — pay only if it works

## Next Steps

1. Reply "Yes" to accept this proposal
2. Send 50% deposit via Wave Invoicing (link below)
3. I build and deploy within {service['timeline']}
4. We review results after 7 days

---

*22PM — Automate your business bottlenecks. Pay for results, not tech.*
*hello@22pm.work*
"""
    return proposal


def generate_invoice(client_name: str, service_key: str, price: int,
                     invoice_number: str = None) -> str:
    """Generate a professional invoice."""
    service = CLIENT_SCOPE_TEMPLATES.get(service_key)
    if not invoice_number:
        invoice_number = f"22PM-{datetime.now().strftime('%Y%m')}-{hash(client_name) % 100:02d}"

    deposit = price // 2

    invoice = f"""---
22PM INVOICE
=============
Invoice #: {invoice_number}
Date: {datetime.now().strftime('%B %d, %Y')}
Due: {(datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')}
Status: Due Now (50% Deposit)
---

## Bill To
{client_name}

## Description
{service['name']} — Deposit (50%)

## Payment Details

| Description | Amount |
|-------------|--------|
| {service['name']} — Project Setup (50% deposit) | ${deposit:,} |
| **Total Due** | **${deposit:,}** |

## Payment Methods
- **Wave Invoicing:** [Send payment link via Wave]
- **Bank Transfer:** [Your bank details]
- **PayPal:** [Your PayPal email]

## Terms
- 50% deposit due before work begins
- 50% completion due after 7-day trial
- Full refund if deliverables not met within 7 days

---

*Thank you for choosing 22PM!*
*hello@22pm.work*
"""
    return invoice


def generate_contract(client_name: str, service_key: str, price: int) -> str:
    """Generate a simple service contract."""
    service = CLIENT_SCOPE_TEMPLATES.get(service_key)

    contract = f"""---
22PM SERVICE CONTRACT
====================
Date: {datetime.now().strftime('%B %d, %Y')}
---

## Parties
**22PM** (Service Provider)
Email: hello@22pm.work

**{client_name}** (Client)

## Scope of Work
22PM agrees to build and deploy the following workflow:
- **{service['name']}**
- {service['description']}

### Deliverables
"""
    for d in service["deliverables"]:
        contract += f"- {d}\n"

    contract += f"""
## Timeline
- Build phase: {service['timeline']}
- Trial period: 7 calendar days
- Conversion to retainer: Upon client approval

## Payment
- **Project Fee:** ${price:,} total
- **Deposit:** ${price//2:,} (50% — due now, refundable during trial)
- **Completion:** ${price - price//2:,} (50% — due after trial approval)
- **Ongoing Retainer (optional):** ${price:,}/month after trial

## Risk-Free Guarantee
If {client_name} is not satisfied with the workflow's time savings within 7 days:
1. Workflow will be decommissioned
2. Full deposit refund will be issued within 3 business days
3. No further payment is due

## Client Obligations
- Provide timely access to tools and APIs
- Provide knowledge base documents if applicable
- Review deliverables within 24 hours
- Provide feedback at end of trial period

## 22PM Obligations
- Build and deploy working workflow
- Monitor for 7 days post-deployment
- Make reasonable adjustments during trial
- Provide documentation and handoff

## Signatures
_________________________          _________________________
**22PM Representative**              **{client_name} Representative**
Date: ____________                  Date: ____________
"""
    return contract


def main():
    parser = argparse.ArgumentParser(
        description="22PM Proposal & Invoice Generator"
    )
    parser.add_argument("--client", "-c", required=True,
                        help="Client name")
    parser.add_argument("--service", "-s", required=True,
                        choices=list(CLIENT_SCOPE_TEMPLATES.keys()),
                        help="Service type")
    parser.add_argument("--price", "-p", type=int, default=1500,
                        help="Project price in USD")
    parser.add_argument("--output", "-o", default="./ops/proposals",
                        help="Output directory")
    parser.add_argument("--generate", "-g", choices=["all", "proposal", "invoice", "contract"],
                        default="all", help="Which documents to generate")
    
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    safe_name = args.client.lower().replace(" ", "_")

    print(f"\n📄 Generating documents for {args.client}...\n")

    if args.generate in ("all", "proposal"):
        proposal = generate_proposal(args.client, args.service, args.price)
        filepath = output_path / f"{safe_name}_proposal.md"
        filepath.write_text(proposal, encoding="utf-8")
        print(f"  ✓ Proposal: {filepath}")

    if args.generate in ("all", "invoice"):
        invoice = generate_invoice(args.client, args.service, args.price)
        filepath = output_path / f"{safe_name}_invoice.md"
        filepath.write_text(invoice, encoding="utf-8")
        print(f"  ✓ Invoice:  {filepath}")

    if args.generate in ("all", "contract"):
        contract = generate_contract(args.client, args.service, args.price)
        filepath = output_path / f"{safe_name}_contract.md"
        filepath.write_text(contract, encoding="utf-8")
        print(f"  ✓ Contract: {filepath}")

    print(f"\n✅ Documents saved to: {output_path}/")
    print(f"\n   Next step: Send via Wave Invoicing or Bonsai (both free)")


if __name__ == "__main__":
    main()