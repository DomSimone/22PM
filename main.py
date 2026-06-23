"""
22PM AI Engine — FastAPI Server
================================
Activation point for all services. Deploy to any cloud provider.
Start: uvicorn main:app --reload

All endpoints are POST/GET with JSON payloads.
Rate-limited to free-tier quotas automatically.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from llm import llm


# ===== Logging =====
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("22pm.server")


# ===== App Lifecycle =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("=" * 50)
    logger.info("22PM AI Engine Starting")
    logger.info(f"  Providers: {', '.join(settings.get_active_providers()) or 'NONE'}")
    logger.info(f"  Gemini model: {settings.GEMINI_MODEL}")
    logger.info(f"  Groq model: {settings.GROQ_MODEL}")
    logger.info(f"  Rate limits: Gemini {settings.GEMINI_RATE_LIMIT_RPM} rpm, "
                f"Groq {settings.GROQ_RATE_LIMIT_RPM} rpm")
    logger.info(f"  Cost: $0 (free tiers)")
    logger.info("=" * 50)

    if not settings.is_configured() and settings.DEBUG:
        logger.warning("⚠ No API keys configured. Set GEMINI_API_KEY or GROQ_API_KEY in .env")

    yield

    logger.info("22PM AI Engine Shutting Down")


# ===== App =====

app = FastAPI(
    title="22PM AI Engine",
    description="Backend AI engine for 22PM drop-servicing workflows. "
                "Powered by free-tier Gemini and Groq APIs.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Health & Status =====

@app.get("/")
async def root():
    return {
        "service": "22PM AI Engine",
        "version": "1.0.0",
        "status": "running",
        "providers": settings.get_active_providers(),
        "cost": "$0 (free tiers)"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "llm_configured": settings.is_configured(),
        "active_providers": settings.get_active_providers()
    }


# ===== Import Service Routes =====

# Lead Nurturing
from services.lead_nurturing import (
    LeadNurturingService,
    Lead, OutreachDraft, BatchRequest, BatchResponse
)

# Content Factory
from services.content_factory import (
    ContentFactoryService,
    ContentRequest, SinglePlatformRequest,
    ContentResponse, BatchContentResponse
)

# Support Agent
from services.support_agent import (
    SupportAgentService,
    TrainRequest, TrainResponse,
    AskRequest, AskResponse,
    StatusResponse
)


# ===== Service Instances =====

lead_service = LeadNurturingService()
content_service = ContentFactoryService()
support_service = SupportAgentService()


# ================================================================
# LEAD NURTURING ENDPOINTS
# ================================================================

@app.post("/api/leads/enrich", tags=["Lead Nurturing"])
async def enrich_lead(lead: Lead):
    """Enrich a single lead with AI-inferred industry, city, and pain points."""
    enriched = await lead_service.enrich_lead(lead)
    return enriched.model_dump()

@app.post("/api/leads/outreach", tags=["Lead Nurturing"])
async def generate_outreach(lead: Lead):
    """Generate personalized email outreach for a single lead."""
    outreach = await lead_service.generate_outreach(lead)
    return outreach.model_dump()

@app.post("/api/leads/bulk", tags=["Lead Nurturing"])
async def bulk_process(request: BatchRequest):
    """
    Process multiple leads: enrich + generate outreach.
    Rate-limited to 30 leads/day (Groq free tier).
    Returns CRM-ready CSV in response.
    """
    response = await lead_service.process_batch(request)

    # Generate CRM CSV
    csv_data = lead_service.to_crm_csv(response.results)

    return JSONResponse(content={
        "batch": response.model_dump(),
        "crm_csv": csv_data,
        "crm_csv_filename": "crm_import_ready.csv",
        "download_instruction": "Copy the crm_csv content into a .csv file and import into HubSpot"
    })

@app.post("/api/leads/csv", tags=["Lead Nurturing"])
async def process_csv(csv_content: str, limit: int = 30):
    """Upload and process a CSV file of leads."""
    leads = lead_service.parse_csv(csv_content)
    request = BatchRequest(leads=leads, limit_per_day=limit)
    return await bulk_process(request)


# ================================================================
# CONTENT FACTORY ENDPOINTS
# ================================================================

@app.post("/api/content/generate", tags=["Content Factory"])
async def generate_content(request: ContentRequest):
    """Generate platform-specific posts from source content."""
    result = await content_service.generate_all(request)
    
    calendar = content_service.format_content_calendar(result.results)
    
    return JSONResponse(content={
        **result.model_dump(),
        "content_calendar": calendar
    })

@app.post("/api/content/generate-one", tags=["Content Factory"])
async def generate_single(request: SinglePlatformRequest):
    """Generate a post for a single platform."""
    result = await content_service.generate_single(request)
    return result.model_dump()

@app.post("/api/content/repurpose", tags=["Content Factory"])
async def repurpose(url: str, platforms: str = "linkedin,instagram,twitter,tiktok"):
    """
    Repurpose a URL (blog, video, podcast) into platform posts.
    Note: For full URL scraping, use the Python script (scripts/content_factory.py)
    """
    return {
        "message": "For URL-based repurposing, use the command-line tool: "
                   "python scripts/content_factory.py --input url.txt --output ./posts",
        "note": "Or paste the article text directly into /api/content/generate"
    }


# ================================================================
# SUPPORT AGENT ENDPOINTS
# ================================================================

@app.post("/api/support/train", tags=["Support Agent"])
async def train_support_agent(request: TrainRequest):
    """Train the chatbot on client's knowledge base documents."""
    result = await support_service.train(request)
    return result.model_dump()

@app.post("/api/support/ask", tags=["Support Agent"])
async def ask_support_agent(request: AskRequest):
    """Ask a question to the trained chatbot."""
    result = await support_service.ask(request)
    return result.model_dump()

@app.get("/api/support/status", tags=["Support Agent"])
async def support_agent_status(collection: str = "22pm_knowledge_base"):
    """Check the chatbot's status and document count."""
    result = await support_service.status(collection)
    return result.model_dump()


# ================================================================
# LLM UTILITY ENDPOINTS
# ================================================================

from pydantic import BaseModel as PydanticBaseModel

class PromptRequest(PydanticBaseModel):
    prompt: str
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    prefer: str = "auto"

@app.post("/api/llm/generate", tags=["LLM"])
async def llm_generate(request: PromptRequest):
    """Direct LLM access — generate text from any prompt."""
    result = await llm.generate(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        prefer=request.prefer
    )
    return {
        "text": result.text,
        "provider": result.provider,
        "model": result.model,
        "latency_ms": result.latency_ms,
        "error": result.error,
        "cost": "$0 (free tier)"
    }


# ===== Entry Point =====

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
