import React, { useState, useEffect, useCallback, useRef } from 'react';
import './App.css';
import { FinChatClient } from './services/FinChatClient';

function App() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [client, setClient] = useState(null);
  const timerIntervalRef = useRef(null);

  // Initialize FinChat client
  useEffect(() => {
    const initializeClient = async () => {
      try {
        const finchatClient = new FinChatClient();
        await finchatClient.initialize();
        setClient(finchatClient);
      } catch (error) {
        console.error('Failed to initialize client:', error);
      }
    };

    initializeClient();
  }, []);

  // Timer effect - updates elapsed time when processing
  useEffect(() => {
    if (isProcessing) {
      // Start timer
      setElapsedTime(0);
      timerIntervalRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      // Stop timer
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
    }

    // Cleanup on unmount
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    };
  }, [isProcessing]);

  // Format elapsed time as MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setInputText(text);
    } catch (err) {
      // Failed to paste
    }
  };

  const handleCopy = async () => {
    if (!outputText) return;
    
    try {
      await navigator.clipboard.writeText(outputText);
    } catch (err) {
      // Failed to copy
    }
  };

  const handleAnalyze = useCallback(async () => {
    const paragraph = inputText.trim();
    
    if (!paragraph) {
      setOutputText('');
      return;
    }
    
    if (paragraph.length < 10) {
      setOutputText('Text must be at least 10 characters long for accurate evaluation.');
      return;
    }
    
    setIsProcessing(true);
    
    try {
      if (!client || !client.isConnected()) {
        setOutputText('⚠️ Backend not configured. Please check your connection.');
        setIsProcessing(false);
        return;
      }
      
      // Use MCP mode with polling
      const result = await client.analyzeMCP('', paragraph, 'AI detection analysis', (progress, status) => {
        // Progress callback for polling updates
      });
      
      setOutputText(formatResult(result));
    } catch (error) {
      console.error('Analysis error:', error);
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
        {isProcessing && (
          <div className="timer-display">
            <span className="timer-label">Analysis Time:</span>
            <span className="timer-value">{formatTime(elapsedTime)}</span>
          </div>
        )}
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
