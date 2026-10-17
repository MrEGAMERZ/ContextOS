'use client';

import React, { useState } from 'react';

interface CoTDrawerProps {
  thinkingProcess: string | null;
  auditId?: string | null;
}

export default function CoTDrawer({ thinkingProcess, auditId }: CoTDrawerProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-2">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <span className="text-base">🧠</span>
          <h2 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            &quot;Why Did You Do That?&quot; CoT Drawer (AWS Builder Mini-Challenge)
          </h2>
        </div>
        <div className="flex items-center gap-2">
          {auditId && (
            <span className="text-[10px] text-slate-500 font-mono">
              Audit ID: {auditId.slice(0, 8)}..
            </span>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-[11px] font-mono text-slate-400 hover:text-white px-2 py-0.5 rounded bg-slate-800 transition"
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs max-h-64 overflow-y-auto">
          {thinkingProcess ? (
            <div>
              <div className="text-purple-400 font-bold mb-1.5 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
                Bedrock Claude 3.5 Sonnet &lt;thinking&gt; Reasoning Steps:
              </div>
              <pre className="whitespace-pre-wrap text-slate-300 text-[11px] leading-relaxed">
                {thinkingProcess}
              </pre>
            </div>
          ) : (
            <div className="text-slate-500 italic text-[11px] py-4 text-center">
              Trigger a voice query or smart-home anomaly to inspect Claude 3.5 reasoning steps.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
