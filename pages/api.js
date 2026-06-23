/**
 * 22PM — Frontend API Client
 * ============================
 * Connects the web app to the FastAPI backend engine.
 * 
 * Configuration:
 *   Set API_BASE_URL to your deployed engine URL.
 *   Default: http://localhost:8000 (local development)
 * 
 * All endpoints are POST/GET with JSON payloads.
 * All costs: $0 (free-tier LLM providers)
 */

const API_BASE_URL = window._22PM_API_URL || 'http://localhost:8000';

const API_CLIENT_VERSION = '1.0.0';

/**
 * Generic API request helper.
 * Handles errors, CORS, and response parsing.
 */
async function apiRequest(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error ${response.status}: ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            console.warn(`API unavailable at ${API_BASE_URL}. Engine not running.`);
            return {
                error: 'engine_offline',
                message: `AI Engine is not running. Start with: cd engine && uvicorn main:app --reload`,
                api_url: API_BASE_URL,
                status: 'offline'
            };
        }
        throw error;
    }
}


// ================================================================
// 1. LEAD NURTURING API
// ================================================================

const LeadNurturingAPI = {
    /**
     * Enrich a single lead with AI-inferred data.
     * @param {Object} lead - { company, email, industry?, city?, website? }
     * @returns {Object} Enriched lead data
     */
    enrichLead: async (lead) => {
        return apiRequest('/api/leads/enrich', 'POST', lead);
    },

    /**
     * Generate personalized outreach for a lead.
     * @param {Object} lead - Lead data
     * @returns {Object} { subject_line_1, subject_line_2, email_draft_1, email_draft_2, ... }
     */
    generateOutreach: async (lead) => {
        return apiRequest('/api/leads/outreach', 'POST', lead);
    },

    /**
     * Bulk process leads: enrich + generate outreach.
     * @param {Array} leads - Array of lead objects
     * @param {number} limit - Max leads to process (default 30)
     * @returns {Object} { batch: {...}, crm_csv: "..." }
     */
    bulkProcess: async (leads, limit = 30) => {
        return apiRequest('/api/leads/bulk', 'POST', {
            leads: leads,
            limit_per_day: limit
        });
    },

    /**
     * Upload a CSV string of leads for processing.
     * @param {string} csvContent - CSV text with headers
     * @param {number} limit - Max leads
     * @returns {Object} Processed results with CRM-ready CSV
     */
    processCSV: async (csvContent, limit = 30) => {
        return apiRequest(`/api/leads/csv?csv_content=${encodeURIComponent(csvContent)}&limit=${limit}`, 'POST');
    },

    /**
     * Check if API is online.
     * @returns {Object} { status, llm_configured, active_providers }
     */
    health: async () => {
        return apiRequest('/health');
    }
};


// ================================================================
// 2. CONTENT FACTORY API
// ================================================================

const ContentFactoryAPI = {
    /**
     * Generate posts for all platforms from source text.
     * @param {string} sourceText - Blog post, transcript, etc.
     * @param {Array} platforms - ['linkedin','instagram','twitter','tiktok','quote_card']
     * @param {string} brandVoice - Optional brand guidelines
     * @returns {Object} { results: [...], content_calendar: "..." }
     */
    generateAll: async (sourceText, platforms = ['linkedin','instagram','twitter','tiktok','quote_card'], brandVoice = '') => {
        return apiRequest('/api/content/generate', 'POST', {
            source_text: sourceText,
            platforms: platforms,
            brand_voice: brandVoice
        });
    },

    /**
     * Generate a single platform post.
     * @param {string} sourceText - Source content
     * @param {string} platform - One of: linkedin, instagram, twitter, tiktok, quote_card
     * @param {string} brandVoice - Optional brand voice
     * @returns {Object} { platform, content }
     */
    generateOne: async (sourceText, platform, brandVoice = '') => {
        return apiRequest('/api/content/generate-one', 'POST', {
            source_text: sourceText,
            platform: platform,
            brand_voice: brandVoice
        });
    },

    /**
     * Quick content calendar generation.
     * @param {string} sourceText - Source content
     * @returns {Object} Results with content_calendar field
     */
    generateCalendar: async (sourceText) => {
        const result = await ContentFactoryAPI.generateAll(sourceText);
        return result.content_calendar || 'Calendar generation failed.';
    }
};


// ================================================================
// 3. SUPPORT AGENT API
// ================================================================

const SupportAgentAPI = {
    /**
     * Train the chatbot on knowledge base documents.
     * @param {Array} documents - Array of { content, source?, metadata? }
     * @param {string} collectionName - Client identifier
     * @param {boolean} clearExisting - Reset before training
     * @returns {Object} { status, documents_indexed, collection_name }
     */
    train: async (documents, collectionName = '22pm_knowledge_base', clearExisting = false) => {
        return apiRequest('/api/support/train', 'POST', {
            documents: documents.map(d => ({
                content: typeof d === 'string' ? d : d.content,
                source: d.source || 'client_document',
                metadata: d.metadata || {}
            })),
            collection_name: collectionName,
            clear_existing: clearExisting
        });
    },

    /**
     * Ask a question to the trained chatbot.
     * @param {string} query - User's question
     * @param {string} collectionName - Client collection
     * @param {Array} conversationHistory - Previous messages [{role, content}]
     * @returns {Object} { answer, sources, confidence }
     */
    ask: async (query, collectionName = '22pm_knowledge_base', conversationHistory = []) => {
        return apiRequest('/api/support/ask', 'POST', {
            query: query,
            collection_name: collectionName,
            conversation_history: conversationHistory
        });
    },

    /**
     * Get chatbot status.
     * @param {string} collectionName - Collection to check
     * @returns {Object} { collection_name, document_count, provider, status }
     */
    status: async (collectionName = '22pm_knowledge_base') => {
        return apiRequest(`/api/support/status?collection=${encodeURIComponent(collectionName)}`);
    }
};


// ================================================================
// 4. LLM UTILITY API
// ================================================================

const LLMAPI = {
    /**
     * Direct LLM access. Generate text from any prompt.
     * @param {string} prompt - The user prompt
     * @param {string} systemPrompt - System instructions
     * @param {Object} options - { temperature, maxTokens, prefer }
     * @returns {Object} { text, provider, model, latency_ms }
     */
    generate: async (prompt, systemPrompt = '', options = {}) => {
        return apiRequest('/api/llm/generate', 'POST', {
            prompt: prompt,
            system_prompt: systemPrompt,
            temperature: options.temperature ?? 0.7,
            max_tokens: options.maxTokens ?? 2048,
            prefer: options.prefer ?? 'auto'
        });
    }
};


// ================================================================
// 5. SYSTEM INTEGRATION — Demo / Test Functions
// ================================================================

const TwentyTwoPM = {
    version: API_CLIENT_VERSION,
    apiBaseUrl: API_BASE_URL,

    /** Check if the AI engine is running */
    async isOnline() {
        const health = await LeadNurturingAPI.health();
        return health.status === 'healthy' || health.status === 'running';
    },

    /** Quick demo: Generate leads outreach (sample data) */
    async demoLeads() {
        const sampleLeads = [
            { company: "Acme Realty", email: "info@acmerealty.com", industry: "Real Estate", city: "Austin" },
            { company: "Bright Agency", email: "hello@brightagency.io", industry: "Marketing", city: "New York" },
        ];
        return await LeadNurturingAPI.bulkProcess(sampleLeads, 2);
    },

    /** Quick demo: Generate content posts */
    async demoContent(text) {
        const sampleText = text || "Artificial intelligence is transforming how businesses operate. From automating repetitive tasks to generating insights from data, AI tools are becoming essential for modern organizations. The key is knowing which processes to automate first.";
        return await ContentFactoryAPI.generateAll(sampleText);
    },

    /** Connection status display */
    async getStatus() {
        const online = await this.isOnline();
        return {
            engine: online ? '🟢 Online' : '🔴 Offline',
            api_url: this.apiBaseUrl,
            providers: online ? (await LeadNurturingAPI.health()).active_providers : [],
            cost: '$0 (free tiers)',
            documentation: `${this.apiBaseUrl}/docs`
        };
    }
};


// ================================================================
// EXPORT
// ================================================================

// Make available globally
window.TwentyTwoPM = TwentyTwoPM;
window.LeadNurturingAPI = LeadNurturingAPI;
window.ContentFactoryAPI = ContentFactoryAPI;
window.SupportAgentAPI = SupportAgentAPI;
window.LLMAPI = LLMAPI;

console.log(`%c 22PM API Client v${API_CLIENT_VERSION} `, 'background: #000; color: #fff; font-weight: bold; padding: 4px 8px; border-radius: 4px;');
console.log(`%c API URL: ${API_BASE_URL}`, 'color: #888;');
console.log(`%c To configure: window._22PM_API_URL = 'https://your-deployed-engine.com'`, 'color: #555;');
console.log(`%c Cost: $0 (free tiers)`, 'color: #00cec9;');