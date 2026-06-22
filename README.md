# 22PM — Drop-Servicing AI Workflows

**Zero capital. Infinite ambition.**

22PM is a drop-servicing business that builds custom AI workflows for businesses using **only free-tier tools**. You pay for the *result* (time saved, revenue unlocked), not the technology.

This repository contains the complete tech infrastructure to launch and scale 22PM.

---

## 🚀 Quick Start

### 1. Launch the Brand Website

Open `index.html` in any browser to see the 22PM landing page:

```
open 22pm-business/index.html
```

The site includes:
- Service menu (Lead Nurturing, Content Factory, Support Agent)
- How-it-works section (Audit → Build → Deploy → Scale)
- Pricing with 50/50 payment structure
- Complete tech stack overview
- Contact form with risk-free guarantee

### 2. Set Up Your Free-Tier Tool Accounts

| Tool | Sign Up | Free Tier Limit |
|------|---------|-----------------|
| [Google Gemini API](https://aistudio.google.com/app/apikey) | Free | 60 requests/min |
| [Groq API](https://console.groq.com) | Free | 30 req/min, 6k tokens/min |
| [Make.com](https://make.com) | Free | 2 scenarios, 1k ops/month |
| [Apify](https://apify.com) | Free | $5 free credits (no CC) |
| [Dify.ai](https://dify.ai) | Free | 300 messages/month |
| [HubSpot CRM](https://hubspot.com) | Free | 1,000 contacts |
| [Buffer](https://buffer.com) | Free | 3 channels, 10 posts/channel |
| [Canva](https://canva.com) | Free | 250k+ templates |
| [Wave Invoicing](https://waveapps.com) | Free | Unlimited invoicing |
| [Slack](https://slack.com) | Free | Unlimited workspace |

### 3. Acquire Your First Client

1. **Find 50 target prospects** — local businesses with slow response times, manual processes, or no automation
2. **Record a 2-minute Loom video** — show their current process and how 22PM would automate it
3. **Send the risk-free offer** — "I'll build this for free. If it doesn't save time in 7 days, you owe nothing."

### 4. Build the Workflow

Use the blueprints in `/workflows/` to assemble the automation:

- **Lead Nurturing:** `workflows/lead-nurturing-workflow.md`
- **Content Factory:** `workflows/content-factory-workflow.md`
- **Support Agent:** `workflows/support-agent-workflow.md`

### 5. Send Proposal & Invoice

```bash
python ops/proposal_generator.py --client "ABC Corp" --service lead_nurturing --price 1500
```

This generates:
- ✅ Professional proposal with deliverables & timeline
- ✅ Invoice for 50% deposit
- ✅ Service contract with risk-free guarantee

### 6. Collect Payment (50% deposit) → Build → Collect remaining 50%

**The golden rule:** Never hire a freelancer or start work until the client's deposit is in your account.

---

## 📁 Project Structure

```
22pm-business/
├── index.html                      # Brand landing page
├── README.md                       # This file
│
├── css/
│   └── style.css                   # Dark theme, responsive design
│
├── js/
│   └── main.js                     # Form handling, animations, mobile menu
│
├── workflows/
│   ├── lead-nurturing-workflow.md  # Lead scraping → LLM → CRM pipeline
│   ├── content-factory-workflow.md # 1 piece → 10 platform posts
│   └── support-agent-workflow.md   # Custom chatbot with Slack escalation
│
├── scripts/
│   ├── content_factory.py          # Python: Gemini-powered content repurposing
│   ├── lead_nurturing.py           # Python: Groq-powered personalization engine
│   └── support_agent_builder.py    # Python: Dify.ai config generator + RAG
│
├── ops/
│   ├── client_onboarding_template.md  # Full client journey template
│   └── proposal_generator.py          # Auto-generate proposals/invoices/contracts
│
└── assets/                         # Brand assets (logos, icons)
```

---

## 🛠 Scripts Reference

### Content Factory (`scripts/content_factory.py`)
```bash
export GEMINI_API_KEY='your-key-here'
python scripts/content_factory.py --input blog_post.txt --output ./generated_content
```
Takes 1 blog/video transcript → generates LinkedIn, Instagram, Twitter, TikTok, quote cards. Uses Gemini API free tier.

### Lead Nurturing (`scripts/lead_nurturing.py`)
```bash
export GROQ_API_KEY='your-key-here'
python scripts/lead_nurturing.py --input leads.csv --output ./outreach --limit 30
```
Takes lead data → generates personalized email drafts + follow-ups + CRM-ready CSV. Uses Groq API free tier.

### Support Agent Builder (`scripts/support_agent_builder.py`)
```bash
export GEMINI_API_KEY='your-key-here'
python scripts/support_agent_builder.py --mode dify --knowledge-base ./client_docs --company "Client Name"
```
Parses knowledge base → generates Dify.ai config + setup instructions + system prompts.

### Proposal Generator (`ops/proposal_generator.py`)
```bash
python ops/proposal_generator.py --client "ABC Corp" --service lead_nurturing --price 1500
```
Generates proposal, invoice, and contract as markdown files. Send via Wave Invoicing (free).

---

## 💰 The Drop-Servicing Model

```
[Client Pays 22PM] ──► $1,500 Retainer / Project Fee
                            │
                            ▼
                     (You keep $1,000 profit)
                            │
                            ▼
[You Pay Freelancer] ──► $500 (Via Upwork/Fiverr *after* client deposit lands)
```

**Golden Rule:** Never hire a freelancer until the client's deposit is securely in your bank account.

### Pricing Structure
| Package | Price | Free Trial |
|---------|-------|------------|
| Starter Workflow | $750/project | 7 days |
| Growth Package | $1,500/project | 7 days |
| Enterprise Retainer | $2,500/month | 7 days |

Payment: 50% deposit upfront, 50% upon completion.

---

## 📋 Client Acquisition Strategy

1. **Day 1-2:** Identify 50 local/digital businesses with poor automation
2. **Day 3-4:** Build a personalized Loom video showing their automation opportunity
3. **Day 5:** Send risk-free offer — "7-day free trial, pay only if it saves time"
4. **Day 6+:** Close on retainer after successful trial

---

## 🎯 Metrics That Matter

| Service | Key Metric | Target |
|---------|-----------|--------|
| Lead Nurturing | Outreach volume increase | 10x |
| Content Factory | Posts generated/week | 10 |
| Support Agent | FAQ deflection rate | >80% |

---

## 📄 License & Legal

- Terms of Service: See `index.html` footer
- Refund Policy: 100% refund if no measurable time savings within 7 days
- All tools used are free-tier — no ongoing software costs

---

## 🤝 Why 22PM Works

| Factor | Explanation |
|--------|-------------|
| **Zero Capital** | All tools have generous free tiers — $0 startup cost |
| **Risk-Free Offer** | 7-day trial removes all client hesitation |
| **Drop-Servicing** | Build yourself initially, outsource at scale, keep $1k+/client profit |
| **High Margin** | $1,500 project costs $0 in tools, ~$500 in freelance labor if outsourced |
| **Scalable** | Each workflow can be cloned for unlimited clients |

**Built with zero capital, infinite ambition.**

*hello@22pm.work*
