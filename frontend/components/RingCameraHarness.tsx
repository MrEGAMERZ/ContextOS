'use client';

import React, { useState } from 'react';
import { simulateRing, RingEventResult } from '../lib/api';

interface RingCameraHarnessProps {
  onEventTriggered: () => void;
}

export default function RingCameraHarness({ onEventTriggered }: RingCameraHarnessProps) {
  const [latestResult, setLatestResult] = useState<RingEventResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSimulate(scenario: string) {
    setLoading(true);
    try {
      const res = await simulateRing(scenario);
      setLatestResult(res);
      onEventTriggered();
    } catch (err) {
      console.error('Ring simulation error:', err);
    } finally {
      setLoading(false);
    }
  }

  let badgeColor = 'text-emerald-400 bg-emerald-950/60 border-emerald-500/30';
  if (latestResult?.threat_level === 'HIGH' || latestResult?.threat_level === 'CRITICAL') {
    badgeColor = 'text-rose-400 bg-rose-950/60 border-rose-500/30';
  } else if (latestResult?.threat_level === 'MEDIUM') {
    badgeColor = 'text-amber-400 bg-amber-950/60 border-amber-500/30';
  }

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <span className="text-base">📹</span>
          <h2 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Ring Doorbell & Perception Feed Simulator (Ring Track)
          </h2>
        </div>
        <span className="text-[10px] text-cyan-400 font-mono bg-cyan-950/50 border border-cyan-500/30 px-2 py-0.5 rounded">
          Device Synced: Front Door
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <button
          onClick={() => handleSimulate('ding_neighbor')}
          disabled={loading}
          className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-left transition"
        >
          <div className="font-bold text-xs text-emerald-400">🔔 Neighbor Ding</div>
          <div className="text-[10px] text-slate-400">Ravi at Front Porch</div>
        </button>

        <button
          onClick={() => handleSimulate('ding_stranger')}
          disabled={loading}
          className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-left transition"
        >
          <div className="font-bold text-amber-400">🔔 Unknown Visitor</div>
          <div className="text-[10px] text-slate-400">Unrecognized Chime</div>
        </button>

        <button
          onClick={() => handleSimulate('late_night_motion')}
          disabled={loading}
          className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-left transition"
        >
          <div className="font-bold text-rose-400">🚨 Night Motion</div>
          <div className="text-[10px] text-slate-400">2:15 AM Porch Alert</div>
        </button>

        <button
          onClick={() => handleSimulate('motion_package')}
          disabled={loading}
          className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-left transition"
        >
          <div className="font-bold text-cyan-400">📦 Package Motion</div>
          <div className="text-[10px] text-slate-400">Porch Zone Activity</div>
        </button>
      </div>

      {latestResult && (
        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5 animate-fadeIn">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Latest Ring Webhook:</span>
            <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${badgeColor}`}>
              {latestResult.threat_level} Threat
            </span>
          </div>
          <div className="text-white font-medium">{latestResult.context_summary}</div>
          <div className="text-[10px] text-slate-500">Event ID: {latestResult.ring_event_id}</div>
        </div>
      )}
    </div>
  );
}
