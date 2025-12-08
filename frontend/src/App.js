import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';
import { FinChatClient } from './services/FinChatClient';

function App() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  const [progressPercent, setProgressPercent] = useState(0);
  const [isMCPConnected, setIsMCPConnected] = useState(false);
  const [showWarning, setShowWarning] = useState(false);
  const [showSameTextWarning, setShowSameTextWarning] = useState(false);
  const [client, setClient] = useState(null);
  const [analysisType, setAnalysisType] = useState('GO'); // 'GO' or 'GO2'
  const timerIntervalRef = useRef(null);
  const analysisStartTimeRef = useRef(null); // Store start timestamp instead of counting
  const lastAnalyzedTextRef = useRef('');
  const analysisAbortRef = useRef(false);
  const currentAnalysisPromiseRef = useRef(null);

  // Initialize FinChat client
  useEffect(() => {
    const initializeClient = async () => {
      try {
        const finchatClient = new FinChatClient();
        await finchatClient.initialize();
        setClient(finchatClient);
        setIsMCPConnected(finchatClient.isConnected());
      } catch (error) {
        console.error('Failed to initialize client:', error);
        setIsMCPConnected(false);
      }
    };

    initializeClient();
  }, []);

  // Timer effect - updates elapsed time when processing
  // Uses actual timestamp difference instead of counting to work when tab is in background
  useEffect(() => {
    if (isProcessing) {
      // Store start time
      analysisStartTimeRef.current = Date.now();
      setElapsedTime(0);
      
      // Update timer based on actual elapsed time (not counting)
      timerIntervalRef.current = setInterval(() => {
        if (analysisStartTimeRef.current) {
          const elapsed = Math.floor((Date.now() - analysisStartTimeRef.current) / 1000);
          setElapsedTime(elapsed);
        }
      }, 100); // Update every 100ms for smooth display, but calculate from actual time
    } else {
      // Stop timer
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
      analysisStartTimeRef.current = null;
    }

    // Cleanup on unmount
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
      analysisStartTimeRef.current = null;
    };
  }, [isProcessing]);

  // Restart analysis if input text changes while processing
  useEffect(() => {
    // Only restart if currently processing and text has changed from what was analyzed
    if (isProcessing && inputText.trim() !== lastAnalyzedTextRef.current && inputText.trim().length > 0) {
      const wordCount = countWords(inputText.trim());
      // Only restart if new text meets minimum word requirement
      if (wordCount >= 250) {
        // Debounce: wait 1 second after user stops typing before restarting
        const debounceTimer = setTimeout(() => {
          // Double-check conditions haven't changed
          const currentText = inputText.trim();
          if (isProcessing && currentText !== lastAnalyzedTextRef.current && currentText.length > 0) {
            const currentWordCount = countWords(currentText);
            if (currentWordCount >= 250) {
              // Clear output and restart analysis
              setOutputText('');
              analysisAbortRef.current = true;
              // Small delay to ensure state updates, then restart
              setTimeout(() => {
                analysisAbortRef.current = false;
                handleAnalyze();
              }, 100);
            }
          }
        }, 1000); // 1 second debounce
        
        return () => clearTimeout(debounceTimer);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inputText, isProcessing]);

  // Format elapsed time as MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Count words in text
  const countWords = (text) => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  };

  // Play bell sound 3 times - MAXIMUM VOLUME
  const playBellSound = async () => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      // Resume audio context if suspended (required by some browsers)
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }

      // Create a bell-like sound using oscillators - MAXIMUM VOLUME
      const playBell = (delay) => {
        setTimeout(() => {
          const oscillator = audioContext.createOscillator();
          const gainNode = audioContext.createGain();
          
          oscillator.connect(gainNode);
          gainNode.connect(audioContext.destination);
          
          // Bell-like frequency (starts high, decays to lower)
          oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
          oscillator.frequency.exponentialRampToValueAtTime(400, audioContext.currentTime + 0.3);
          
          // Envelope for bell-like decay - MAXIMUM VOLUME (gain 1.0 = 100%)
          gainNode.gain.setValueAtTime(0, audioContext.currentTime);
          gainNode.gain.linearRampToValueAtTime(1.0, audioContext.currentTime + 0.01); // Peak at maximum volume
          gainNode.gain.exponentialRampToValueAtTime(0.1, audioContext.currentTime + 0.6); // Longer decay, louder sustain
          
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.6); // Longer duration for more impact
        }, delay);
      };

      // Play bell 3 times with delays
      playBell(0);      // First bell immediately
      playBell(300);    // Second bell after 300ms
      playBell(600);    // Third bell after 600ms
    } catch (error) {
      console.warn('Could not play bell sound:', error);
    }
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

  const handleReset = () => {
    setInputText('');
    setOutputText('');
    setProgressStatus('');
    setProgressPercent(0);
    setShowWarning(false);
    setShowSameTextWarning(false);
  };

  const handleAnalyze = useCallback(async () => {
    const paragraph = inputText.trim();
    
    if (!paragraph) {
      setOutputText('');
      return;
    }
    
    // Check for minimum 250 words
    const wordCount = countWords(paragraph);
    if (wordCount < 250) {
      setShowWarning(true);
      return;
    }
    
    // Store whether we were already processing (before state changes)
    const wasProcessing = isProcessing;
    
    // Check if text hasn't changed from last analysis (only if analysis is running)
    // If text has changed, proceed with new analysis regardless
    // Only check if we have a previous analysis to compare against
    if (wasProcessing && lastAnalyzedTextRef.current && paragraph === lastAnalyzedTextRef.current) {
      setShowSameTextWarning(true);
      return;
    }
    
    // If analysis is already running, abort it immediately
    if (wasProcessing) {
      console.log('Aborting current analysis to start new one');
      analysisAbortRef.current = true;
      setOutputText(''); // Clear output immediately
      
      // Cancel the current analysis promise if it exists
      if (currentAnalysisPromiseRef.current) {
        // The promise will be rejected when abort is detected in polling
        currentAnalysisPromiseRef.current = null;
      }
      
      // Reset timer immediately
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
      analysisStartTimeRef.current = null;
      setElapsedTime(0);
    }
    
    // Update the last analyzed text reference
    lastAnalyzedTextRef.current = paragraph;
    
      // Reset abort flag BEFORE starting new analysis
      analysisAbortRef.current = false;
      setOutputText(''); // Clear output when starting new analysis
      setProgressStatus('Initializing...');
      setProgressPercent(0);
      setAnalysisType('GO'); // Mark as GO analysis
      
      // Reset timer - will be set by useEffect when isProcessing becomes true
      analysisStartTimeRef.current = null;
      setElapsedTime(0);
      
      // Set processing state
      setIsProcessing(true);
    
    // Timer will be automatically started by useEffect when isProcessing becomes true
    
    try {
      if (!client || !client.isConnected()) {
        setOutputText('⚠️ Backend not configured. Please check your connection.');
        setIsProcessing(false);
        return;
      }
      
      // Use MCP mode with polling
      // Pass abort check function so polling can be cancelled
      const analysisPromise = client.analyzeMCP('', paragraph, 'AI detection analysis', {
        callback: (progress, status, statusMessage) => {
          // Progress callback for polling updates
          setProgressPercent(progress || 0);
          setProgressStatus(statusMessage || status || 'Processing...');
        },
        shouldAbort: () => analysisAbortRef.current
      });
      
      // Store the promise reference so we can track it
      currentAnalysisPromiseRef.current = analysisPromise;
      
      const result = await analysisPromise;
      
      // Clear the promise reference after completion
      currentAnalysisPromiseRef.current = null;
      
      // Only set result if analysis wasn't aborted
      if (!analysisAbortRef.current) {
        setOutputText(formatResult(result, 'GO'));
        setProgressStatus('Completed');
        setProgressPercent(100);
        
        // Play bell sound 3 times when analysis completes
        playBellSound();
      }
    } catch (error) {
      // Clear the promise reference on error
      currentAnalysisPromiseRef.current = null;
      
      // Don't show error if analysis was intentionally aborted
      if (!analysisAbortRef.current && 
          !error.message.includes('Analysis cancelled') && 
          !error.message.includes('restart requested')) {
        console.error('Analysis error:', error);
        setOutputText(`⚠️ Error: ${error.message}`);
      } else {
        // Silently ignore aborted analyses
        console.log('Analysis aborted:', error.message);
      }
    } finally {
      // Only reset processing state if not aborted (new analysis will set it)
      if (!analysisAbortRef.current) {
        setIsProcessing(false);
        // Keep progress status visible even after completion
      }
    }
  }, [inputText, client, isProcessing]);

  const handleAnalyzeGO2 = useCallback(async () => {
    const paragraph = inputText.trim();
    
    if (!paragraph) {
      setOutputText('');
      return;
    }
    
    // Check for minimum 250 words
    const wordCount = countWords(paragraph);
    if (wordCount < 250) {
      setShowWarning(true);
      return;
    }
    
    // Store whether we were already processing (before state changes)
    const wasProcessing = isProcessing;
    
    // Check if text hasn't changed from last analysis (only if analysis is running)
    if (wasProcessing && lastAnalyzedTextRef.current && paragraph === lastAnalyzedTextRef.current) {
      setShowSameTextWarning(true);
      return;
    }
    
    // If analysis is already running, abort it immediately
    if (wasProcessing) {
      console.log('Aborting current analysis to start new GO2 analysis');
      analysisAbortRef.current = true;
      setOutputText('');
      
      if (currentAnalysisPromiseRef.current) {
        currentAnalysisPromiseRef.current = null;
      }
      
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
      analysisStartTimeRef.current = null;
      setElapsedTime(0);
    }
    
    // Update the last analyzed text reference
    lastAnalyzedTextRef.current = paragraph;
    
    // Reset abort flag BEFORE starting new analysis
    analysisAbortRef.current = false;
    setOutputText('');
    setProgressStatus('Initializing GO2...');
    setProgressPercent(0);
    setAnalysisType('GO2'); // Mark as GO2 analysis
    
    // Reset timer
    analysisStartTimeRef.current = null;
    setElapsedTime(0);
    
    // Set processing state
    setIsProcessing(true);
    
    try {
      if (!client || !client.isConnected()) {
        setOutputText('⚠️ Backend not configured. Please check your connection.');
        setIsProcessing(false);
        return;
      }
      
      // Use GO2 (v2) mode with polling
      const analysisPromise = client.analyzeMCPv2('', paragraph, 'Text humanization', {
        callback: (progress, status, statusMessage) => {
          setProgressPercent(progress || 0);
          setProgressStatus(statusMessage || status || 'Processing...');
        },
        shouldAbort: () => analysisAbortRef.current
      });
      
      currentAnalysisPromiseRef.current = analysisPromise;
      
      const result = await analysisPromise;
      
      currentAnalysisPromiseRef.current = null;
      
      // Only set result if analysis wasn't aborted
      if (!analysisAbortRef.current) {
        setOutputText(formatResult(result, 'GO2'));
        setProgressStatus('Completed');
        setProgressPercent(100);
        
        // Play bell sound when GO2 completes
        playBellSound();
      }
    } catch (error) {
      currentAnalysisPromiseRef.current = null;
      
      if (!analysisAbortRef.current && 
          !error.message.includes('Analysis cancelled') && 
          !error.message.includes('restart requested')) {
        console.error('GO2 analysis error:', error);
        setOutputText(`⚠️ Error: ${error.message}`);
      } else {
        console.log('GO2 analysis aborted:', error.message);
      }
    } finally {
      if (!analysisAbortRef.current) {
        setIsProcessing(false);
      }
    }
  }, [inputText, client, isProcessing]);

  const formatResult = (result, type = 'GO') => {
    if (!result || result.trim().length === 0) {
      return 'No analysis result received.';
    }
    
    let output = '---\n\n';
    if (type === 'GO2') {
      output += '# TEXT HUMANIZATION\n';
      output += '*(Powered by FinChat v2 API)*\n\n';
    } else {
      output += '# AI DETECTION ANALYSIS\n\n';
    }
    output += '---\n\n';
    output += result;
    
    return output;
  };

  return (
    <div className="container">
      {/* Warning Modal */}
      {showWarning && (
        <div className="modal-overlay" onClick={() => setShowWarning(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">⚠️ Insufficient Text</h3>
              <button 
                className="modal-close" 
                onClick={() => setShowWarning(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>Please provide at least <strong>250 words</strong> for accurate AI detection analysis.</p>
              <p className="modal-explanation">
                The AI detection tool requires a minimum amount of text to properly analyze writing patterns and detect AI-generated content. Short phrases or single sentences may not provide enough context for reliable results.
              </p>
              <p className="modal-word-count">
                Current word count: <strong>{countWords(inputText.trim())}</strong> word{countWords(inputText.trim()) !== 1 ? 's' : ''}
              </p>
            </div>
            <div className="modal-footer">
              <button 
                className="modal-button" 
                onClick={() => setShowWarning(false)}
              >
                OK, I Understand
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Same Text Warning Modal */}
      {showSameTextWarning && (
        <div className="modal-overlay" onClick={() => setShowSameTextWarning(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">⚠️ Same Text</h3>
              <button 
                className="modal-close" 
                onClick={() => setShowSameTextWarning(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>If you want to start a new analysis, change the text and press the GO button.</p>
              <p className="modal-explanation">
                The current text is the same as the text being analyzed. Please modify the text before starting a new analysis.
              </p>
            </div>
            <div className="modal-footer">
              <button 
                className="modal-button" 
                onClick={() => setShowSameTextWarning(false)}
              >
                OK, I Understand
              </button>
            </div>
          </div>
        </div>
      )}

      <header>
        <h1 className="title">
          <span className="title-write-aid">Write Aid</span>{' '}
          <span className="title-ai-checker">AI Checker</span>
        </h1>
        {isProcessing && (
          <div className="timer-display">
            <span className="timer-label">Analysis Time:</span>
            <span className="timer-value">{formatTime(elapsedTime)}</span>
            {progressStatus && (
              <>
                <span className="timer-separator">•</span>
                <span className="progress-status">{progressStatus}</span>
                {progressPercent > 0 && (
                  <span className="progress-percent">({progressPercent}%)</span>
                )}
              </>
            )}
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
                className="icon-button" 
                onClick={handleReset}
                disabled={isProcessing}
                title="Reset input and output to start a new analysis"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M13.65 2.35C12.2 0.9 10.2 0 8 0C3.58 0 0 3.58 0 8C0 12.42 3.58 16 8 16C11.73 16 14.84 13.45 15.73 10H13.65C12.83 12.33 10.61 14 8 14C4.69 14 2 11.31 2 8C2 4.69 4.69 2 8 2C9.66 2 11.14 2.69 12.22 3.78L9 7H16V0L13.65 2.35Z" fill="currentColor"/>
                </svg>
              </button>
              <button 
                className="go-button" 
                onClick={handleAnalyze}
                disabled={!inputText.trim()}
                title={isProcessing ? "Restart analysis with current text" : "Start AI detection analysis"}
              >
                Detect
              </button>
              <button 
                className="go-button go2-button" 
                onClick={handleAnalyzeGO2}
                disabled={!inputText.trim()}
                title={isProcessing ? "Restart humanization with current text" : "Start text humanization"}
              >
                Humanize
              </button>
            </div>
          </div>
          <div className="info-message">
            <span className="info-icon">ℹ️</span>
            <span>Analysis takes approximately 9 minutes. Minimum 250 words required.</span>
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
            {outputText ? (
              <div className="text-output-markdown">
                <ReactMarkdown>{outputText}</ReactMarkdown>
              </div>
            ) : isProcessing && progressStatus ? (
              <div className="text-output-placeholder processing-status">
                <div className="processing-spinner">⏳</div>
                <div className="processing-text">
                  <div className="processing-status-message">{progressStatus}</div>
                  {progressPercent > 0 && (
                    <div className="processing-progress-bar">
                      <div 
                        className="processing-progress-fill" 
                        style={{ width: `${progressPercent}%` }}
                      ></div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-output-placeholder">Results here...</div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
