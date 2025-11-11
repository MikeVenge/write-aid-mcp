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
          this.mcpEnabled = config.mcp_enabled || false;
          this.connected = true;
          
          console.log('✓ FinChat client initialized');
          console.log(`  Backend URL: ${this.backendUrl}`);
          console.log(`  MCP Enabled: ${this.mcpEnabled}`);
          
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
      
      if (startData.error) {
        throw new Error(startData.error);
      }

      const jobId = startData.job_id;
      
      if (!jobId) {
        throw new Error('No job ID received from server');
      }

      // Step 2: Poll for results
      return await this.pollForResult(jobId, onProgress);
      
    } catch (error) {
      throw new Error(`Failed to analyze with MCP: ${error.message}`);
    }
  }

  async pollForResult(jobId, onProgress = null) {
    const pollInterval = 5000; // Poll every 5 seconds
    const maxAttempts = 200; // 200 * 5s = 1000s = ~16 minutes
    let attempts = 0;

    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, pollInterval));
      attempts++;

      try {
        const response = await fetch(`${this.backendUrl}/api/mcp/status/${jobId}`);
        
        if (!response.ok) {
          throw new Error(`Status check failed: ${response.statusText}`);
        }

        const status = await response.json();

        // Call progress callback if provided
        if (onProgress) {
          onProgress(status.progress || 0, status.status);
        }

        if (status.status === 'completed') {
          return status.result || 'Analysis completed';
        }

        if (status.status === 'failed') {
          throw new Error(status.error || 'Analysis failed');
        }

        // Status is 'processing', continue polling
        
      } catch (error) {
        console.warn(`Poll attempt ${attempts} failed:`, error);
        // Continue polling even on error
      }
    }

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

