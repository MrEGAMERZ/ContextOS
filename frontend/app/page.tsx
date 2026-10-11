'use client';

import React, { useState, useEffect } from 'react';

type EntityType = 'person' | 'location' | 'object' | 'device' | 'routine';

interface Entity {
  id: string;
  name: string;
  entity_type: EntityType;
  metadata: Record<string, unknown>;
}

interface Relationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relation_type: string;
  weight: number;
}

interface NeighborhoodData {
  center: Entity;
  immediate_neighbors: Array<{
    entity: Entity;
    relation_type: string;
    direction: string;
    weight: number;
  }>;
  two_hop_neighbors: Array<{
    entity: Entity;
    relation_type: string;
    direction: string;
  }>;
}

function getEntityColor(type: EntityType): string {
  switch (type) {
    case 'person':
      return 'text-emerald-400 border-emerald-500/40 bg-emerald-950/40';
    case 'location':
      return 'text-cyan-400 border-cyan-500/40 bg-cyan-950/40';
    case 'object':
      return 'text-amber-400 border-amber-500/40 bg-amber-950/40';
    case 'device':
      return 'text-purple-400 border-purple-500/40 bg-purple-950/40';
    case 'routine':
      return 'text-rose-400 border-rose-500/40 bg-rose-950/40';
    default: {
      const _exhaustive: never = type;
      return _exhaustive;
    }
  }
}

export default function CaregiverDashboard() {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [selectedNeighborhood, setSelectedNeighborhood] = useState<NeighborhoodData | null>(null);
  const [voiceQuery, setVoiceQuery] = useState('Who is at the front door?');
  const [voiceResponse, setVoiceResponse] = useState<string | null>(null);
  const [thinkingProcess, setThinkingProcess] = useState<string | null>(null);
  const [loadingVoice, setLoadingVoice] = useState(false);
  const [statusMessage, setStatusMessage] = useState('SSE Stream Connected');

  useEffect(() => {
    fetchGraph();
  }, []);

  async function fetchGraph() {
    try {
      const [eRes, rRes] = await Promise.all([
        fetch('/api/graph/entities'),
        fetch('/api/graph/relationships')
      ]);
      if (eRes.ok && rRes.ok) {
        setEntities(await eRes.json());
        setRelationships(await rRes.json());
      }
    } catch (err) {
      console.error('Failed to load graph:', err);
    }
  }

  async function inspectEntity(name: string) {
    try {
      const res = await fetch(`/api/graph/entities/${encodeURIComponent(name)}/neighborhood`);
      if (res.ok) {
        setSelectedNeighborhood(await res.json());
      }
    } catch (err) {
      console.error('Failed to load neighborhood:', err);
    }
  }

  async function askVoice(queryToAsk?: string) {
    const q = queryToAsk || voiceQuery;
    setLoadingVoice(true);
    try {
      const res = await fetch('/api/agent/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      });
      if (res.ok) {
        const data = await res.json();
        setVoiceResponse(data.response);
        setThinkingProcess(data.thinking_process);
      }
    } catch (err) {
      console.error('Voice query failed:', err);
    } finally {
      setLoadingVoice(false);
    }
  }

  async function triggerScenario(scenario: string) {
    try {
      const res = await fetch('/api/events/inject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.anomalies_detected && data.anomalies_detected.length > 0) {
          const firstAnomaly = data.anomalies_detected[0];
          setThinkingProcess(firstAnomaly.thinking_process);
          setVoiceResponse(`[ALERT] ${firstAnomaly.title}: ${firstAnomaly.description}`);
        }
        await fetchGraph();
      }
    } catch (err) {
      console.error('Scenario injection failed:', err);
    }
  }

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto space-y-6">
      {/* HEADER */}
      <header className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold tracking-tight text-white">ContextOS</h1>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              Caregiver Trust Dashboard
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Ambient Contextual Intelligence Platform — Primary Track: Alexa+ MCP Server | AWS Builder
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-3 py-1.5 rounded-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>{statusMessage}</span>
        </div>
      </header>

      {/* DASHBOARD GRID */}
      <div className="grid grid-cols-12 gap-6">
        {/* GRAPH & NEIGHBORHOOD (7 COLS) */}
        <div className="col-span-12 lg:col-span-7 space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h2 className="text-sm font-bold text-white uppercase tracking-wide mb-3 flex items-center gap-2">
              <span>🕸️</span> Active Memory Graph Entities ({entities.length})
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {entities.map((e) => (
                <button
                  key={e.id}
                  onClick={() => inspectEntity(e.name)}
                  className={`p-3 rounded-xl border text-left transition hover:scale-105 ${getEntityColor(e.entity_type)}`}
                >
                  <div className="font-bold text-sm text-white">{e.name}</div>
                  <div className="text-[10px] uppercase tracking-wider font-mono opacity-80">{e.entity_type}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 2-HOP NEIGHBORHOOD */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <span>🔍</span> 2-Hop Neighborhood Context Inspector
            </h3>
            {selectedNeighborhood ? (
              <div className="space-y-3 font-mono text-xs">
                <div className="text-white font-bold">
                  Target: {selectedNeighborhood.center.name} ({selectedNeighborhood.center.entity_type})
                </div>
                <div className="text-accent-400 font-semibold">Immediate Connections:</div>
                <ul className="list-disc pl-4 space-y-1 text-slate-300">
                  {selectedNeighborhood.immediate_neighbors.map((n, i) => (
                    <li key={i}>
                      {n.direction === 'outgoing' ? '→' : '←'} {n.entity.name} [{n.relation_type}] (weight: {n.weight})
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="text-xs text-slate-500 font-mono italic">
                Select any entity above to inspect its 2-hop relational neighborhood.
              </div>
            )}
          </div>
        </div>

        {/* CONTROLS, VOICE & COT (5 COLS) */}
        <div className="col-span-12 lg:col-span-5 space-y-6">
          {/* SIMULATED EVENT INJECTOR */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
            <h2 className="text-sm font-bold text-white uppercase tracking-wide flex items-center gap-2">
              <span>⚡</span> Simulated Event Injector
            </h2>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => triggerScenario('visitor_arrival')}
                className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-left text-xs border border-slate-700"
              >
                <div className="font-bold text-emerald-400">🔔 Neighbor Visits</div>
                <div className="text-[10px] text-slate-400">Ravi at Front Door</div>
              </button>
              <button
                onClick={() => triggerScenario('object_relocation')}
                className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-left text-xs border border-slate-700"
              >
                <div className="font-bold text-cyan-400">👓 Move Glasses</div>
                <div className="text-[10px] text-slate-400">Relocate to Kitchen</div>
              </button>
              <button
                onClick={() => triggerScenario('front_door_open_anomaly')}
                className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-left text-xs border border-slate-700"
              >
                <div className="font-bold text-rose-400">🚪 Door Left Open</div>
                <div className="text-[10px] text-slate-400">35m Omission Anomaly</div>
              </button>
              <button
                onClick={() => triggerScenario('missed_medication')}
                className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-left text-xs border border-slate-700"
              >
                <div className="font-bold text-amber-400">💊 Missed Meds</div>
                <div className="text-[10px] text-slate-400">Routine Missed Alert</div>
              </button>
            </div>
          </div>

          {/* SIMULATED ALEXA+ VOICE HARNESS */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
            <h2 className="text-sm font-bold text-white uppercase tracking-wide flex items-center gap-2">
              <span>🎙️</span> Simulated Alexa+ Voice Harness
            </h2>
            <div className="flex gap-2">
              <input
                type="text"
                value={voiceQuery}
                onChange={(e) => setVoiceQuery(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-white"
              />
              <button
                onClick={() => askVoice()}
                disabled={loadingVoice}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 font-bold text-xs rounded-xl text-slate-950 transition"
              >
                {loadingVoice ? 'Thinking...' : 'Ask'}
              </button>
            </div>
            {voiceResponse && (
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs">
                <div className="text-emerald-400 font-bold mb-1">🔊 Alexa+ Response:</div>
                <div className="text-white">{voiceResponse}</div>
              </div>
            )}
          </div>

          {/* "WHY DID YOU DO THAT?" CHAIN OF THOUGHT DRAWER */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-2">
            <h2 className="text-sm font-bold text-white uppercase tracking-wide flex items-center gap-2">
              <span>🧠</span> "Why Did You Do That?" CoT Drawer
            </h2>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs max-h-56 overflow-y-auto">
              {thinkingProcess ? (
                <div>
                  <div className="text-purple-400 font-bold mb-1">Bedrock &lt;thinking&gt; Steps:</div>
                  <pre className="whitespace-pre-wrap text-slate-300 text-[11px]">{thinkingProcess}</pre>
                </div>
              ) : (
                <div className="text-slate-500 italic">
                  Ask a question or trigger an anomaly above to inspect Claude 3.5 reasoning.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
