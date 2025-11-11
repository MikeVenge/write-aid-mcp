// Finchat CoT API Configuration
// Now uses backend proxy server for secure API calls

const FINCHAT_CONFIG = {
    // Backend proxy URL
    // Auto-detect: use environment variable if set, otherwise use localhost for development
    BACKEND_URL: typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
        ? (window.BACKEND_URL || 'https://your-railway-backend.railway.app')  // Production: Set this via environment or replace with your Railway URL
        : 'http://localhost:5001',  // Development: localhost
    
    // MCP Mode (Model Context Protocol)
    // Set to true if using MCP-based FinChat integration
    // MCP URL should be configured on backend via FINCHAT_MCP_URL env var
    USE_MCP: true,  // Enable MCP mode by default
    MCP_ENDPOINT: '/api/mcp/analyze',  // MCP analysis endpoint
    
    // REST API Mode (fallback)
    // CoT slug for AI detection
    // Update this to match your finchat CoT slug (case-sensitive)
    // The CoT should accept: $sentence (individual sentence) and $paragraph (full context)
    // Common formats: 'ai-detector', 'AI-Detector', 'ai_detector'
    COT_SLUG: 'ai-detector',  // Try 'ai-detector', 'AI-Detector', or check your finchat CoT settings
    REST_ENDPOINT: '/api/chat',  // REST API endpoint (fallback)
    
    // Model to use for analysis
    ANALYSIS_MODEL: 'gemini-2.5-flash',
    
    // Polling settings
    POLL_INTERVAL: 5000, // 5 seconds
    MAX_POLL_ATTEMPTS: 60, // 5 minutes total (60 * 5 = 300 seconds)
    
    // Alternative: Use l2m2 directly (if you have access)
    // Set to true if you want to bypass finchat API and use l2m2 directly
    USE_L2M2: false,
    L2M2_API_URL: 'http://l2m2-production',
    
    // NOTE: Backend configuration via environment variables:
    //   MCP Mode:
    //     export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/YOUR_ID/sse"
    //   
    //   REST API Mode:
    //     export FINCHAT_BASE_URL="https://your-finchat-instance.com"
    //     export FINCHAT_API_TOKEN="your_jwt_token_here"
};

// Note: For production use, consider:
// - Using a backend proxy to keep API tokens secure
// - Implementing a configuration UI to allow users to set their own credentials
// - Using environment variables with a build tool that injects them at build time
