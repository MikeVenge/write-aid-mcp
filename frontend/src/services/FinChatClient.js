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
      // Check backend health
      const healthResponse = await fetch(`${this.backendUrl}/health`, {
        timeout: 5000
      });
      
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
        }
      }
      
      console.warn('⚠ Backend is running but not properly configured');
      this.connected = false;
      return false;
    } catch (error) {
      console.error('✗ Failed to connect to backend:', error.message);
      this.connected = false;
      return false;
    }
  }

  isConnected() {
    return this.connected;
  }

  async analyzeMCP(sentence, paragraph, purpose = 'AI detection for content analysis') {
    if (!this.connected) {
      throw new Error('Backend not connected. Please check your connection.');
    }

    try {
      const response = await fetch(`${this.backendUrl}/api/mcp/analyze`, {
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
        const errorData = await response.json().catch(() => ({ 
          error: response.statusText 
        }));
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

