'use client';

import React from 'react';
import { CaregiverBriefing } from '../lib/api';

interface CaregiverBriefingCardProps {
  briefing: CaregiverBriefing | null;
  onRefreshBriefing: () => void;
  loading: boolean;
}

export default function CaregiverBriefingCard({ briefing, onRefreshBriefing, loading }: CaregiverBriefingCardProps) {
  if (!briefing) return null;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <span className="text-base">📋</span>
          <h2 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Caregiver Daily Executive Briefing (Bedrock Claude 3.5 Sonnet)
          </h2>
        </div>
        <button
          onClick={onRefreshBriefing}
          disabled={loading}
          className="text-xs text-slate-300 hover:text-white px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 transition font-mono text-[11px]"
        >
          {loading ? 'Synthesizing...' : 'Re-generate'}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-2 py-1">
        <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 text-center">
          <div className="text-[10px] text-slate-500 uppercase font-mono">Adherence</div>
          <div className="text-sm font-bold text-emerald-400 font-mono">
            {briefing.medication_adherence_percent}%
          </div>
        </div>
        <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 text-center">
          <div className="text-[10px] text-slate-500 uppercase font-mono">Social Visits</div>
          <div className="text-sm font-bold text-cyan-400 font-mono">
            {briefing.social_interactions_count}
          </div>
        </div>
        <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 text-center">
          <div className="text-[10px] text-slate-500 uppercase font-mono">Anomalies</div>
          <div className="text-sm font-bold text-amber-400 font-mono">
            {briefing.anomalies_detected_count}
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wide">Key Observations:</div>
        <ul className="space-y-1.5 text-xs text-slate-200">
          {briefing.summary_bullets.map((bullet, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-emerald-400 mt-0.5">•</span>
              <span>{bullet}</span>
            </li>
          ))}
        </ul>
      </div>

      {briefing.action_items && briefing.action_items.length > 0 && (
        <div className="pt-2 border-t border-slate-800/60">
          <div className="text-[11px] font-bold text-purple-400 uppercase tracking-wide mb-1">
            Caregiver Action Item:
          </div>
          <div className="text-xs text-slate-300 font-mono bg-purple-950/30 border border-purple-500/20 p-2.5 rounded-xl">
            {briefing.action_items[0]}
          </div>
        </div>
      )}
    </div>
  );
}
