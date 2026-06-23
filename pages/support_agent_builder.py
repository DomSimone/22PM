"""
22PM — Customer Support Agent Builder
======================================
Builds a custom knowledge-base chatbot using free-tier tools.
Two modes: 1) Auto-generate Dify.ai config  2) Local RAG with ChromaDB

Usage:
    # Mode 1: Generate Dify.ai import config
    python support_agent_builder.py --mode dify --knowledge-base ./client_kb
    
    # Mode 2: Local RAG chatbot
    python support_agent_builder.py --mode local --knowledge-base ./client_kb --query "What are your hours?"

Requirements: pip install chromadb sentence-transformers google-generativeai
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional

try:
    import google.generativeai as genai
except ImportError:
    print("Installing: google-generativeai chromadb sentence-transformers")
    os.system("pip install -q google-generativeai chromadb sentence-transformers python-dotenv")
    import google.generativeai as genai


API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-1.5-flash"


KNOWLEDGE_BASE_TEMPLATE = """# Company Knowledge Base — {company_name}

## 1. Company Info
- Company name: {company_name}
- Website: {website}
- Support hours: {support_hours}
- Response time SLA: {sla}

## 2. Common FAQs
{faqs}

## 3. Escalation Rules
When to escalate:
{escalation_rules}

Who to escalate to:
{escalation_contact}
"""


class SupportAgentBuilder:
    """Build custom support chatbots using free-tier AI."""

    def __init__(self, api_key: str = API_KEY):
        if api_key:
            genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel(MODEL_NAME) if api_key else None

    def parse_knowledge_base(self, kb_path: str) -> Dict:
        """Parse a knowledge base directory of documents into structured data."""
        kb_dir = Path(kb_path)
        if not kb_dir.exists():
            raise FileNotFoundError(f"Knowledge base not found: {kb_path}")

        documents = []
        faqs = []
        
        # Scan for supported files
        for ext in ["*.txt", "*.md", "*.pdf", "*.csv"]:
            for filepath in kb_dir.rglob(ext):
                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    
                    # Try to extract Q&A pairs
                    if "Q:" in content or "Question:" in content:
                        docs = self._extract_faqs(content)
                        faqs.extend(docs)
                    
                    documents.append({
                        "source": str(filepath.relative_to(kb_dir)),
                        "content": content,
                        "type": "faq" if faqs else "document"
                    })
                except Exception as e:
                    print(f"  ⚠ Skipping {filepath}: {e}")

        return {"documents": documents, "faqs": faqs}

    def _extract_faqs(self, content: str) -> List[Dict]:
        """Extract Q&A pairs from text content."""
        faqs = []
        lines = content.split("\n")
        current_q = current_a = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("Q:") or line.startswith("Question:"):
                if current_q and current_a:
                    faqs.append({"question": current_q, "answer": current_a})
                current_q = line.split(":", 1)[1].strip()
                current_a = ""
            elif line.startswith("A:") or line.startswith("Answer:"):
                current_a = line.split(":", 1)[1].strip()
            elif current_a is not None:
                current_a += " " + line
        
        if current_q and current_a:
            faqs.append({"question": current_q, "answer": current_a})
        
        return faqs

    def generate_dify_import(self, kb_data: Dict, company_name: str,
                             output_dir: str) -> str:
        """Generate a Dify.ai importable config from parsed knowledge base."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate knowledge base markdown
        faqs_text = "\n".join(
            f"### Q: {faq['question']}\nA: {faq['answer']}\n"
            for faq in kb_data.get("faqs", [])
        ) or "See attached documents.\n"

        kb_markdown = KNOWLEDGE_BASE_TEMPLATE.format(
            company_name=company_name,
            website="[Client Website]",
            support_hours="[Configure]",
            sla="[Configure]",
            faqs=faqs_text,
            escalation_rules="- [Configure escalation triggers]\n- [Configure emergency handling]",
            escalation_contact="- Name: [Name]\n- Email: [Email]\n- Slack: #[channel]"
        )

        # Save knowledge base file
        kb_file = output_path / f"{company_name.lower().replace(' ', '_')}_knowledge_base.md"
        kb_file.write_text(kb_markdown, encoding="utf-8")
        print(f"  ✓ Knowledge base saved: {kb_file}")

        # Generate Dify.ai import instructions
        dify_config = {
            "app_name": f"{company_name} Support Agent",
            "app_type": "chatbot",
            "model": MODEL_NAME,
            "knowledge_base_sources": [str(kb_file)],
            "system_prompt": f"""You are a customer support agent for {company_name}.
Rules:
- Answer ONLY using the provided knowledge base
- If unsure, say "I'll connect you with a human specialist"
- Be polite, concise, and professional
- Never make up information
- Always end with "Is there anything else I can help with?" """,
            "escalation_webhook": "[Set up Slack webhook URL]",
            "welcome_message": f"Hi! 👋 I'm {company_name}'s AI support agent. How can I help you today?"
        }

        config_file = output_path / "dify_import_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(dify_config, f, indent=2)
        print(f"  ✓ Dify.ai config saved: {config_file}")

        # Generate setup instructions
        instructions = f"""# {company_name} — AI Support Agent Setup

## Quick Start (10 minutes, $0)

### 1. Go to Dify.ai
- Create free account at https://dify.ai
- Click "Create App" → "Knowledge Base Chatbot"

### 2. Upload Knowledge Base
- Open: {kb_file}
- Drag & drop into Dify (or copy-paste content)
- Dify will auto-chunk and embed

### 3. Configure System Prompt
Copy this into Dify's system prompt field:

```
{dify_config['system_prompt']}
```

### 4. Deploy
- Click "Deploy" → "Embedded Widget"
- Copy the JS snippet
- Add to your website's <body> tag
- Customize colors via CSS

### 5. Set Up Escalation
1. Go to [Slack API](https://api.slack.com) → Create App → Webhooks
2. Copy webhook URL
3. Paste into Dify's escalation settings
"""
        inst_file = output_path / "SETUP_INSTRUCTIONS.md"
        inst_file.write_text(instructions, encoding="utf-8")
        print(f"  ✓ Setup instructions saved: {inst_file}")

        return str(output_path)

    def answer_query(self, kb_data: Dict, query: str) -> str:
        """Answer a query using RAG with the knowledge base."""
        if not self.llm:
            return "LLM not configured. Set GEMINI_API_KEY."

        # Find relevant FAQ
        relevant_faq = None
        for faq in kb_data.get("faqs", []):
            if any(word in faq["question"].lower() for word in query.lower().split()):
                relevant_faq = faq
                break

        # Also include all document content as context
        context = ""
        for doc in kb_data.get("documents", []):
            context += doc["content"][:2000] + "\n"

        prompt = f"""You are a customer support agent. Answer ONLY using the provided context.
If the answer isn't in the context, say "I'll connect you with a human specialist."

Context:
{context}

Relevant FAQ:
{json.dumps(relevant_faq) if relevant_faq else "None found"}

User Question: {query}

Answer:"""
        
        response = self.llm.generate_content(prompt)
        return response.text


def main():
    parser = argparse.ArgumentParser(
        description="22PM Support Agent Builder - Custom knowledge-base chatbot"
    )
    parser.add_argument("--mode", "-m", choices=["dify", "local"], default="dify",
                        help="Build mode: dify (generate config) or local (test RAG)")
    parser.add_argument("--knowledge-base", "-kb", required=True,
                        help="Path to directory with knowledge base files")
    parser.add_argument("--company", "-c", default="New Client",
                        help="Client company name")
    parser.add_argument("--output", "-o", default="./support_agent",
                        help="Output directory for configs")
    parser.add_argument("--query", "-q", default=None,
                        help="Test query for local mode")
    
    args = parser.parse_args()

    print(f"\n📚 Loading knowledge base from: {args.knowledge_base}")
    print(f"🤖 Initializing AI engine...")

    try:
        builder = SupportAgentBuilder()
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return

    # Parse knowledge base
    try:
        kb_data = builder.parse_knowledge_base(args.knowledge_base)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return

    print(f"\n📊 Found {len(kb_data['documents'])} documents")
    if kb_data["faqs"]:
        print(f"📋 Extracted {len(kb_data['faqs'])} FAQ pairs")

    if args.mode == "dify":
        print(f"\n{'='*50}")
        print(f"GENERATING DIFY.AI CONFIGURATION")
        print(f"{'='*50}\n")
        
        output = builder.generate_dify_import(
            kb_data, args.company, args.output
        )
        
        print(f"\n✅ Config generated in: {output}/")
        print(f"\n📋 Next steps:")
        print(f"   1. Go to https://dify.ai → Create App → Chatbot")
        print(f"   2. Upload the knowledge base markdown file")
        print(f"   3. Copy the system prompt from SETUP_INSTRUCTIONS.md")
        print(f"   4. Deploy embed widget on client's website")
        print(f"   5. Set up Slack escalation")
        print(f"\n💰 Cost: $0 (Dify.ai free tier + 300 msg/mo)")

    elif args.mode == "local" and args.query:
        print(f"\n{'='*50}")
        print(f"TEST: RAG QUERY")
        print(f"{'='*50}\n")
        print(f"Q: {args.query}\n")
        
        answer = builder.answer_query(kb_data, args.query)
        print(f"A: {answer}\n")
        
        print(f"💰 Cost: $0 (Gemini API free tier)")


if __name__ == "__main__":
    main()