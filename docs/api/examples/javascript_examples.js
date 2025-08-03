/**
 * JavaScript/Node.js SDK Examples for Reddit Content Platform API
 */

class RedditContentPlatformAPI {
    constructor(baseUrl, accessToken = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.accessToken = accessToken;
        this.headers = {
            'Content-Type': 'application/json'
        };
        
        if (accessToken) {
            this.headers['Authorization'] = `Bearer ${accessToken}`;
        }
    }
    
    async authenticate(authCode, state) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: authCode, state: state })
        });
        
        if (!response.ok) {
            throw new Error(`Authentication failed: ${response.statusText}`);
        }
        
        const tokens = await response.json();
        this.accessToken = tokens.access_token;
        this.headers['Authorization'] = `Bearer ${this.accessToken}`;
        
        return tokens;
    }
    
    async refreshToken(refreshToken) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${refreshToken}` }
        });
        
        if (!response.ok) {
            throw new Error(`Token refresh failed: ${response.statusText}`);
        }
        
        const tokens = await response.json();
        this.accessToken = tokens.access_token;
        this.headers['Authorization'] = `Bearer ${this.accessToken}`;
        
        return tokens;
    }
    
    async createKeyword(keyword, description = null) {
        const data = { keyword };
        if (description) {
            data.description = description;
        }
        
        const response = await fetch(`${this.baseUrl}/api/v1/keywords`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create keyword: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async getKeywords(page = 1, pageSize = 20) {
        const params = new URLSearchParams({ page, page_size: pageSize });
        const response = await fetch(`${this.baseUrl}/api/v1/keywords?${params}`, {
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get keywords: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async startCrawling(keywordIds, limit = 100) {
        const data = { keyword_ids: keywordIds, limit };
        
        const response = await fetch(`${this.baseUrl}/api/v1/crawling/start`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to start crawling: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async getCrawlingStatus() {
        const response = await fetch(`${this.baseUrl}/api/v1/crawling/status`, {
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get crawling status: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async generateContent(contentType, keywordIds, templateId = null) {
        const data = {
            content_type: contentType,
            keyword_ids: keywordIds
        };
        
        if (templateId) {
            data.template_id = templateId;
        }
        
        const response = await fetch(`${this.baseUrl}/api/v1/content/generate`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to generate content: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async getContent(contentId) {
        const response = await fetch(`${this.baseUrl}/api/v1/content/${contentId}`, {
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get content: ${response.statusText}`);
        }
        
        return response.json();
    }
}

// Example usage
async function example() {
    const api = new RedditContentPlatformAPI('http://localhost:8000');
    
    try {
        // After OAuth2 flow, authenticate
        // const tokens = await api.authenticate('auth_code', 'state');
        
        // Create keywords
        const keyword = await api.createKeyword('artificial intelligence', 'AI discussions');
        console.log('Created keyword:', keyword);
        
        // Start crawling
        const crawlResult = await api.startCrawling([keyword.id], 50);
        console.log('Started crawling:', crawlResult);
        
        // Monitor crawling status
        const status = await api.getCrawlingStatus();
        console.log('Crawling status:', status);
        
        // Generate content
        const contentResult = await api.generateContent('blog_post', [keyword.id]);
        console.log('Generated content:', contentResult);
        
    } catch (error) {
        console.error('API Error:', error.message);
    }
}

// For Node.js environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RedditContentPlatformAPI;
}

// For browser environments
if (typeof window !== 'undefined') {
    window.RedditContentPlatformAPI = RedditContentPlatformAPI;
}
