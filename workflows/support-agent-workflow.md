# 22PM — Customer Support Agent Workflow

## Overview
A custom-trained knowledge-base chatbot that handles 80% of routine client FAQs before escalating to a human — built entirely on free-tier AI tools.

## Architecture

```
[Client Website / FAQ Docs / Knowledge Base]
            ↓
    [Data Ingestion: PDF, Web, Docs]
            ↓
    [Google Gemini API - Embedding Generation]
            ↓
    [Vector Store: ChromaDB / Pinecone FREE]
            ↓
    [RAG Pipeline: Query → Embed → Retrieve → Respond]
            ↓
    [Frontend: Free Chat Widget (Tidio/Chatwoot/Dify)]
            ↓
    [Escalation: Slack FREE / Email]
```

## Free-Tier Tools Required

| Tool          | Free Tier Limit                    | Purpose                        |
|---------------|------------------------------------|--------------------------------|
| Google Gemini API | 60 req/min FREE                 | LLM responses & embeddings     |
| ChromaDB      | Self-hosted (unlimited FREE)        | Vector database                |
| Dify.ai       | Free (300 messages/month)           | No-code agent builder          |
| Tidio         | Free (50 conversations/month)       | Chat widget + live chat        |
| Chatwoot      | Self-hosted FREE                    | Open-source support platform   |
| Slack FREE    | Unlimited with limits               | Escalation notifications       |
| GitHub Pages  | FREE                                | Host chatbot widget            |

## Step-by-Step Build (No-Code / Low-Code)

### Option A: No-Code Route (Dify.ai — 30 minutes setup)

#### Step 1: Prepare Knowledge Base
1. Gather client's documentation: FAQ pages, product manuals, support tickets
2. Export as PDF, markdown, or plain text
3. Clean formatting (remove navigation elements, headers, footers)

#### Step 2: Create AI Agent in Dify.ai (FREE)
1. Go to [Dify.ai](https://dify.ai) → Create new app → "Knowledge Base Chatbot"
2. **Upload knowledge documents:**
   - Drag & drop 5-10 source documents
   - Dify auto-splits into chunks by default
3. **Select embedding model:** Use "text-embedding-ada-002" (free with Dify)
4. **Set system prompt:**
```
You are a customer support agent for {{client_company}}.
Rules:
- Answer ONLY using the provided knowledge base
- If unsure, say "I'll connect you with a human specialist"
- Be polite, concise, and professional
- Never make up information
- Always end with "Is there anything else I can help with?"
```
5. **Configure escalation rule:**
   - Trigger: "I'll connect you with a human specialist"
   - Action: Send notification via webhook to Slack

#### Step 3: Deploy Chat Widget
1. In Dify.ai → "Deploy" → "Embedded Widget"
2. Copy the JavaScript snippet
3. Add to client's website `<body>` tag
4. Customize colors to match client's brand

### Option B: Custom RAG Pipeline (Python — Low Code)

See `scripts/custom_support_agent.py` for the full implementation.

## Knowledge Base Formatting Template

Provide this to clients to fill out:

```markdown
# Company Knowledge Base — {{Client Name}}

## 1. Company Info
- Company name:
- Website:
- Support hours:
- Response time SLA:

## 2. Common FAQs (Top 20)
### Q: [Question]  
A: [Answer]

### Q: [Question]  
A: [Answer]

## 3. Product/Service Info
- Product name:
- Key features:
- Pricing:
- Refund policy:
- Shipping/delivery:

## 4. Troubleshooting
### Issue: [Problem]
Solution: [Step-by-step fix]

## 5. Escalation Rules
When to escalate:
- [e.g., Refund requests]
- [e.g., Account deletion]
- [e.g., Technical bugs]

Who to escalate to:
- Type: [Contact email/Slack channel]
```

## Chatbot Prompt Templates

### Welcome Message
```
Hi {{visitor_name}}! 👋 I'm 22PM's AI support agent for {{client_company}}.
I can help with:
- Frequently asked questions
- Product information
- Order status
- Troubleshooting

How can I help you today?
```

### Escalation Message
```
I understand this needs a human touch. I'm connecting you with our support team now.
They'll respond within {{SLA}}.

In the meantime, here's a related article: {{kb_link}}
```

### Off-hours Auto-Response
```
Our team is currently offline. I've logged your request and here's what I found:
{{kb_answer}}
If you need further assistance, our team will follow up within {{SLA}} hours.
```

## Slack Escalation Setup (FREE)

1. Create a Slack workspace (free)
2. Go to [Slack API](https://api.slack.com) → Create App
3. Enable "Incoming Webhooks"
4. Copy webhook URL
5. In Make.com: Create scenario:
   - **Trigger:** Webhook from Dify/Tidio (escalation flag)
   - **Action:** Send to Slack webhook with message:
```
🚨 *Support Escalation Required*
*Client:* {{client_name}}
*User Question:* {{user_query}}
*Chatbot Response:* {{bot_response}}
*Time:* {{timestamp}}
*Action Required:* Respond within 30 minutes
```

## Chat Widget Customization CSS

```css
/* Add to client's website for branded widget */
.22pm-chat-widget {
    --primary-color: #6c5ce7;
    --secondary-color: #00cec9;
    --font-family: 'Inter', sans-serif;
    --border-radius: 12px;
    --header-bg: linear-gradient(135deg, #6c5ce7, #00cec9);
}
```

## Deliverable to Client

**What the client receives:**
- ✅ Custom-trained chatbot on their knowledge base
- ✅ Embeddable chat widget for their website
- ✅ Slack escalation system for unanswered questions
- ✅ Handles 80%+ of routine FAQs automatically
- ✅ 7-day trial: If not 80% deflection rate, they owe nothing

## Outsourcing Spec for Scale

Post on Upwork/Fiverr:
> **"Train a customer support chatbot using Dify.ai free tier. Upload knowledge base PDFs, configure system prompts, deploy embed widget, set up Slack escalation. Budget $400. Must demonstrate 80% FAQ deflection."**

## Metrics to Track

| Metric               | Target              |
|----------------------|---------------------|
| FAQ deflection rate  | >80%                |
| Avg response time    | <2 seconds          |
| Customer satisfaction | >4.5/5             |
| Escalation rate      | <20%                |
| Client hours saved   | 20+ hours/week      |