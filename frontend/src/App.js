import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { FinChatClient } from './services/FinChatClient';

function App() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [statusText, setStatusText] = useState('Waiting for input...');
  const [currentTime, setCurrentTime] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('Checking connection...');
  const [isProcessing, setIsProcessing] = useState(false);
  const [client, setClient] = useState(null);

  // Initialize time display
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      setCurrentTime(`${hours}:${minutes}`);
    };
    
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);

  // Initialize FinChat client
  useEffect(() => {
    const initializeClient = async () => {
      try {
        const finchatClient = new FinChatClient();
        await finchatClient.initialize();
        setClient(finchatClient);
        
        if (finchatClient.isConnected()) {
          setConnectionStatus('✅ MCP Connected');
        } else {
          setConnectionStatus('⚠️ Backend Offline');
        }
      } catch (error) {
        console.error('Failed to initialize client:', error);
        setConnectionStatus('❌ Error');
      }
    };

    initializeClient();
  }, []);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setInputText(text);
      setStatusText('Text pasted. Click GO to evaluate.');
    } catch (err) {
      setStatusText('Please paste your text manually (Cmd+V / Ctrl+V)');
    }
  };

  const handleCopy = async () => {
    if (!outputText) return;
    
    try {
      await navigator.clipboard.writeText(outputText);
      setStatusText('Results copied to clipboard!');
      setTimeout(() => {
        setStatusText(outputText ? 'Evaluation complete.' : 'Waiting for input...');
      }, 2000);
    } catch (err) {
      setStatusText('Failed to copy to clipboard');
    }
  };

  const handleAnalyze = useCallback(async () => {
    const paragraph = inputText.trim();
    
    if (!paragraph) {
      setStatusText('Please enter some text first.');
      setOutputText('');
      return;
    }
    
    if (paragraph.length < 10) {
      setStatusText('Text is too short. Please provide at least 10 characters.');
      setOutputText('Text must be at least 10 characters long for accurate evaluation.');
      return;
    }
    
    setStatusText('Processing...');
    setIsProcessing(true);
    
    try {
      if (!client || !client.isConnected()) {
        setStatusText('Backend not available. Using local analysis...');
        setOutputText('⚠️ Backend not configured. Please check your connection.');
        setIsProcessing(false);
        return;
      }
      
      // Use MCP mode with polling
      setStatusText('Starting AI Detector analysis...');
      
      const result = await client.analyzeMCP('', paragraph, 'AI detection analysis', (progress, status) => {
        // Update status during polling
        if (status === 'processing') {
          setStatusText(`Analyzing... (this takes ~10 minutes, please wait)`);
        }
      });
      
      setOutputText(formatResult(result));
      setStatusText('Analysis complete (via MCP).');
    } catch (error) {
      console.error('Analysis error:', error);
      setStatusText('Analysis failed. Please try again.');
      setOutputText(`⚠️ Error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  }, [inputText, client]);

  const formatResult = (result) => {
    if (!result || result.trim().length === 0) {
      return 'No analysis result received.';
    }
    
    let output = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += 'AI DETECTION ANALYSIS\n';
    output += '(Powered by FinChat MCP)\n\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += result;
    
    return output;
  };

  return (
    <div className="container">
      <header>
        <h1 className="title">
          <span className="title-write-aid">Write Aid</span>{' '}
          <span className="title-ai-checker">AI Checker</span>
        </h1>
        <div className="status-bar">
          <span className="time">{currentTime}</span>
          <span className="status">{statusText}</span>
          <span 
            className="connection-status" 
            style={{ 
              color: connectionStatus.includes('✅') ? '#4CAF50' : 
                     connectionStatus.includes('⚠️') ? '#ff9800' : '#f44336' 
            }}
          >
            {connectionStatus}
          </span>
        </div>
      </header>

      <main className="content">
        <div className="panel left-panel">
          <div className="panel-header">
            <h2 className="panel-title">Text to Evaluate</h2>
            <div className="header-actions">
              <button className="icon-button" onClick={handlePaste} title="Paste">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 2C4 1.44772 4.44772 1 5 1H7.5C8.05228 1 8.5 1.44772 8.5 2V3H11C11.5523 3 12 3.44772 12 4V13C12 13.5523 11.5523 14 11 14H5C4.44772 14 4 13.5523 4 13V4C4 3.44772 4.44772 3 5 3H7.5V2H5V3H4V2ZM5 4V13H11V4H5ZM6 5H10V6H6V5ZM6 7H10V8H6V7ZM6 9H8V10H6V9Z" fill="currentColor"/>
                </svg>
                Paste
              </button>
              <button 
                className="go-button" 
                onClick={handleAnalyze}
                disabled={isProcessing}
              >
                GO
              </button>
            </div>
          </div>
          <div className="text-area-wrapper">
            <textarea
              className="text-input"
              placeholder="Paste your text here..."
              rows="20"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </div>
        </div>

        <div className="panel right-panel">
          <div className="panel-header">
            <h2 className="panel-title">Evaluation</h2>
            <button 
              className="icon-button" 
              onClick={handleCopy} 
              title="Copy"
              disabled={!outputText}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 4V2C4 1.44772 4.44772 1 5 1H11C11.5523 1 12 1.44772 12 2V8C12 8.55228 11.5523 9 11 9H9V11C9 11.5523 8.55228 12 8 12H2C1.44772 12 1 11.5523 1 11V5C1 4.44772 1.44772 4 2 4H4ZM5 2H11V8H9V5C9 4.44772 8.55228 4 8 4H5V2ZM2 5H8V11H2V5Z" fill="currentColor"/>
              </svg>
              Copy
            </button>
          </div>
          <div className="text-area-wrapper">
            <textarea
              className="text-output"
              placeholder="Results here..."
              rows="20"
              value={outputText}
              readOnly
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
