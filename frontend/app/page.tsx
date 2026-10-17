'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  NodeTypes,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';

// ─── Types ────────────────────────────────────────────────────────────────────

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

interface AuditLog {
  id: string;
  action_type: string;
  thinking_process: string;
  output_response: string;
  created_at: string;
}

// ─── Entity color map ─────────────────────────────────────────────────────────

const ENTITY_COLORS: Record<EntityType, { bg: string; border: string; label: string; icon: string }> = {
  person:   { bg: '#052e16', border: '#16a34a', label: '#4ade80', icon: '👤' },
  location: { bg: '#0c4a6e', border: '#0ea5e9', label: '#38bdf8', icon: '📍' },
  object:   { bg: '#451a03', border: '#d97706', label: '#fbbf24', icon: '📦' },
  device:   { bg: '#2e1065', border: '#9333ea', label: '#c084fc', icon: '🔌' },
  routine:  { bg: '#450a0a', border: '#dc2626', label: '#f87171', icon: '🔁' },
};

// ─── Custom Entity Node ────────────────────────────────────────────────────────

function EntityNode({ data }: { data: { label: string; entityType: EntityType; metadata: Record<string, unknown>; selected: boolean } }) {
  const colors = ENTITY_COLORS[data.entityType] || ENTITY_COLORS.device;
  return (
    <div
      style={{
        background: colors.bg,
        border: `1.5px solid ${data.selected ? '#fff' : colors.border}`,
        borderRadius: 12,
        padding: '8px 12px',
        minWidth: 110,
        textAlign: 'center',
        boxShadow: data.selected ? `0 0 12px ${colors.border}` : 'none',
        transition: 'box-shadow 0.2s',
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: colors.border, width: 8, height: 8 }} />
      <div style={{ fontSize: 18, marginBottom: 2 }}>{colors.icon}</div>
      <div style={{ color: colors.label, fontWeight: 700, fontSize: 11, lineHeight: 1.2 }}>{data.label}</div>
      <div style={{ color: '#64748b', fontSize: 9, marginTop: 2, textTransform: 'uppercase', letterSpacing: 1 }}>
        {data.entityType}
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: colors.border, width: 8, height: 8 }} />
    </div>
  );
}

const nodeTypes: NodeTypes = { entity: EntityNode };

// ─── Layout helper (simple circular) ─────────────────────────────────────────

function buildLayout(entities: Entity[], relationships: Relationship[]) {
  const TYPES: EntityType[] = ['person', 'location', 'device', 'object', 'routine'];
  const groups: Record<string, Entity[]> = {};
  for (const e of entities) {
    if (!groups[e.entity_type]) groups[e.entity_type] = [];
    groups[e.entity_type].push(e);
  }

  const nodes: Node[] = [];
  const COL_GAP = 200, ROW_GAP = 110;
  TYPES.forEach((type, col) => {
    (groups[type] || []).forEach((e, row) => {
      nodes.push({
        id: e.id,
        type: 'entity',
        position: { x: col * COL_GAP + 40, y: row * ROW_GAP + 40 },
        data: { label: e.name, entityType: e.entity_type, metadata: e.metadata, selected: false },
      });
    });
  });

  const edges: Edge[] = relationships.map((r) => ({
    id: r.id,
    source: r.source_entity_id,
    target: r.target_entity_id,
    label: r.relation_type,
    labelStyle: { fill: '#94a3b8', fontSize: 9 },
    style: { stroke: '#334155', strokeWidth: 1.5 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' },
    type: 'smoothstep',
  }));

  return { nodes, edges };
}

// ─── SSE hook ─────────────────────────────────────────────────────────────────

function useSSE(url: string, onMessage: (data: unknown) => void) {
  const cbRef = useRef(onMessage);
  cbRef.current = onMessage;
  useEffect(() => {
    const es = new EventSource(url);
    es.onmessage = (e) => {
      try { cbRef.current(JSON.parse(e.data)); } catch { /* ignore non-JSON */ }
    };
    return () => es.close();
  }, [url]);
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────

export default function CaregiverDashboard() {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [voiceQuery, setVoiceQuery] = useState('Where are my glasses?');
  const [voiceResponse, setVoiceResponse] = useState<string | null>(null);
  const [thinkingProcess, setThinkingProcess] = useState<string | null>(null);
  const [loadingVoice, setLoadingVoice] = useState(false);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [activeTab, setActiveTab] = useState<'graph' | 'audit'>('graph');
  const [streamEvents, setStreamEvents] = useState<string[]>([]);
  const [sseStatus, setSseStatus] = useState<'connecting' | 'live' | 'error'>('connecting');

  // ── Load graph data ──────────────────────────────────────────────────────────

  const fetchGraph = useCallback(async () => {
    try {
      const [eRes, rRes] = await Promise.all([
        fetch('http://localhost:8000/api/graph/entities'),
        fetch('http://localhost:8000/api/graph/relationships'),
      ]);
      if (eRes.ok && rRes.ok) {
        const es: Entity[] = await eRes.json();
        const rs: Relationship[] = await rRes.json();
        setEntities(es);
        setRelationships(rs);
        const { nodes: n, edges: e } = buildLayout(es, rs);
        setNodes(n);
        setEdges(e);
        setSseStatus('live');
      }
    } catch (err) {
      console.error('Graph fetch failed:', err);
    }
  }, [setNodes, setEdges]);

  const fetchAuditLogs = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/audit-logs?limit=10');
      if (res.ok) setAuditLogs(await res.json());
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    fetchGraph();
    fetchAuditLogs();
  }, [fetchGraph, fetchAuditLogs]);

  // ── SSE realtime stream ──────────────────────────────────────────────────────

  useSSE('http://localhost:8000/api/events/stream', (data) => {
    const msg = (data as { event?: string; message?: string });
    const label = msg.event ?? JSON.stringify(data).slice(0, 60);
    setStreamEvents((prev) => [label, ...prev].slice(0, 30));
    fetchGraph();
    fetchAuditLogs();
  });

  // ── Highlight selected node ──────────────────────────────────────────────────

  const highlightEntity = useCallback((name: string) => {
    setSelectedEntity(name);
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: { ...n.data, selected: n.data.label === name },
      }))
    );
  }, [setNodes]);

  // ── Voice query ──────────────────────────────────────────────────────────────

  async function askVoice() {
    setLoadingVoice(true);
    setVoiceResponse(null);
    setThinkingProcess(null);
    try {
      const res = await fetch('http://localhost:8000/api/agent/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: voiceQuery }),
      });
      if (res.ok) {
        const data = await res.json();
        setVoiceResponse(data.response);
        setThinkingProcess(data.thinking_process);
        fetchAuditLogs();
      }
    } catch { setVoiceResponse('Backend unavailable.'); }
    finally { setLoadingVoice(false); }
  }

  // ── Event Injector ───────────────────────────────────────────────────────────

  async function injectScenario(scenario: string) {
    try {
      const res = await fetch('http://localhost:8000/api/events/inject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.anomalies_detected?.length) {
          const a = data.anomalies_detected[0];
          setVoiceResponse(`⚠️ ${a.title}: ${a.description}`);
          setThinkingProcess(a.thinking_process);
        }
        fetchGraph();
        fetchAuditLogs();
      }
    } catch { /* silent */ }
  }

  // ─── Render ────────────────────────────────────────────────────────────────

  const SCENARIOS = [
    { id: 'visitor_arrival',      icon: '🔔', label: 'Visitor Arrives',  sub: 'Ravi at front door',      color: '#4ade80' },
    { id: 'object_relocation',    icon: '👓', label: 'Glasses Moved',    sub: 'Relocated to kitchen',    color: '#38bdf8' },
    { id: 'front_door_open_anomaly', icon: '🚪', label: 'Door Left Open', sub: '35m anomaly alert',    color: '#f87171' },
    { id: 'missed_medication',    icon: '💊', label: 'Missed Meds',      sub: 'Routine omission',        color: '#fbbf24' },
  ];

  const PRESET_QUERIES = [
    'Where are my glasses?',
    'Who was at the door today?',
    'Did Arthur take his medication?',
    'What happened at midnight?',
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#0a0f1e', color: '#e2e8f0', fontFamily: 'system-ui, sans-serif', padding: '20px' }}>
      
      {/* ── HEADER ── */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: 16, marginBottom: 20 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 22, fontWeight: 900, color: '#fff' }}>ContextOS</span>
            <span style={{ fontSize: 10, padding: '3px 8px', borderRadius: 6, background: '#052e1640', color: '#4ade80', border: '1px solid #16a34a40', fontFamily: 'monospace' }}>
              Caregiver Trust Dashboard
            </span>
            <span style={{ fontSize: 10, padding: '3px 8px', borderRadius: 6, background: '#2e106540', color: '#c084fc', border: '1px solid #9333ea40', fontFamily: 'monospace' }}>
              Alexa+ MCP · AWS Builder
            </span>
          </div>
          <p style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>
            Ambient Contextual Intelligence · Semantic Memory Graph · {entities.length} entities · {relationships.length} relationships
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: sseStatus === 'live' ? '#052e1660' : '#45031660', border: `1px solid ${sseStatus === 'live' ? '#16a34a50' : '#dc262650'}`, borderRadius: 8, padding: '6px 12px', fontSize: 11, fontFamily: 'monospace', color: sseStatus === 'live' ? '#4ade80' : '#f87171' }}>
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: sseStatus === 'live' ? '#4ade80' : '#f87171', display: 'inline-block', animation: sseStatus === 'live' ? 'pulse 2s infinite' : 'none' }} />
          {sseStatus === 'live' ? 'SSE Stream Live' : 'Connecting...'}
        </div>
      </header>

      {/* ── MAIN GRID ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 20 }}>

        {/* ── LEFT: Graph + tabs ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Tab strip */}
          <div style={{ display: 'flex', gap: 8 }}>
            {(['graph', 'audit'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '6px 16px', borderRadius: 8, fontSize: 11, fontWeight: 700,
                  background: activeTab === tab ? '#1e293b' : 'transparent',
                  color: activeTab === tab ? '#fff' : '#64748b',
                  border: `1px solid ${activeTab === tab ? '#334155' : 'transparent'}`,
                  cursor: 'pointer', textTransform: 'uppercase', letterSpacing: 1,
                }}
              >
                {tab === 'graph' ? '🕸️ Memory Graph' : '🧠 Audit Log'}
              </button>
            ))}
          </div>

          {activeTab === 'graph' && (
            <div style={{ background: '#0d1526', border: '1px solid #1e293b', borderRadius: 16, overflow: 'hidden', height: 500 }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={(_, node) => highlightEntity(node.data.label)}
                nodeTypes={nodeTypes}
                fitView
                proOptions={{ hideAttribution: true }}
              >
                <Background color="#1e293b" gap={20} />
                <Controls style={{ background: '#0d1526', border: '1px solid #1e293b' }} />
                <MiniMap
                  nodeStrokeColor={(n) => ENTITY_COLORS[(n.data as { entityType: EntityType }).entityType]?.border ?? '#64748b'}
                  nodeColor={(n) => ENTITY_COLORS[(n.data as { entityType: EntityType }).entityType]?.bg ?? '#0d1526'}
                  style={{ background: '#0d1526', border: '1px solid #1e293b' }}
                />
              </ReactFlow>
            </div>
          )}

          {activeTab === 'audit' && (
            <div style={{ background: '#0d1526', border: '1px solid #1e293b', borderRadius: 16, padding: 16, height: 500, overflowY: 'auto' }}>
              {auditLogs.length === 0 ? (
                <div style={{ color: '#475569', fontSize: 12, fontFamily: 'monospace', textAlign: 'center', paddingTop: 40 }}>
                  No audit logs yet. Ask a question or trigger a scenario.
                </div>
              ) : auditLogs.map((log) => (
                <div key={log.id} style={{ borderBottom: '1px solid #1e293b', paddingBottom: 12, marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: '#c084fc', textTransform: 'uppercase' }}>{log.action_type}</span>
                    <span style={{ fontSize: 9, color: '#475569', fontFamily: 'monospace' }}>{new Date(log.created_at).toLocaleTimeString()}</span>
                  </div>
                  <div style={{ fontSize: 11, color: '#e2e8f0', marginBottom: 4 }}>{log.output_response}</div>
                  {log.thinking_process && (
                    <details style={{ fontSize: 10, color: '#64748b', fontFamily: 'monospace' }}>
                      <summary style={{ cursor: 'pointer', color: '#9333ea' }}>View thinking process →</summary>
                      <pre style={{ whiteSpace: 'pre-wrap', marginTop: 4, color: '#94a3b8', lineHeight: 1.5 }}>{log.thinking_process}</pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* SSE Event Feed */}
          <div style={{ background: '#0d1526', border: '1px solid #1e293b', borderRadius: 12, padding: 12 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: '#4ade80', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>
              📡 Live SSE Event Feed
            </div>
            <div style={{ maxHeight: 80, overflowY: 'auto', fontFamily: 'monospace', fontSize: 10, color: '#475569' }}>
              {streamEvents.length === 0
                ? <span style={{ color: '#334155', fontStyle: 'italic' }}>Waiting for events...</span>
                : streamEvents.map((ev, i) => (
                    <div key={i} style={{ color: i === 0 ? '#94a3b8' : '#334155', paddingBottom: 2 }}>
                      {i === 0 ? '▶ ' : '  '}{ev}
                    </div>
                  ))}
            </div>
          </div>
        </div>

        {/* ── RIGHT: Controls ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Event Injector */}
          <div style={{ background: '#0d1526', border: '1px solid #1e293b', borderRadius: 16, padding: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#fff', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 }}>
              ⚡ Event Injector
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {SCENARIOS.map((s) => (
                <button
                  key={s.id}
                  onClick={() => injectScenario(s.id)}
                  style={{
                    padding: '10px 8px', borderRadius: 10, background: '#141f35', border: '1px solid #1e293b',
                    cursor: 'pointer', textAlign: 'left', transition: 'border-color 0.15s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.borderColor = s.color)}
                  onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#1e293b')}
                >
                  <div style={{ fontSize: 14, marginBottom: 3 }}>{s.icon}</div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: s.color }}>{s.label}</div>
                  <div style={{ fontSize: 9, color: '#64748b', marginTop: 1 }}>{s.sub}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Voice Harness */}
          <div style={{ background: '#0d1526', border: '1px solid #1e293b', borderRadius: 16, padding: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#fff', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 }}>
              🎙️ Simulated Alexa+ Voice
            </div>

            {/* Preset queries */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 8 }}>
              {PRESET_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => setVoiceQuery(q)}
                  style={{
                    fontSize: 9, padding: '3px 7px', borderRadius: 6, background: voiceQuery === q ? '#1e3a5f' : '#141f35',
                    border: `1px solid ${voiceQuery === q ? '#0ea5e9' : '#1e293b'}`, color: voiceQuery === q ? '#38bdf8' : '#64748b',
                    cursor: 'pointer',
                  }}
                >
                  {q}
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', gap: 6, marginBottom: 10 }}>
              <input
                type="text"
                value={voiceQuery}
                onChange={(e) => setVoiceQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && askVoice()}
                style={{ flex: 1, background: '#0a0f1e', border: '1px solid #1e293b', borderRadius: 8, padding: '8px 10px', fontSize: 11, color: '#e2e8f0', outline: 'none', fontFamily: 'monospace' }}
              />
              <button
                onClick={askVoice}
                disabled={loadingVoice}
                style={{
                  padding: '8px 14px', borderRadius: 8, background: loadingVoice ? '#1e3a5f' : '#16a34a',
                  color: '#fff', fontWeight: 700, fontSize: 11, cursor: loadingVoice ? 'wait' : 'pointer', border: 'none',
                }}
              >
                {loadingVoice ? '...' : '▶'}
              </button>
            </div>

            {voiceResponse && (
              <div style={{ background: '#0a0f1e', border: '1px solid #1e293b', borderRadius: 10, padding: 10, fontSize: 11, color: '#e2e8f0', fontFamily: 'monospace', marginBottom: 8 }}>
                <span style={{ color: '#4ade80', fontWeight: 700 }}>Alexa: </span>{voiceResponse}
              </div>
            )}
          </div>

          {/* CoT Drawer */}
          {thinkingProcess && (
            <div style={{ background: '#0d1526', border: '1px solid #2e1065', borderRadius: 16, padding: 16 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#c084fc', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>
                🧠 Why Did You Do That?
              </div>
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: 10, color: '#94a3b8', fontFamily: 'monospace', maxHeight: 160, overflowY: 'auto', lineHeight: 1.6 }}>
                {thinkingProcess}
              </pre>
            </div>
          )}

          {/* Entity Legend */}
          <div style={{ background: '#0d1526', border: '1px solid #1e293b', borderRadius: 12, padding: 12 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Legend</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              {(Object.entries(ENTITY_COLORS) as [EntityType, typeof ENTITY_COLORS[EntityType]][]).map(([type, c]) => (
                <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 10 }}>
                  <span style={{ width: 10, height: 10, borderRadius: 3, background: c.bg, border: `1.5px solid ${c.border}`, display: 'inline-block' }} />
                  <span style={{ color: c.label }}>{c.icon} {type}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
