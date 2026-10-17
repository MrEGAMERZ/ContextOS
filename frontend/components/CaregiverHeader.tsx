'use client';

import React from 'react';
import { CaregiverHealthScore } from '../lib/api';

interface CaregiverHeaderProps {
  scoreData: CaregiverHealthScore | null;
  statusMessage: string;
  onRefresh: () => void;
}

export default function CaregiverHeader({ scoreData, statusMessage, onRefresh }: CaregiverHeaderProps) {
  const score = scoreData?.autonomy_score ?? 95;
  const statusLabel = scoreData?.status_label ?? 'Stable';

  let scoreColor = 'text-emerald-400 border-emerald-500/30 bg-emerald-950/40';
  if (score < 50) scoreColor = 'text-rose-400 border-rose-500/30 bg-rose-950/40';
  else if (score < 75) scoreColor = 'text-amber-400 border-amber-500/30 bg-amber-950/40';

  return (
    <header className="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-slate-800 pb-5 gap-4">
      <div>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-cyan-500 flex items-center justify-center font-black text-slate-950 text-base shadow-lg shadow-emerald-500/20">
            C
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-white tracking-tight">ContextOS</h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Caregiver Trust OS
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Ambient Contextual Intelligence for Independent Living — Arthur (Age 78)
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center flex-wrap gap-3">
        {/* Autonomy & Safety Score Badge */}
        <div className={`flex items-center gap-2.5 px-3.5 py-1.5 rounded-xl border text-xs font-mono ${scoreColor}`}>
          <div className="flex flex-col text-right">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider">Autonomy Index</span>
            <span className="font-bold text-sm leading-none">{score}/100 • {statusLabel}</span>
          </div>
        </div>

        {/* Live SSE Status */}
        <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-500/30 px-3 py-2 rounded-xl">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>{statusMessage}</span>
        </div>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          title="Refresh Graph and Metrics"
        >
          🔄
        </button>
      </div>
    </header>
  );
}
