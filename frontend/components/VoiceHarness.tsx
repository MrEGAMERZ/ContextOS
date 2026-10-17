'use client';

import React, { useState } from 'react';
import { askAgent, AgentQueryResponse } from '../lib/api';

interface VoiceHarnessProps {
  onResponseReceived: (res: AgentQueryResponse) => void;
}

export default function VoiceHarness({ onResponseReceived }: VoiceHarnessProps) {
  const [query, setQuery] = useState('Who is at the front door?');
  const [response, setResponse] = useState<AgentQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(true);

  async function handleAsk(queryText?: string) {
    const q = queryText || query;
    setLoading(true);
    try {
      const res = await askAgent(q);
      setResponse(res);
      onResponseReceived(res);

      // Web Speech TTS readout
      if (speechEnabled && typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(res.response);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
      }
    } catch (err) {
      console.error('Voice query error:', err);
    } finally {
      setLoading(false);
    }
  }

  const presets = [
    'Who is at the front door?',
    'Why is he here?',
    'Where are my glasses?',
    'Was the front door left open?',
  ];

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <span className="text-base">🎙️</span>
          <h2 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Simulated Alexa+ Voice Harness (Primary Track)
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSpeechEnabled(!speechEnabled)}
            className={`text-[10px] font-mono px-2 py-0.5 rounded border transition ${
              speechEnabled
                ? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-800 text-slate-500 border-slate-700'
            }`}
          >
            {speechEnabled ? '🔊 Audio TTS: ON' : '🔈 Audio TTS: OFF'}
          </button>
          <span className="text-[10px] text-emerald-400 font-mono bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded">
            SLA: &lt;50ms MCP
          </span>
        </div>
      </div>

      {/* Preset pills */}
      <div className="flex flex-wrap gap-1.5">
        {presets.map((preset, idx) => (
          <button
            key={idx}
            onClick={() => {
              setQuery(preset);
              handleAsk(preset);
            }}
            className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 transition font-mono"
          >
            &quot;{preset}&quot;
          </button>
        ))}
      </div>

      {/* Query input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask Alexa+ a natural question..."
          className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
          onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
        />
        <button
          onClick={() => handleAsk()}
          disabled={loading}
          className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 font-bold text-xs rounded-xl text-slate-950 transition shadow-lg shadow-emerald-500/10 font-mono"
        >
          {loading ? 'Thinking...' : 'Ask Voice'}
        </button>
      </div>

      {/* Live Response Box */}
      {response && (
        <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs space-y-1.5 animate-fadeIn">
          <div className="flex items-center justify-between">
            <span className="text-emerald-400 font-bold flex items-center gap-1.5">
              <span>🔊</span> Alexa+ Voice Turn:
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              {response.model_used.split('-')[1] || 'Claude'} • {response.execution_ms.toFixed(1)}ms
            </span>
          </div>
          <div className="text-white text-sm leading-relaxed">{response.response}</div>
        </div>
      )}
    </div>
  );
}
