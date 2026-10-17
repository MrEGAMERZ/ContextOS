'use client';

import React, { useState, useEffect, useCallback } from 'react';
import CaregiverHeader from '../components/CaregiverHeader';
import GraphCanvas from '../components/GraphCanvas';
import NeighborhoodInspector from '../components/NeighborhoodInspector';
import CaregiverBriefingCard from '../components/CaregiverBriefingCard';
import RingCameraHarness from '../components/RingCameraHarness';
import VoiceHarness from '../components/VoiceHarness';
import CoTDrawer from '../components/CoTDrawer';
import PendingConfirmationsModal from '../components/PendingConfirmationsModal';
import {
  Entity,
  Relationship,
  NeighborhoodData,
  CaregiverHealthScore,
  CaregiverBriefing,
  PendingConfirmation,
  fetchEntities,
  fetchRelationships,
  fetchNeighborhood,
  fetchCaregiverHealthScore,
  fetchCaregiverBriefing,
  fetchPendingConfirmations,
  injectScenario,
  AgentQueryResponse
} from '../lib/api';

export default function CaregiverDashboard() {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [selectedNeighborhood, setSelectedNeighborhood] = useState<NeighborhoodData | null>(null);
  const [selectedEntityName, setSelectedEntityName] = useState<string | null>(null);

  const [healthScore, setHealthScore] = useState<CaregiverHealthScore | null>(null);
  const [briefing, setBriefing] = useState<CaregiverBriefing | null>(null);
  const [pendingConfirmations, setPendingConfirmations] = useState<PendingConfirmation[]>([]);

  const [thinkingProcess, setThinkingProcess] = useState<string | null>(null);
  const [currentAuditId, setCurrentAuditId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState('SSE Stream Active');
  const [loadingBriefing, setLoadingBriefing] = useState(false);

  const loadAllData = useCallback(async () => {
    try {
      const [eData, rData, sData, bData, cData] = await Promise.all([
        fetchEntities(),
        fetchRelationships(),
        fetchCaregiverHealthScore(),
        fetchCaregiverBriefing(),
        fetchPendingConfirmations(),
      ]);
      setEntities(eData);
      setRelationships(rData);
      setHealthScore(sData);
      setBriefing(bData);
      setPendingConfirmations(cData);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    }
  }, []);

  useEffect(() => {
    loadAllData();

    // Subscribe to SSE stream
    let eventSource: EventSource | null = null;
    try {
      eventSource = new EventSource('/api/events/stream');
      eventSource.onopen = () => setStatusMessage('SSE Stream Connected');
      eventSource.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.type === 'CONFIRMATION_REQUIRED') {
            loadAllData();
          } else if (parsed.type === 'anomaly_alert' && parsed.data) {
            setThinkingProcess(parsed.data.thinking_process);
            setCurrentAuditId(parsed.data.audit_id);
            loadAllData();
          } else {
            loadAllData();
          }
        } catch {
          // ignore parsing error
        }
      };
      eventSource.onerror = () => setStatusMessage('SSE Reconnecting...');
    } catch (err) {
      console.error('SSE initialization error:', err);
    }

    return () => {
      if (eventSource) eventSource.close();
    };
  }, [loadAllData]);

  async function handleSelectEntity(name: string) {
    setSelectedEntityName(name);
    try {
      const data = await fetchNeighborhood(name);
      setSelectedNeighborhood(data);
    } catch (err) {
      console.error('Failed to load neighborhood:', err);
    }
  }

  async function handleRefreshBriefing() {
    setLoadingBriefing(true);
    try {
      const data = await fetchCaregiverBriefing();
      setBriefing(data);
      const sData = await fetchCaregiverHealthScore();
      setHealthScore(sData);
    } catch (err) {
      console.error('Failed to refresh briefing:', err);
    } finally {
      setLoadingBriefing(false);
    }
  }

  function handleVoiceResponse(res: AgentQueryResponse) {
    setThinkingProcess(res.thinking_process);
    setCurrentAuditId(res.audit_id);
    if (res.grounded_entity) {
      handleSelectEntity(res.grounded_entity);
    }
  }

  async function handleInjectScenario(scenario: string) {
    try {
      const res = await injectScenario(scenario);
      const anomalies = (res.anomalies_detected as Array<{ thinking_process?: string; audit_id?: string }>) || [];
      if (anomalies.length > 0) {
        setThinkingProcess(anomalies[0].thinking_process || null);
        setCurrentAuditId(anomalies[0].audit_id || null);
      }
      await loadAllData();
    } catch (err) {
      console.error('Scenario injection error:', err);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-6 max-w-7xl mx-auto space-y-6">
      {/* HEADER */}
      <CaregiverHeader
        scoreData={healthScore}
        statusMessage={statusMessage}
        onRefresh={loadAllData}
      />

      {/* PENDING CONFIRMATIONS MODAL / BANNER */}
      <PendingConfirmationsModal
        confirmations={pendingConfirmations}
        onResolved={loadAllData}
      />

      {/* MAIN TWO-COLUMN WORKSPACE */}
      <div className="grid grid-cols-12 gap-6">
        {/* LEFT COLUMN: GRAPH & CAREGIVER BRIEFING (7 COLS) */}
        <div className="col-span-12 lg:col-span-7 space-y-6">
          <GraphCanvas
            entities={entities}
            relationships={relationships}
            selectedEntityName={selectedEntityName}
            onSelectEntity={handleSelectEntity}
          />

          <NeighborhoodInspector
            neighborhood={selectedNeighborhood}
            onClose={() => {
              setSelectedNeighborhood(null);
              setSelectedEntityName(null);
            }}
          />

          <CaregiverBriefingCard
            briefing={briefing}
            onRefreshBriefing={handleRefreshBriefing}
            loading={loadingBriefing}
          />
        </div>

        {/* RIGHT COLUMN: VOICE HARNESS, COT, RING & INJECTORS (5 COLS) */}
        <div className="col-span-12 lg:col-span-5 space-y-6">
          <VoiceHarness onResponseReceived={handleVoiceResponse} />

          <CoTDrawer thinkingProcess={thinkingProcess} auditId={currentAuditId} />

          <RingCameraHarness onEventTriggered={loadAllData} />

          {/* SIMULATED ANOMALY INJECTOR */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center gap-2">
                <span className="text-base">⚡</span>
                <h2 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                  Autonomous Anomaly &amp; Omission Injector
                </h2>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Live Demo Controls</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => handleInjectScenario('wandering_nighttime')}
                className="p-3 rounded-xl bg-slate-950 hover:bg-slate-800 text-left border border-slate-800 transition"
              >
                <div className="font-bold text-xs text-rose-400">🌙 Wandering Risk</div>
                <div className="text-[10px] text-slate-400">2:30 AM Exterior Door</div>
              </button>

              <button
                onClick={() => handleInjectScenario('bathroom_fall')}
                className="p-3 rounded-xl bg-slate-950 hover:bg-slate-800 text-left border border-slate-800 transition"
              >
                <div className="font-bold text-amber-400">🚨 Bathroom Fall</div>
                <div className="text-[10px] text-slate-400">50m Inactivity Alert</div>
              </button>

              <button
                onClick={() => handleInjectScenario('front_door_open_anomaly')}
                className="p-3 rounded-xl bg-slate-950 hover:bg-slate-800 text-left border border-slate-800 transition"
              >
                <div className="font-bold text-cyan-400">🚪 Door Left Open</div>
                <div className="text-[10px] text-slate-400">35m Omission Pass</div>
              </button>

              <button
                onClick={() => handleInjectScenario('missed_medication')}
                className="p-3 rounded-xl bg-slate-950 hover:bg-slate-800 text-left border border-slate-800 transition"
              >
                <div className="font-bold text-emerald-400">💊 Missed Meds</div>
                <div className="text-[10px] text-slate-400">Morning Schedule Skip</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
