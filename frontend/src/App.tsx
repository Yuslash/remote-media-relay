import { useState, useEffect } from 'react';
import './App.css';

// Using simple globals for MVP since we load this from Vite locally
const API_URL = import.meta.env.VITE_VPS_API_URL || "http://localhost:8000";
const WS_URL = import.meta.env.VITE_VPS_WS_URL || "ws://localhost:8000";
const API_TOKEN = import.meta.env.VITE_API_TOKEN || "super_secret_token_123";

function App() {
  const [url, setUrl] = useState('');
  const [preset, setPreset] = useState('discord_default');
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('Idle');
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<{ id: string; [key: string]: unknown }[]>([]);

  const startJob = async () => {
    if (!url) return;
    setError(null);
    setResultUrl(null);
    setProgress(0);
    setStage('Starting...');
    
    try {
      const response = await fetch(`${API_URL}/jobs/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-token': API_TOKEN
        },
        body: JSON.stringify({ source_url: url, preset })
      });
      
      if (!response.ok) throw new Error('Failed to create job');
      
      const data = await response.json();
      setActiveJobId(data.id);
      setHistory(prev => [data, ...prev]);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(String(err));
      }
      setStage('Error');
    }
  };

  useEffect(() => {
    if (!activeJobId) return;

    const ws = new WebSocket(`${WS_URL}/jobs/ws/${activeJobId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.percent);
      setStage(data.stage);
      
      if (data.stage === 'completed') {
        setResultUrl(data.output_url);
        setActiveJobId(null);
        ws.close();
      }
      if (data.stage === 'failed' || data.stage === 'cancelled') {
        setError(data.message);
        setActiveJobId(null);
        ws.close();
      }
    };

    return () => {
      ws.close();
    };
  }, [activeJobId]);

  const deleteJobFile = async (jobId: string) => {
    // Call the Electron bridge to confirm
    const confirm = await (window as unknown as { api: { confirmDelete: () => Promise<boolean> } }).api.confirmDelete();
    if (!confirm) return;

    try {
      const response = await fetch(`${API_URL}/jobs/${jobId}/file`, {
        method: 'DELETE',
        headers: {
          'x-token': API_TOKEN
        }
      });
      if (response.ok) {
        alert("File deleted from VPS.");
      } else {
        alert("Failed to delete file.");
      }
    } catch {
      alert("Error deleting file.");
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>Media Relay.</h1>
        <p className="subtitle">Remote rendering power at your fingertips.</p>
      </header>

      <main className="main-content">
        <div className="card input-card">
          <input 
            type="url" 
            placeholder="Paste your video URL here..." 
            value={url} 
            onChange={(e) => setUrl(e.target.value)}
            className="url-input"
          />
          <div className="controls">
            <select value={preset} onChange={(e) => setPreset(e.target.value)} className="preset-select">
              <option value="discord_default">Discord Default (720p, 10MB limit)</option>
              <option value="discord_small">Discord Small (Aggressive config)</option>
              <option value="discord_high_quality">High Quality (Max bits)</option>
            </select>
            <button className="btn-primary" onClick={startJob} disabled={!!activeJobId || !url}>
              {activeJobId ? 'Processing...' : 'Start Job'}
            </button>
          </div>
        </div>

        {activeJobId && (
          <div className="card progress-card active">
            <div className="progress-header">
              <span className="stage-badge">{stage.toUpperCase()}</span>
              <span className="percent">{Math.round(progress)}%</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}

        {resultUrl && !activeJobId && (
          <div className="card result-card pulse">
            <h3>Download Ready!</h3>
            <div className="result-actions">
              <a href={`${API_URL}${resultUrl}`} target="_blank" className="btn-secondary">Download Now</a>
              <button 
                  className="btn-danger" 
                  onClick={() => deleteJobFile(history[0]?.id)}>
                  Delete from VPS
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
             ⚠ {error}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
