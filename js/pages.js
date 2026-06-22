/**
 * 22PM — Shared Page Components
 * Reusable navbar, footer, and utilities for all sub-pages.
 * Include this script on every page after the HTML structure.
 */

const PAGES_JS_VERSION = "1.0.0";

// ===== SHARED NAVBAR HTML =====
const SHARED_NAVBAR = `
<nav class="navbar">
    <div class="container">
        <a href="../index.html" class="logo">
            <img src="../22pmlogo24.png" alt="22PM Logo" class="logo-img" 
                 onerror="this.style.display='none'">
            <span class="logo-text">22PM</span>
        </a>
        <div class="nav-links">
            <a href="../pages/services/lead-nurturing.html">Services</a>
            <a href="../pages/how-it-works.html">How It Works</a>
            <a href="../pages/pricing.html">Pricing</a>
            <a href="../pages/stack.html">Our Stack</a>
            <a href="../pages/contact.html" class="btn-nav">Get Started</a>
        </div>
    </div>
</nav>
`;

// ===== FOOTER HTML =====
const SHARED_FOOTER = `
<footer class="footer">
    <div class="container">
        <div class="footer-grid">
            <div class="footer-brand">
                <div class="footer-logo-row">
                    <img src="../22pmlogo24.png" alt="22PM Logo" class="footer-logo-img"
                         onerror="this.style.display='none'">
                    <span class="logo-text">22PM</span>
                </div>
                <p>Drop-servicing AI workflows. You pay for results, not tech.</p>
            </div>
            <div class="footer-links">
                <h4>Services</h4>
                <a href="../pages/services/lead-nurturing.html">Lead Nurturing</a>
                <a href="../pages/services/content-factory.html">Content Factory</a>
                <a href="../pages/services/support-agent.html">Support Agent</a>
            </div>
            <div class="footer-links">
                <h4>Company</h4>
                <a href="../pages/how-it-works.html">How It Works</a>
                <a href="../pages/pricing.html">Pricing</a>
                <a href="../pages/stack.html">Tech Stack</a>
            </div>
            <div class="footer-links">
                <h4>Legal</h4>
                <a href="../pages/legal/terms.html">Terms of Service</a>
                <a href="../pages/legal/privacy.html">Privacy Policy</a>
                <a href="../pages/legal/refund.html">Refund Policy</a>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2026 22PM. All rights reserved. Built with zero capital, infinite ambition.</p>
        </div>
    </div>
</footer>
`;

// ===== PAGE FRAMEWORK =====
class TwentyTwoPage {
    constructor(options = {}) {
        this.title = options.title || "22PM";
        this.navbar = options.navbar !== false;
        this.footer = options.footer !== false;
        this.init();
    }

    init() {
        document.title = this.title;
        if (this.navbar) this.injectNavbar();
        if (this.footer) this.injectFooter();
        this.setupScrollReveal();
        this.setupNavbarScroll();
        this.setupSmoothScroll();
    }

    injectNavbar() {
        const target = document.getElementById('navbar-placeholder');
        if (target) {
            target.innerHTML = SHARED_NAVBAR;
            // Fix logo path for pages that are one level deep vs two
            const logoImg = target.querySelector('.logo-img');
            if (logoImg) {
                const depth = window.location.pathname.split('/').length - 1;
                if (depth > 3) {
                    logoImg.src = '../../22pmlogo24.png';
                }
            }
        }
    }

    injectFooter() {
        const target = document.getElementById('footer-placeholder');
        if (target) {
            target.innerHTML = SHARED_FOOTER;
        }
    }

    setupNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 100) {
                navbar.style.background = 'rgba(10, 10, 15, 0.95)';
            } else {
                navbar.style.background = 'rgba(10, 10, 15, 0.8)';
            }
        });
    }

    setupScrollReveal() {
        const elements = document.querySelectorAll('.reveal');
        if (!elements.length) return;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });
        elements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }

    setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }
}

// ===== SERVICE DATA (shared across service pages) =====
const SERVICE_DATA = {
    "lead-nurturing": {
        title: "Automated Lead Nurturing",
        icon: "📧",
        subtitle: "10x Your Outreach Without Adding Headcount",
        description: "A fully automated pipeline that scrapes local leads, generates hyper-personalized emails using AI, and pushes everything into your CRM — all running on free-tier tools.",
        bestFor: ["B2B Agencies", "Real Estate Firms", "Consulting Companies", "Local Service Businesses"],
        deliverables: [
            "Local lead scraping pipeline (50+ leads/day)",
            "AI-powered email personalization engine",
            "HubSpot CRM integration with custom fields",
            "Automated email dispatch (10/day, spam-safe)",
            "7-day free trial with performance monitoring"
        ],
        workflow: [
            { step: "01", title: "Scrape", desc: "Apify scraper finds local businesses matching your ideal client profile" },
            { step: "02", title: "Enrich", desc: "Groq/Gemini AI analyzes each lead and generates personalized outreach" },
            { step: "03", title: "CRM", desc: "All leads + drafts pushed to HubSpot automatically" },
            { step: "04", title: "Send", desc: "Gmail dispatches 10 personalized emails per day, follow-ups included" }
        ],
        pricing: "$1,500",
        techStack: [
            { name: "Apify", tier: "$5 free credits" },
            { name: "Groq API", tier: "30 req/min free" },
            { name: "Make.com", tier: "2 scenarios free" },
            { name: "HubSpot", tier: "1,000 contacts free" },
            { name: "Gmail", tier: "500 emails/day free" }
        ]
    },
    "content-factory": {
        title: "AI Content Factory",
        icon: "🎨",
        subtitle: "Turn 1 Piece of Content Into 10 Platform-Specific Posts",
        description: "Take one blog post, video, or podcast and automatically generate a week's worth of platform-optimized content with custom graphics — no extra work required.",
        bestFor: ["Content Creators", "E-commerce Brands", "Marketing Teams", "Agencies"],
        deliverables: [
            "Content ingestion (YouTube, blog, podcast)",
            "10 platform-specific post generations",
            "Auto-designed graphics via Canva API",
            "2-week content calendar with Buffer scheduling",
            "7-day free trial with engagement report"
        ],
        workflow: [
            { step: "01", title: "Ingest", desc: "Paste a URL or upload a file — we extract the core content automatically" },
            { step: "02", title: "Chunk", desc: "Gemini AI analyzes and identifies key angles, quotes, and insights" },
            { step: "03", title: "Generate", desc: "10 posts created for LinkedIn, Instagram, Twitter, TikTok, and more" },
            { step: "04", title: "Schedule", desc: "Auto-designed graphics + captions scheduled 2 weeks out in Buffer" }
        ],
        pricing: "$1,500",
        techStack: [
            { name: "Google Gemini", tier: "60 req/min free" },
            { name: "Canva", tier: "250k+ templates free" },
            { name: "Buffer", tier: "3 channels free" },
            { name: "Make.com", tier: "2 scenarios free" },
            { name: "YouTube API", tier: "10k units/day free" }
        ]
    },
    "support-agent": {
        title: "Customer Support Agent",
        icon: "🤖",
        subtitle: "Handle 80% of FAQs Automatically, 24/7",
        description: "A custom-trained AI chatbot that learns your business and answers customer questions instantly. Only escalates to humans when it can't help — saving your team 20+ hours per week.",
        bestFor: ["E-commerce Stores", "Local Service Businesses", "Clinics & Practices", "SaaS Companies"],
        deliverables: [
            "Custom-trained chatbot on your knowledge base",
            "Embeddable website widget with brand styling",
            "Slack escalation system for complex queries",
            "24/7 automated FAQ response",
            "7-day free trial with deflection rate report"
        ],
        workflow: [
            { step: "01", title: "Upload", desc: "Send us your FAQs, manuals, and support docs" },
            { step: "02", title: "Train", desc: "We configure Dify.ai with your data and custom system prompts" },
            { step: "03", title: "Deploy", desc: "Embed widget on your site with matching brand colors" },
            { step: "04", title: "Escalate", desc: "Unanswered questions route to Slack for human follow-up" }
        ],
        pricing: "$1,500",
        techStack: [
            { name: "Dify.ai", tier: "300 messages/month free" },
            { name: "Google Gemini", tier: "60 req/min free" },
            { name: "Slack", tier: "Free workspace" },
            { name: "Tidio", tier: "50 conversations/month free" },
            { name: "GitHub Pages", tier: "Free hosting" }
        ]
    }
};

/**
 * Generate a service page from data
 * Used by all three service HTML pages
 */
function renderServicePage(serviceKey) {
    const data = SERVICE_DATA[serviceKey];
    if (!data) return;

    // Hero
    const heroTitle = document.getElementById('service-hero-title');
    const heroSub = document.getElementById('service-hero-sub');
    const heroDesc = document.getElementById('service-hero-desc');
    if (heroTitle) heroTitle.innerHTML = `${data.icon} ${data.title}`;
    if (heroSub) heroSub.textContent = data.subtitle;
    if (heroDesc) heroDesc.textContent = data.description;

    // Best for list
    const bestForList = document.getElementById('best-for-list');
    if (bestForList) {
        bestForList.innerHTML = data.bestFor.map(item => `<li>${item}</li>`).join('');
    }

    // Deliverables
    const deliverablesList = document.getElementById('deliverables-list');
    if (deliverablesList) {
        deliverablesList.innerHTML = data.deliverables.map(d => `<li>✅ ${d}</li>`).join('');
    }

    // Workflow
    const workflowContainer = document.getElementById('workflow-steps');
    if (workflowContainer) {
        workflowContainer.innerHTML = data.workflow.map(w => `
            <div class="step reveal">
                <div class="step-num">${w.step}</div>
                <h3>${w.title}</h3>
                <p>${w.desc}</p>
            </div>
        `).join('');
    }

    // Pricing
    const pricingEl = document.getElementById('service-pricing');
    if (pricingEl) pricingEl.textContent = data.pricing;

    // Tech stack
    const techContainer = document.getElementById('tech-stack-list');
    if (techContainer) {
        techContainer.innerHTML = data.techStack.map(t => `
            <div class="stack-item reveal">
                <h4>${t.name}</h4>
                <p>${t.tier} — cost: $0</p>
            </div>
        `).join('');
    }

    // Initialize shared page behavior
    new TwentyTwoPage({ title: `${data.title} | 22PM` });
}