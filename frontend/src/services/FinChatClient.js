/**
 * FinChat MCP Client for React
 * Communicates with backend server for AI detection
 */

export class FinChatClient {
  constructor() {
    // Auto-detect backend URL based on environment
    this.backendUrl = process.env.REACT_APP_BACKEND_URL || 
      (window.location.hostname === 'localhost' 
        ? 'http://localhost:5001'
        : 'https://write-aid-mcp-production.up.railway.app'
      );
    
    this.connected = false;
    this.mcpEnabled = false;
  }

  async initialize() {
    try {
      console.log(`Attempting to connect to backend: ${this.backendUrl}`);
      
      // Check backend health
      const healthResponse = await fetch(`${this.backendUrl}/health`);
      
      if (healthResponse.ok) {
        // Check configuration
        const configResponse = await fetch(`${this.backendUrl}/api/config`);
        
        if (configResponse.ok) {
          const config = await configResponse.json();
          // Support both mcp_enabled (old) and cot_enabled (new)
          this.mcpEnabled = config.cot_enabled || config.mcp_enabled || false;
          this.connected = true;
          
          console.log('✓ FinChat client initialized');
          console.log(`  Backend URL: ${this.backendUrl}`);
          console.log(`  COT/MCP Enabled: ${this.mcpEnabled}`);
          if (config.cot_slug) {
            console.log(`  COT Slug: ${config.cot_slug}`);
          }
          
          return true;
        } else {
          console.warn(`⚠ Config endpoint returned status: ${configResponse.status}`);
        }
      } else {
        console.warn(`⚠ Health endpoint returned status: ${healthResponse.status}`);
      }
      
      console.warn('⚠ Backend is running but not properly configured');
      this.connected = false;
      return false;
    } catch (error) {
      console.error('✗ Failed to connect to backend:', error.message);
      console.error(`  Attempted URL: ${this.backendUrl}`);
      console.error(`  Error type: ${error.name}`);
      if (error.cause) {
        console.error(`  Error cause:`, error.cause);
      }
      this.connected = false;
      return false;
    }
  }

  isConnected() {
    return this.connected;
  }

  async analyzeMCP(sentence, paragraph, purpose = 'AI detection for content analysis', onProgress = null) {
    if (!this.connected) {
      throw new Error('Backend not connected. Please check your connection.');
    }

    try {
      // Step 1: Start the analysis job
      const response = await fetch(`${this.backendUrl}/api/mcp/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: paragraph || sentence,  // Use text field
          purpose: purpose
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          error: response.statusText 
        }));
        throw new Error(`Failed to start analysis: ${errorData.error || response.statusText}`);
      }

      const startData = await response.json();
      console.log('Analysis job started, response:', JSON.stringify(startData, null, 2));
      
      if (startData.error) {
        throw new Error(startData.error);
      }

      const jobId = startData.job_id;
      
      if (!jobId) {
        console.error('No job_id in start response:', startData);
        throw new Error('No job ID received from server');
      }

      console.log(`Starting to poll for job ID: ${jobId}`);
      // Step 2: Poll for results
      // Extract shouldAbort from onProgress if it's an object, otherwise use null
      const abortCheck = onProgress && typeof onProgress === 'object' && onProgress.shouldAbort 
        ? onProgress.shouldAbort 
        : null;
      const progressCallback = onProgress && typeof onProgress === 'function' 
        ? onProgress 
        : (onProgress && typeof onProgress === 'object' && onProgress.callback) 
          ? onProgress.callback 
          : null;
      return await this.pollForResult(jobId, progressCallback, abortCheck);
      
    } catch (error) {
      throw new Error(`Failed to analyze with MCP: ${error.message}`);
    }
  }

  async analyzeMCPv2(sentence, paragraph, purpose = 'Text humanization', onProgress = null) {
    if (!this.connected) {
      throw new Error('Backend not connected. Please check your connection.');
    }

    try {
      // Step 1: Start the GO2 analysis job
      const response = await fetch(`${this.backendUrl}/api/mcp/analyze-v2`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: paragraph || sentence,
          purpose: purpose
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          error: response.statusText 
        }));
        throw new Error(`Failed to start GO2 analysis: ${errorData.error || response.statusText}`);
      }

      const startData = await response.json();
      console.log('GO2 analysis job started, response:', JSON.stringify(startData, null, 2));
      
      if (startData.error) {
        throw new Error(startData.error);
      }

      const jobId = startData.job_id;
      
      if (!jobId) {
        console.error('No job_id in start response:', startData);
        throw new Error('No job ID received from server');
      }

      console.log(`Starting to poll for GO2 job ID: ${jobId}`);
      // Step 2: Poll for results (same polling logic as GO button)
      const abortCheck = onProgress && typeof onProgress === 'object' && onProgress.shouldAbort 
        ? onProgress.shouldAbort 
        : null;
      const progressCallback = onProgress && typeof onProgress === 'function' 
        ? onProgress 
        : (onProgress && typeof onProgress === 'object' && onProgress.callback) 
          ? onProgress.callback 
          : null;
      return await this.pollForResult(jobId, progressCallback, abortCheck);
      
    } catch (error) {
      throw new Error(`Failed to analyze with GO2: ${error.message}`);
    }
  }

  async pollForResult(jobId, onProgress = null, shouldAbort = null) {
    const pollInterval = 5000; // Poll every 5 seconds
    const maxAttempts = 200; // 200 * 5s = 1000s = ~16 minutes
    const requestTimeout = 10000; // 10 second timeout for each request
    const maxConsecutiveFailures = 5; // Max consecutive failures before retrying more aggressively
    let attempts = 0;
    let consecutiveFailures = 0;
    let lastSuccessfulStatus = null;
    let lastStatusTime = Date.now();

    console.log(`Starting to poll for job ${jobId}`);

    // Helper function to make a request with timeout and retry
    const fetchWithRetry = async (url, retries = 3) => {
      for (let i = 0; i < retries; i++) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), requestTimeout);
          
          const response = await fetch(url, {
            signal: controller.signal,
            headers: {
              'Cache-Control': 'no-cache',
              'Pragma': 'no-cache'
            }
          });
          
          clearTimeout(timeoutId);
          
          if (!response.ok) {
            const errorText = await response.text().catch(() => response.statusText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
          }
          
          return await response.json();
        } catch (error) {
          if (error.name === 'AbortError') {
            console.warn(`Request timeout (attempt ${i + 1}/${retries})`);
          } else {
            console.warn(`Request failed (attempt ${i + 1}/${retries}):`, error.message);
          }
          
          // If this is the last retry, throw the error
          if (i === retries - 1) {
            throw error;
          }
          
          // Wait before retry with exponential backoff
          await new Promise(resolve => setTimeout(resolve, Math.min(1000 * Math.pow(2, i), 5000)));
        }
      }
    };

    while (attempts < maxAttempts) {
      // Check if we should abort before waiting
      if (shouldAbort && shouldAbort()) {
        console.log(`Polling aborted for job ${jobId} - immediate stop`);
        throw new Error('Analysis cancelled - restart requested');
      }

      // Adjust poll interval based on consecutive failures
      // If we've had failures, poll more frequently to recover faster
      const currentPollInterval = consecutiveFailures > 0 
        ? Math.max(2000, pollInterval - (consecutiveFailures * 500)) // Faster polling after failures
        : pollInterval;

      // Wait before polling (except for first attempt)
      if (attempts > 0) {
        const chunkSize = 500; // Check every 500ms
        const chunks = Math.ceil(currentPollInterval / chunkSize);
        for (let i = 0; i < chunks; i++) {
          await new Promise(resolve => setTimeout(resolve, chunkSize));
          // Check abort during wait
          if (shouldAbort && shouldAbort()) {
            console.log(`Polling aborted for job ${jobId} during wait`);
            throw new Error('Analysis cancelled - restart requested');
          }
        }
      }
      
      // Check again after waiting
      if (shouldAbort && shouldAbort()) {
        console.log(`Polling aborted for job ${jobId} after wait`);
        throw new Error('Analysis cancelled - restart requested');
      }
      
      attempts++;

      try {
        console.log(`Poll attempt ${attempts}/${maxAttempts} for job ${jobId}${consecutiveFailures > 0 ? ` (recovering from ${consecutiveFailures} failures)` : ''}`);
        
        const status = await fetchWithRetry(`${this.backendUrl}/api/mcp/status/${jobId}`);
        
        // Reset consecutive failures on successful request
        consecutiveFailures = 0;
        lastSuccessfulStatus = status;
        lastStatusTime = Date.now();

        console.log(`Job ${jobId} status response:`, JSON.stringify(status, null, 2));
        console.log(`Job ${jobId} status:`, status.status, status.progress !== undefined ? `(${status.progress}%)` : '');

        // Check for completion FIRST before checking abort
        if (status.status === 'completed' || status.status === 'done' || status.status === 'success') {
          console.log(`Job ${jobId} completed! Result length:`, status.result ? status.result.length : 0);
          if (shouldAbort && shouldAbort()) {
            console.log(`Polling aborted for job ${jobId} but result was completed`);
            throw new Error('Analysis cancelled - restart requested');
          }
          return status.result || status.data || 'Analysis completed';
        }

        if (status.status === 'failed' || status.status === 'error') {
          console.error(`Job ${jobId} failed:`, status.error || status.message);
          throw new Error(status.error || status.message || 'Analysis failed');
        }

        // Check abort after checking completion/failure status
        if (shouldAbort && shouldAbort()) {
          console.log(`Polling aborted for job ${jobId} during status check`);
          throw new Error('Analysis cancelled - restart requested');
        }

        // Call progress callback if provided
        if (onProgress) {
          onProgress(status.progress || 0, status.status, status.status_message || '');
        }

        // Status is 'processing', continue polling
        console.log(`Job ${jobId} still processing, will check again in ${currentPollInterval/1000}s...`);
        
      } catch (error) {
        // If aborted, re-throw immediately
        if (error.message.includes('Analysis cancelled') || error.message.includes('restart requested')) {
          throw error;
        }
        
        // Don't throw on failed status (that's handled above)
        if (error.message.includes('Analysis failed')) {
          throw error;
        }
        
        // Track consecutive failures
        consecutiveFailures++;
        console.warn(`Poll attempt ${attempts} failed (${consecutiveFailures} consecutive):`, error.message);
        
        // If we've had too many consecutive failures, throw an error
        if (consecutiveFailures >= maxConsecutiveFailures) {
          console.error(`Too many consecutive failures (${consecutiveFailures}), giving up`);
          throw new Error(`Failed to get status updates after ${consecutiveFailures} attempts: ${error.message}`);
        }
        
        // If we have a last successful status and it's been a while, check if we should continue
        if (lastSuccessfulStatus && Date.now() - lastStatusTime > 60000) {
          // It's been more than a minute since last successful status
          // Check if the last status was still processing
          if (lastSuccessfulStatus.status === 'processing') {
            console.warn(`No status updates for ${Math.floor((Date.now() - lastStatusTime) / 1000)}s, but continuing...`);
          }
        }
        
        // Continue polling with shorter interval after failures
        // Don't wait the full interval if we had a failure
        if (consecutiveFailures > 0) {
          // Already waited, but reduce next wait time
          continue;
        }
      }
    }

    console.error(`Polling timed out after ${attempts} attempts for job ${jobId}`);
    throw new Error('Analysis timed out - exceeded maximum polling attempts');
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
        const errorData = await response.json().catch(() => ({ 
          error: response.statusText 
        }));
        throw new Error(`Session creation failed: ${errorData.error || response.statusText}`);
      }

      const data = await response.json();
      return data.uid;
    } catch (error) {
      throw new Error(`Failed to create session: ${error.message}`);
    }
  }

  async executeCoT(sessionUid, sentence, paragraph) {
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
        const errorData = await response.json().catch(() => ({ 
          error: response.statusText 
        }));
        throw new Error(`CoT execution failed: ${errorData.error || response.statusText}`);
      }

      const data = await response.json();
      return data.uid;
    } catch (error) {
      throw new Error(`Failed to execute CoT: ${error.message}`);
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
        const errorData = await response.json().catch(() => ({ 
          error: response.statusText 
        }));
        throw new Error(`Failed to get chat: ${errorData.error || response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to get chat: ${error.message}`);
    }
  }
}

