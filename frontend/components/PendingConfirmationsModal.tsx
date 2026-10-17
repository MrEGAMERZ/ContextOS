'use client';

import React, { useState } from 'react';
import { PendingConfirmation, resolveConfirmation } from '../lib/api';

interface PendingConfirmationsModalProps {
  confirmations: PendingConfirmation[];
  onResolved: () => void;
}

export default function PendingConfirmationsModal({ confirmations, onResolved }: PendingConfirmationsModalProps) {
  const [resolvingToken, setResolvingToken] = useState<string | null>(null);

  if (!confirmations || confirmations.length === 0) return null;

  async function handleDecision(token: string, approved: boolean) {
    setResolvingToken(token);
    try {
      await resolveConfirmation(token, approved);
      onResolved();
    } catch (err) {
      console.error('Failed to resolve confirmation:', err);
    } finally {
      setResolvingToken(null);
    }
  }

  return (
    <div className="bg-amber-950/40 border-2 border-amber-500/40 rounded-2xl p-4 shadow-2xl space-y-3 animate-pulse-subtle">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">🛡️</span>
          <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono">
            Safety Gate: Action Requires Human-In-The-Loop Confirmation
          </h3>
        </div>
        <span className="text-[10px] bg-amber-500/20 text-amber-300 font-mono px-2 py-0.5 rounded border border-amber-500/30">
          CONFIRM Permission
        </span>
      </div>

      <div className="space-y-2">
        {confirmations.map((c) => (
          <div
            key={c.confirmation_token}
            className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-mono"
          >
            <div>
              <div className="text-white font-bold">
                Action: <span className="text-amber-400">{c.action_type}</span>{' '}
                {c.target_entity && <span className="text-slate-400">on {c.target_entity}</span>}
              </div>
              {c.reasoning && (
                <div className="text-[11px] text-slate-400 mt-0.5">Reason: {c.reasoning}</div>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleDecision(c.confirmation_token, true)}
                disabled={resolvingToken === c.confirmation_token}
                className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs transition"
              >
                Approve &amp; Execute
              </button>
              <button
                onClick={() => handleDecision(c.confirmation_token, false)}
                disabled={resolvingToken === c.confirmation_token}
                className="px-3 py-1.5 rounded-lg bg-rose-600/80 hover:bg-rose-500 text-white font-bold text-xs transition"
              >
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
