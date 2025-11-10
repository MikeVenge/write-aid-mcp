// DOM Elements - will be initialized when DOM is ready
let inputText, outputText, pasteButton, copyButton, goButton, statusText, currentTime;
let configButton, configModal, closeConfig, saveConfig, cancelConfig;
let configBaseUrl, configApiToken, configCotSlug, configModel, configStatus;

// Sentence Splitter - Split paragraph into sentences
class SentenceSplitter {
    constructor() {
        // Regex pattern for sentence boundaries (handles periods, exclamation, question marks)
        this.sentencePattern = /(?<=[.!?])\s+(?=[A-Z])/;
    }
    
    splitParagraph(paragraph) {
        if (!paragraph || paragraph.trim().length === 0) {
            return [];
        }
        
        // Split by sentence boundaries
        let sentences = paragraph.split(this.sentencePattern);
        
        // Clean and filter
        sentences = sentences
            .map(s => s.trim())
            .filter(s => s.length > 0);
        
        // Handle edge cases where sentence might not end properly
        if (sentences.length === 0 && paragraph.trim().length > 0) {
            // If no sentence boundaries found, treat entire paragraph as one sentence
            return [paragraph.trim()];
        }
        
        return sentences;
    }
}

// Finchat CoT Client - Uses Backend Proxy
class FinchatCoTClient {
    constructor(config) {
        // Backend proxy URL (defaults to localhost:5001)
        this.backendUrl = config.BACKEND_URL || 'http://localhost:5001';
        
        // Store original config for reference (not used for API calls)
        this.config = config;
        this.cotSlug = config.COT_SLUG || 'ai-detector';
        this.analysisModel = config.ANALYSIS_MODEL || 'gemini-2.5-flash';
        this.pollInterval = config.POLL_INTERVAL || 5000;
        this.maxPollAttempts = config.MAX_POLL_ATTEMPTS || 60;
        this.useL2M2 = config.USE_L2M2 || false;
        this.l2m2ApiUrl = config.L2M2_API_URL;
        
        // MCP configuration
        this.useMcp = config.USE_MCP || false;
        this.mcpEndpoint = config.MCP_ENDPOINT || '/api/mcp/analyze';
        
        // No need to validate tokens - backend handles that
    }
    
    async analyzeMCP(sentence, paragraph, purpose = 'AI detection for content analysis') {
        // Use MCP endpoint for analysis
        try {
            const response = await fetch(`${this.backendUrl}${this.mcpEndpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sentence: sentence,
                    paragraph: paragraph,
                    purpose: purpose
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(`MCP analysis failed: ${errorData.error || response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                return data.analysis || data.raw_content?.join('\n') || 'Analysis completed';
            } else if (data.error) {
                throw new Error(data.error);
            } else {
                return JSON.stringify(data);
            }
        } catch (error) {
            throw new Error(`Failed to analyze with MCP: ${error.message}`);
        }
    }
    
    async createSession() {
        try {
            const response = await fetch(`${this.backendUrl}/api/session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(`Session creation failed: ${errorData.error || response.statusText}`);
            }
            
            const data = await response.json();
            return data.uid;
        } catch (error) {
            throw new Error(`Failed to create session: ${error.message}`);
        }
    }
    
    async executeCoT(sessionUid, sentence, paragraph) {
        // Execute CoT for a single sentence with paragraph context
        // Backend handles parameter combinations
        
        try {
            const response = await fetch(`${this.backendUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session: sessionUid,
                    sentence: sentence,
                    paragraph: paragraph
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(`CoT execution failed: ${errorData.error || response.statusText}`);
            }
            
            const data = await response.json();
            return data.uid;
        } catch (error) {
            throw new Error(`Failed to execute CoT: ${error.message}`);
        }
    }
    
    async executeCoTSingle(sessionUid, text) {
        // Legacy method for single text analysis (backward compatibility)
        const prompt = `Analyze the following text and determine if it was written by AI or a human. Provide a detailed analysis including:
1. Verdict (AI-generated or Human-written)
2. Confidence level (0-100%)
3. Key indicators that led to this conclusion
4. Specific evidence from the text
5. Likelihood percentages for both AI and human authorship

Text to analyze:
${text}`;

        // Use l2m2 directly if configured
        if (this.useL2M2 && this.l2m2ApiUrl && this.l2m2ApiUrl !== 'http://l2m2-production') {
            return this.callL2M2(prompt);
        }
        
        // Note: If client exists, config is already validated (no placeholders)
        // So we can safely use this.baseUrl and this.cotSlug
        
        // If COT_SLUG is 'ai-detector' or similar, use it
        if (this.cotSlug && this.cotSlug.toLowerCase().includes('detector')) {
            // Try different parameter names that the CoT might expect
            const parameterNames = ['$text', '$input', '$content', '$input_text'];
            let lastError = null;
            
            for (const paramName of parameterNames) {
                const cotMessage = `/cot ${this.cotSlug} ${paramName}=${encodeURIComponent(text)}`;
                
                try {
                    const response = await fetch(`${this.baseUrl}/api/v1/chat/`, {
                        method: 'POST',
                        headers: this.headers,
                        body: JSON.stringify({
                            session: sessionUid,
                            message: cotMessage,
                            analysis_model: this.analysisModel,
                            use_web_search: this.useWebSearch
                        })
                    });
                    
                    if (!response.ok) {
                        lastError = new Error(`CoT execution failed: ${response.statusText}`);
                        continue;
                    }
                    
                    const data = await response.json();
                    return data.uid;
                } catch (error) {
                    lastError = error;
                    continue;
                }
            }
            
            // If all parameter names failed, try without parameter (some CoTs might read from context)
            if (lastError) {
                try {
                    const cotMessage = `/cot ${this.cotSlug}`;
                    const response = await fetch(`${this.baseUrl}/api/v1/chat/`, {
                        method: 'POST',
                        headers: this.headers,
                        body: JSON.stringify({
                            session: sessionUid,
                            message: cotMessage,
                            analysis_model: this.analysisModel,
                            use_web_search: this.useWebSearch
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        // Then send the text as a follow-up message
                        // This approach depends on how the CoT is structured
                        return data.uid;
                    }
                } catch (err) {
                    console.warn('CoT API call failed with all parameter attempts:', lastError);
                    throw lastError; // Re-throw to trigger fallback
                }
            }
        } else if (this.cotSlug) {
            // Use configured CoT slug (client exists, so config is valid)
            const cotMessage = `/cot ${this.cotSlug} $text=${encodeURIComponent(text)}`;
            
            try {
                const response = await fetch(`${this.baseUrl}/api/v1/chat/`, {
                    method: 'POST',
                    headers: this.headers,
                    body: JSON.stringify({
                        session: sessionUid,
                        message: cotMessage,
                        analysis_model: this.analysisModel,
                        use_web_search: this.useWebSearch
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`CoT execution failed: ${response.statusText}`);
                }
                
                const data = await response.json();
                return data.uid;
            } catch (error) {
                console.warn('CoT API call failed, trying direct prompt:', error);
                // Fall through to direct prompt
            }
        }
        
        // Fallback: Use direct prompt to finchat chat API
        try {
            const response = await fetch(`${this.baseUrl}/api/v1/chat/`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({
                    session: sessionUid,
                    message: prompt,
                    analysis_model: this.analysisModel,
                    use_web_search: this.useWebSearch
                })
            });
            
            if (!response.ok) {
                throw new Error(`Chat API failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data.uid;
        } catch (error) {
            // Last resort: try l2m2 if URL is configured
            if (this.l2m2ApiUrl && this.l2m2ApiUrl !== 'http://l2m2-production') {
                return this.callL2M2(prompt);
            }
            throw new Error(`Failed to execute analysis: ${error.message}`);
        }
    }
    
    async callL2M2(prompt) {
        const l2m2Endpoint = `${this.l2m2ApiUrl}/api/v1/completions/`;
        
        try {
            const response = await fetch(l2m2Endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cached: true,
                    context: {
                        host: 'ai-checker-web',
                        local_user: 'user',
                        property: 'ai-detection'
                    },
                    models: [{
                        model: this.analysisModel,
                        temperature: 0.1,
                        enable_web_search: this.useWebSearch
                    }],
                    messages: [{
                        role: 'user',
                        content: prompt
                    }]
                }),
                timeout: 30000
            });
            
            if (!response.ok) {
                throw new Error(`L2M2 call failed: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.errors && result.errors[0]) {
                throw new Error(`L2M2 error: ${result.errors[0]}`);
            }
            
            if (result.completions && result.completions.length > 0) {
                return result.completions[0];
            }
            
            throw new Error('No completion in L2M2 response');
        } catch (error) {
            throw new Error(`L2M2 call failed: ${error.message}`);
        }
    }
    
    async getChat(chatUid) {
        try {
            const response = await fetch(`${this.backendUrl}/api/chat/${chatUid}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(`Failed to get chat: ${errorData.error || response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to get chat: ${error.message}`);
        }
    }
    
    async waitForResult(chatUid, onProgress) {
        let attempt = 0;
        
        while (attempt < this.maxPollAttempts) {
            await new Promise(resolve => setTimeout(resolve, this.pollInterval));
            
            try {
                const chatData = await this.getChat(chatUid);
                const children = chatData.children || [];
                
                if (children.length > 0) {
                    const resultChat = children[children.length - 1];
                    const intent = resultChat.intent;
                    
                    if (intent === 'error') {
                        const error = resultChat.metadata?.error || 'Unknown error';
                        throw new Error(`CoT Error: ${error}`);
                    }
                    
                    if (intent !== 'loading') {
                        return resultChat.message || resultChat.content || 'Analysis complete.';
                    }
                }
                
                // Update progress
                if (onProgress) {
                    const metadata = chatData.metadata || {};
                    const progress = metadata.current_progress || 0;
                    const total = metadata.total_progress || 1;
                    onProgress(progress, total, attempt);
                }
            } catch (error) {
                if (error.message.includes('CoT Error')) {
                    throw error;
                }
                // Continue polling on other errors
                console.warn(`Poll attempt ${attempt + 1} failed:`, error);
            }
            
            attempt++;
        }
        
        throw new Error(`Timeout: CoT execution took longer than ${this.maxPollAttempts * this.pollInterval / 1000} seconds`);
    }
}

// Initialize client (will use defaults from config, or can be overridden)
let finchatClient = null;

async function initializeFinchatClient() {
    const statusEl = document.getElementById('connectionStatus');
    
    try {
        // Check if backend is available
        const backendUrl = (typeof FINCHAT_CONFIG !== 'undefined' && FINCHAT_CONFIG.BACKEND_URL) 
            ? FINCHAT_CONFIG.BACKEND_URL 
            : 'http://localhost:5001';
        
        if (statusEl) statusEl.textContent = 'Checking backend...';
        
        try {
            const healthResponse = await fetch(`${backendUrl}/health`, { timeout: 5000 });
            if (healthResponse.ok) {
                if (statusEl) statusEl.textContent = 'Checking MCP config...';
                
                // Check full config to see if MCP or REST API is configured
                const configResponse = await fetch(`${backendUrl}/api/config`);
                if (configResponse.ok) {
                    const configData = await configResponse.json();
                    
                    // Check if either MCP or REST API is configured
                    if (configData.mcp_enabled || configData.configured) {
                        const config = {
                            BACKEND_URL: backendUrl,
                            COT_SLUG: FINCHAT_CONFIG?.COT_SLUG || 'ai-detector',
                            ANALYSIS_MODEL: FINCHAT_CONFIG?.ANALYSIS_MODEL || 'gemini-2.5-flash',
                            POLL_INTERVAL: FINCHAT_CONFIG?.POLL_INTERVAL || 5000,
                            MAX_POLL_ATTEMPTS: FINCHAT_CONFIG?.MAX_POLL_ATTEMPTS || 60,
                            USE_MCP: FINCHAT_CONFIG?.USE_MCP || configData.mcp_enabled || false,
                            MCP_ENDPOINT: FINCHAT_CONFIG?.MCP_ENDPOINT || '/api/mcp/analyze'
                        };
                        finchatClient = new FinchatCoTClient(config);
                        
                        if (configData.mcp_enabled) {
                            console.log('✓ Finchat client initialized (MCP mode)');
                            console.log(`  Backend URL: ${backendUrl}`);
                            console.log(`  MCP Session ID: ${configData.mcp_session_id}`);
                            
                            if (statusEl) {
                                statusEl.textContent = '✅ MCP Connected';
                                statusEl.style.color = '#4CAF50';
                                statusEl.title = `Session: ${configData.mcp_session_id}`;
                            }
                        } else {
                            console.log('✓ Finchat client initialized (REST API mode)');
                            console.log(`  Backend URL: ${backendUrl}`);
                            console.log(`  CoT Slug: ${config.COT_SLUG}`);
                            
                            if (statusEl) {
                                statusEl.textContent = '✅ API Connected';
                                statusEl.style.color = '#4CAF50';
                            }
                        }
                        return;
                    }
                }
                
                // If we get here, backend is running but not configured
                console.warn('⚠ Backend is running but finchat is not configured');
                console.warn('  Set environment variables on the backend:');
                console.warn('    MCP Mode: export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/YOUR_ID/sse"');
                console.warn('    REST Mode: export FINCHAT_BASE_URL + FINCHAT_API_TOKEN');
                
                if (statusEl) {
                    statusEl.textContent = '⚠️ Not Configured';
                    statusEl.style.color = '#ff9800';
                    statusEl.title = 'Backend running but MCP/API not configured';
                }
                finchatClient = null;
                return;
            }
        } catch (backendError) {
            console.warn('⚠ Backend server not available:', backendError.message);
            console.warn('  Make sure backend_server.py is running on', backendUrl);
            console.warn('  Using local analysis as fallback');
            
            if (statusEl) {
                statusEl.textContent = '⚠️ Backend Offline';
                statusEl.style.color = '#ff9800';
                statusEl.title = `Cannot reach ${backendUrl}`;
            }
            finchatClient = null;
            return;
        }
    } catch (error) {
        console.error('✗ Finchat client initialization failed:', error.message);
        console.error('  Using local analysis as fallback');
        
        if (statusEl) {
            statusEl.textContent = '❌ Error';
            statusEl.style.color = '#f44336';
            statusEl.title = error.message;
        }
        finchatClient = null;
    }
}

// Wait for DOM to be ready before initializing everything
document.addEventListener('DOMContentLoaded', () => {
    // Load saved config from localStorage if available
    loadSavedConfig();
    
    // Initialize finchat client after DOM is ready (ensures config is loaded)
    // Note: initializeFinchatClient is now async, so we await it
    (async () => {
        await initializeFinchatClient();
    })();
    
    // Initialize DOM elements
    inputText = document.getElementById('inputText');
    outputText = document.getElementById('outputText');
    pasteButton = document.getElementById('pasteButton');
    copyButton = document.getElementById('copyButton');
    goButton = document.getElementById('goButton');
    statusText = document.getElementById('statusText');
    currentTime = document.getElementById('currentTime');
    
    // Configuration modal elements
    configButton = document.getElementById('configButton');
    configModal = document.getElementById('configModal');
    closeConfig = document.getElementById('closeConfig');
    saveConfig = document.getElementById('saveConfig');
    cancelConfig = document.getElementById('cancelConfig');
    configBaseUrl = document.getElementById('configBaseUrl');
    configApiToken = document.getElementById('configApiToken');
    configCotSlug = document.getElementById('configCotSlug');
    configModel = document.getElementById('configModel');
    configStatus = document.getElementById('configStatus');
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Update time display
    updateTime();
    setInterval(updateTime, 60000); // Update every minute
});

// Update time display
function updateTime() {
    if (currentTime) {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        currentTime.textContent = `${hours}:${minutes}`;
    }
}

// Initialize all event listeners
function initializeEventListeners() {
    if (!inputText || !outputText || !pasteButton || !copyButton || !goButton || !statusText) {
        console.error('Some DOM elements are missing');
        return;
    }

    // Paste functionality
    pasteButton.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            inputText.value = text;
            inputText.focus();
            statusText.textContent = 'Text pasted. Click GO to evaluate.';
        } catch (err) {
            // Fallback: select all and let user paste manually
            inputText.focus();
            inputText.select();
            statusText.textContent = 'Please paste your text manually (Cmd+V / Ctrl+V)';
        }
    });

    // Copy functionality
    copyButton.addEventListener('click', async () => {
        const text = outputText.value;
        if (!text) return;
        
        try {
            await navigator.clipboard.writeText(text);
            statusText.textContent = 'Results copied to clipboard!';
            setTimeout(() => {
                if (outputText.value) {
                    statusText.textContent = 'Evaluation complete.';
                } else {
                    statusText.textContent = 'Waiting for input...';
                }
            }, 2000);
        } catch (err) {
            // Fallback
            outputText.select();
            document.execCommand('copy');
            statusText.textContent = 'Results copied!';
        }
    });

    // Scroll buttons
    document.querySelectorAll('.scroll-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const textarea = e.target.closest('.panel').querySelector('textarea');
        
        if (e.target.closest('.scroll-btn').classList.contains('scroll-up')) {
            textarea.scrollTop -= 50;
        } else {
            textarea.scrollTop += 50;
        }
    });
});

// AI Detection Algorithm
function evaluateText(text) {
    if (!text || text.trim().length === 0) {
        return {
            error: 'Please enter some text to evaluate.'
        };
    }

    // Basic metrics
    const words = text.split(/\s+/).filter(w => w.length > 0);
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const characters = text.length;
    const wordCount = words.length;
    const sentenceCount = sentences.length;
    
    if (wordCount < 10) {
        return {
            error: 'Text is too short. Please provide at least 10 words for accurate evaluation.'
        };
    }

    // Calculate features
    const avgWordsPerSentence = wordCount / sentenceCount;
    const avgWordLength = words.reduce((sum, w) => sum + w.length, 0) / wordCount;
    
    // Sentence length variance (humans have more variation)
    const sentenceLengths = sentences.map(s => s.trim().split(/\s+/).length);
    const sentenceVariance = calculateVariance(sentenceLengths);
    
    // Word repetition (AI tends to repeat words more)
    const wordFrequency = {};
    words.forEach(word => {
        const normalized = word.toLowerCase().replace(/[^\w]/g, '');
        wordFrequency[normalized] = (wordFrequency[normalized] || 0) + 1;
    });
    const uniqueWords = Object.keys(wordFrequency).length;
    const repetitionScore = 1 - (uniqueWords / wordCount); // Higher = more repetition
    
    // Transitional phrases (humans use more varied transitions)
    const transitions = ['however', 'therefore', 'moreover', 'furthermore', 'nevertheless', 
                         'consequently', 'additionally', 'similarly', 'conversely', 'indeed'];
    const transitionCount = transitions.reduce((count, transition) => {
        const regex = new RegExp(`\\b${transition}\\b`, 'gi');
        return count + (text.match(regex) || []).length;
    }, 0);
    
    // Punctuation patterns
    const exclamationCount = (text.match(/!/g) || []).length;
    const questionCount = (text.match(/\?/g) || []).length;
    const punctuationVariety = exclamationCount + questionCount;
    
    // Paragraph breaks (humans use more paragraph breaks)
    const paragraphBreaks = (text.match(/\n\n+/g) || []).length;
    
    // Perplexity-like measure: sentence complexity
    const complexSentences = sentences.filter(s => {
        const words = s.trim().split(/\s+/);
        return words.length > 20 || (s.match(/,/g) || []).length > 2;
    }).length;
    const complexityRatio = complexSentences / sentenceCount;
    
    // Calculate scores
    let aiScore = 0;
    let humanScore = 0;
    
    // Lower sentence variance suggests AI (humans vary more)
    if (sentenceVariance < 20) aiScore += 15;
    else if (sentenceVariance > 40) humanScore += 15;
    
    // Higher repetition suggests AI
    if (repetitionScore > 0.4) aiScore += 20;
    else if (repetitionScore < 0.25) humanScore += 15;
    
    // Very consistent sentence length suggests AI
    if (avgWordsPerSentence > 15 && avgWordsPerSentence < 25 && sentenceVariance < 15) {
        aiScore += 10;
    } else if (sentenceVariance > 30) {
        humanScore += 10;
    }
    
    // Few transitions might suggest AI (though not always)
    if (transitionCount === 0 && sentenceCount > 5) aiScore += 5;
    else if (transitionCount > sentenceCount * 0.1) humanScore += 10;
    
    // Low punctuation variety suggests AI
    if (punctuationVariety === 0 && sentenceCount > 3) aiScore += 5;
    else if (punctuationVariety > 2) humanScore += 8;
    
    // Few paragraph breaks might suggest AI
    if (paragraphBreaks === 0 && wordCount > 100) aiScore += 5;
    else if (paragraphBreaks > 2) humanScore += 10;
    
    // Very high complexity ratio might suggest AI (overly complex)
    if (complexityRatio > 0.8) aiScore += 10;
    else if (complexityRatio < 0.5) humanScore += 10;
    
    // Average word length (very consistent might suggest AI)
    const wordLengthVariance = calculateVariance(words.map(w => w.length));
    if (wordLengthVariance < 2) aiScore += 5;
    
    // Final confidence calculation
    const totalScore = aiScore + humanScore;
    const aiProbability = totalScore > 0 ? (aiScore / totalScore) * 100 : 50;
    const humanProbability = 100 - aiProbability;
    
    // Determine result
    const isLikelyAI = aiProbability > 55;
    const confidence = Math.max(aiProbability, humanProbability);
    
    return {
        isAI: isLikelyAI,
        aiProbability: aiProbability.toFixed(1),
        humanProbability: humanProbability.toFixed(1),
        confidence: confidence.toFixed(1),
        wordCount,
        sentenceCount,
        avgWordsPerSentence: avgWordsPerSentence.toFixed(1),
        metrics: {
            sentenceVariance: sentenceVariance.toFixed(2),
            repetitionScore: (repetitionScore * 100).toFixed(1) + '%',
            transitionCount,
            punctuationVariety,
            paragraphBreaks,
            complexityRatio: (complexityRatio * 100).toFixed(1) + '%'
        }
    };
}

function calculateVariance(values) {
    if (values.length === 0) return 0;
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const squaredDiffs = values.map(value => Math.pow(value - mean, 2));
    return squaredDiffs.reduce((a, b) => a + b, 0) / values.length;
}

function formatResults(result) {
    if (result.error) {
        return result.error;
    }
    
    const verdict = result.isAI ? 'LIKELY AI-GENERATED' : 'LIKELY HUMAN-WRITTEN';
    const verdictColor = result.isAI ? '🔴' : '🟢';
    
    let output = `${verdictColor} VERDICT: ${verdict}\n\n`;
    output += `Confidence: ${result.confidence}%\n`;
    output += `AI Probability: ${result.aiProbability}%\n`;
    output += `Human Probability: ${result.humanProbability}%\n\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
    output += `TEXT ANALYSIS\n\n`;
    output += `Word Count: ${result.wordCount}\n`;
    output += `Sentence Count: ${result.sentenceCount}\n`;
    output += `Avg Words per Sentence: ${result.metrics.avgWordsPerSentence}\n\n`;
    output += `DETAILED METRICS\n\n`;
    output += `• Sentence Length Variance: ${result.metrics.sentenceVariance}\n`;
    output += `• Word Repetition: ${result.metrics.repetitionScore}\n`;
    output += `• Transition Phrases: ${result.metrics.transitionCount}\n`;
    output += `• Punctuation Variety: ${result.metrics.punctuationVariety}\n`;
    output += `• Paragraph Breaks: ${result.metrics.paragraphBreaks}\n`;
    output += `• Complexity Ratio: ${result.metrics.complexityRatio}\n\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
    output += `Note: This is a local heuristic-based analysis.`;
    
    return output;
}

function formatFinchatResults(resultText) {
    // Format the result from finchat CoT
    // The result should already be formatted by the CoT, but we can enhance it
    if (!resultText || resultText.trim().length === 0) {
        return 'No analysis result received from finchat.';
    }
    
    // If the result is already well-formatted, return as-is
    // Otherwise, add a header
    if (resultText.includes('VERDICT') || resultText.includes('verdict') || 
        resultText.includes('AI') || resultText.includes('Human')) {
        return resultText;
    }
    
    // Add formatting if needed
    let output = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += 'AI DETECTION ANALYSIS\n';
    output += '(Powered by finchat CoT)\n\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += resultText;
    
    return output;
}

function formatAggregatedResults(results, totalSentences) {
    // Format aggregated results from sentence-by-sentence analysis
    let output = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += 'AI DETECTION ANALYSIS\n';
    output += `(Sentence-by-Sentence Analysis - ${totalSentences} sentence(s))\n\n`;
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    
    if (results.length === 0) {
        output += 'No results available.\n';
        return output;
    }
    
    // Format each sentence result
    for (const item of results) {
        output += `\n[Sentence ${item.sentenceIndex}/${totalSentences}]\n`;
        output += `"${item.sentence.substring(0, 100)}${item.sentence.length > 100 ? '...' : ''}"\n\n`;
        
        if (item.error) {
            output += `⚠️ Error: ${item.result}\n\n`;
        } else {
            output += `${item.result}\n\n`;
        }
        
        output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    }
    
    // Summary
    const successful = results.filter(r => !r.error).length;
    const failed = results.filter(r => r.error).length;
    
    output += '\nSUMMARY\n';
    output += `Total Sentences: ${totalSentences}\n`;
    output += `Successfully Analyzed: ${successful}\n`;
    if (failed > 0) {
        output += `Failed: ${failed}\n`;
    }
    
    return output;
}

    // GO button functionality - Process sentence-by-sentence like Write Aid
    goButton.addEventListener('click', async () => {
        const paragraph = inputText.value.trim();
        
        if (!paragraph) {
            statusText.textContent = 'Please enter some text first.';
            outputText.value = '';
            copyButton.disabled = true;
            return;
        }
        
        // Validate text length
        if (paragraph.length < 10) {
            statusText.textContent = 'Text is too short. Please provide at least 10 characters.';
            outputText.value = 'Text must be at least 10 characters long for accurate evaluation.';
            copyButton.disabled = false;
            return;
        }
        
        statusText.textContent = 'Processing...';
        copyButton.disabled = true;
        goButton.disabled = true;
        
        try {
            // Check if finchat client is available
            if (!finchatClient) {
                // Check if config exists but has placeholders
                let configMessage = 'Finchat not configured.';
                if (typeof FINCHAT_CONFIG !== 'undefined') {
                    const hasPlaceholders = FINCHAT_CONFIG.BASE_URL === 'https://your-finchat-instance.com' ||
                                           FINCHAT_CONFIG.API_TOKEN === 'your_jwt_token_here';
                    if (hasPlaceholders) {
                        configMessage = 'Finchat not configured - please update ai_checker_config.js with your BASE_URL and API_TOKEN';
                    }
                }
                
                // Fallback to local heuristic-based analysis
                statusText.textContent = configMessage;
                outputText.value = `⚠️ ${configMessage}\n\n` +
                                 `Using local analysis as fallback.\n\n` +
                                 `To enable finchat:\n` +
                                 `1. Open ai_checker_config.js\n` +
                                 `2. Set BASE_URL to your finchat instance URL\n` +
                                 `3. Set API_TOKEN to your JWT token\n` +
                                 `4. Refresh this page\n\n` +
                                 `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
                
                setTimeout(() => {
                    const result = evaluateText(paragraph);
                    const formatted = formatResults(result);
                    outputText.value = outputText.value + formatted;
                    copyButton.disabled = false;
                    goButton.disabled = false;
                    
                    if (result.error) {
                        statusText.textContent = result.error;
                    } else {
                        statusText.textContent = 'Evaluation complete (local analysis).';
                    }
                }, 500);
                return;
            }
            
            // Check if using MCP mode
            if (finchatClient.useMcp) {
                // MCP mode: analyze full text with ai_detector tool
                statusText.textContent = 'Analyzing with AI Detector (MCP)... This may take ~10 minutes.';
                
                try {
                    const result = await finchatClient.analyzeMCP('', paragraph, 'AI detection analysis');
                    
                    outputText.value = formatFinchatResults(result);
                    copyButton.disabled = false;
                    goButton.disabled = false;
                    statusText.textContent = 'Analysis complete (via MCP).';
                } catch (error) {
                    console.error('MCP analysis error:', error);
                    // Fall back to local analysis
                    const localResult = evaluateText(paragraph);
                    const formatted = formatResults(localResult);
                    outputText.value = `⚠️ MCP analysis failed: ${error.message}\n\nUsing local fallback:\n\n${formatted}`;
                    copyButton.disabled = false;
                    goButton.disabled = false;
                    statusText.textContent = 'Analysis complete (local fallback).';
                }
                return;
            }
            
            // REST API mode: sentence-by-sentence analysis
            // Split paragraph into sentences
            const splitter = new SentenceSplitter();
            const sentences = splitter.splitParagraph(paragraph);
            
            if (sentences.length === 0) {
                outputText.value = 'No sentences found in the text.';
                copyButton.disabled = false;
                goButton.disabled = false;
                statusText.textContent = 'No sentences detected.';
                return;
            }
            
            statusText.textContent = `Found ${sentences.length} sentence(s). Analyzing...`;
            
            // Process each sentence with paragraph context
            const results = [];
            
            for (let i = 0; i < sentences.length; i++) {
                const sentence = sentences[i];
                const sentenceNum = i + 1;
                
                statusText.textContent = `Analyzing sentence ${sentenceNum}/${sentences.length}...`;
                
                try {
                    // Create session for this sentence
                    const sessionUid = await finchatClient.createSession();
                    
                    // Execute CoT with sentence and paragraph context
                    const chatUid = await finchatClient.executeCoT(sessionUid, sentence, paragraph);
                    
                    // Wait for result
                    const result = await finchatClient.waitForResult(chatUid, (progress, total, attempt) => {
                        statusText.textContent = `Sentence ${sentenceNum}/${sentences.length}: Step ${progress}/${total}...`;
                    });
                    
                    results.push({
                        sentenceIndex: sentenceNum,
                        sentence: sentence,
                        result: result
                    });
                    
                    // Update output with progress
                    outputText.value = formatAggregatedResults(results, sentences.length);
                    
                } catch (error) {
                    console.error(`Error processing sentence ${sentenceNum}:`, error);
                    results.push({
                        sentenceIndex: sentenceNum,
                        sentence: sentence,
                        result: `Error: ${error.message}`,
                        error: true
                    });
                    // Continue with next sentence
                }
            }
            
            // Final aggregated results
            outputText.value = formatAggregatedResults(results, sentences.length);
            copyButton.disabled = false;
            goButton.disabled = false;
            statusText.textContent = `Analysis complete. Processed ${sentences.length} sentence(s).`;
            
        } catch (error) {
            console.error('Evaluation error:', error);
            
            // Fallback to local analysis on error
            statusText.textContent = 'Finchat error. Using local analysis...';
            try {
                const result = evaluateText(paragraph);
                const formatted = formatResults(result);
                outputText.value = `⚠️ Note: Finchat API unavailable. Using local analysis.\n\n${formatted}\n\nError: ${error.message}`;
                copyButton.disabled = false;
                goButton.disabled = false;
                statusText.textContent = 'Evaluation complete (local fallback).';
            } catch (fallbackError) {
                outputText.value = `Error: ${error.message}\n\nFallback analysis also failed: ${fallbackError.message}`;
                copyButton.disabled = false;
                goButton.disabled = false;
                statusText.textContent = 'Evaluation failed.';
            }
        }
    });

    // Allow Enter key to trigger evaluation (Ctrl/Cmd + Enter)
    inputText.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            goButton.click();
        }
    });

    // Enable copy button when there's output
    outputText.addEventListener('input', () => {
        copyButton.disabled = !outputText.value.trim();
    });
    
    // Configuration modal handlers
    if (configButton) {
        configButton.addEventListener('click', () => {
            // Populate form with current config (from file or localStorage)
            if (typeof FINCHAT_CONFIG !== 'undefined') {
                configBaseUrl.value = FINCHAT_CONFIG.BASE_URL || '';
                configApiToken.value = FINCHAT_CONFIG.API_TOKEN || '';
                configCotSlug.value = FINCHAT_CONFIG.COT_SLUG || 'ai-detector';
                configModel.value = FINCHAT_CONFIG.ANALYSIS_MODEL || 'gemini-2.5-flash';
            }
            
            // Try to load from localStorage
            const saved = getSavedConfig();
            if (saved) {
                configBaseUrl.value = saved.BASE_URL || configBaseUrl.value;
                configApiToken.value = saved.API_TOKEN || configApiToken.value;
                configCotSlug.value = saved.COT_SLUG || configCotSlug.value;
                configModel.value = saved.ANALYSIS_MODEL || configModel.value;
            }
            
            configModal.style.display = 'block';
            configStatus.textContent = '';
            configStatus.className = 'config-status';
        });
    }
    
    if (closeConfig) {
        closeConfig.addEventListener('click', () => {
            configModal.style.display = 'none';
        });
    }
    
    if (cancelConfig) {
        cancelConfig.addEventListener('click', () => {
            configModal.style.display = 'none';
        });
    }
    
    if (saveConfig) {
        saveConfig.addEventListener('click', () => {
            const baseUrl = configBaseUrl.value.trim();
            const apiToken = configApiToken.value.trim();
            const cotSlug = configCotSlug.value.trim() || 'ai-detector';
            const model = configModel.value.trim() || 'gemini-2.5-flash';
            
            if (!baseUrl || !apiToken) {
                configStatus.textContent = 'Please fill in Base URL and API Token';
                configStatus.className = 'config-status error';
                return;
            }
            
            // Save to localStorage
            const config = {
                BASE_URL: baseUrl,
                API_TOKEN: apiToken,
                COT_SLUG: cotSlug,
                ANALYSIS_MODEL: model,
                USE_WEB_SEARCH: true,
                POLL_INTERVAL: 5000,
                MAX_POLL_ATTEMPTS: 60,
                USE_L2M2: false,
                L2M2_API_URL: 'http://l2m2-production'
            };
            
            localStorage.setItem('finchat_config', JSON.stringify(config));
            
            configStatus.textContent = 'Configuration saved! Refreshing page...';
            configStatus.className = 'config-status success';
            
            // Reload page to apply new config
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }
    
    // Close modal when clicking outside
    if (configModal) {
        window.addEventListener('click', (event) => {
            if (event.target === configModal) {
                configModal.style.display = 'none';
            }
        });
    }
}

// Load saved config from localStorage
function loadSavedConfig() {
    const saved = getSavedConfig();
    if (saved && typeof FINCHAT_CONFIG !== 'undefined') {
        // Override FINCHAT_CONFIG with saved values
        Object.assign(FINCHAT_CONFIG, saved);
    }
}

// Get saved config from localStorage
function getSavedConfig() {
    try {
        const saved = localStorage.getItem('finchat_config');
        if (saved) {
            return JSON.parse(saved);
        }
    } catch (error) {
        console.warn('Failed to load saved config:', error);
    }
    return null;
}
