'use client';

import React from 'react';
import { NeighborhoodData } from '../lib/api';

interface NeighborhoodInspectorProps {
  neighborhood: NeighborhoodData | null;
  onClose: () => void;
}

export default function NeighborhoodInspector({ neighborhood, onClose }: NeighborhoodInspectorProps) {
  if (!neighborhood) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 shadow-xl text-xs text-slate-500 font-mono italic">
        Select any node in the graph above to inspect its 2-hop relational context.
      </div>
    );
  }

  const { center, immediate_neighbors, two_hop_neighbors } = neighborhood;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3 relative">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <span className="text-base">🔍</span>
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            2-Hop Neighborhood Context Inspector
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-xs text-slate-400 hover:text-white transition font-mono px-2 py-0.5 rounded bg-slate-800"
        >
          ✕
        </button>
      </div>

      <div className="space-y-3 font-mono text-xs">
        <div>
          <span className="text-slate-400">Target: </span>
          <span className="text-emerald-400 font-bold">{center.name}</span>
          <span className="text-slate-500 ml-1.5 uppercase text-[10px]">({center.entity_type})</span>
        </div>

        {center.metadata && Object.keys(center.metadata).length > 0 && (
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-[11px] text-slate-300">
            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Entity Attributes</div>
            <pre className="whitespace-pre-wrap">{JSON.stringify(center.metadata, null, 2)}</pre>
          </div>
        )}

        <div>
          <div className="text-cyan-400 font-semibold mb-1">Immediate (1-Hop) Connections:</div>
          {immediate_neighbors.length > 0 ? (
            <ul className="list-disc pl-4 space-y-1 text-slate-300 text-[11px]">
              {immediate_neighbors.map((n, i) => (
                <li key={i}>
                  <span className="text-slate-400 font-bold">{n.direction === 'outgoing' ? '→' : '←'}</span>{' '}
                  <span className="text-white font-medium">{n.entity.name}</span>{' '}
                  <span className="text-amber-400/90 font-mono">[{n.relation_type}]</span>{' '}
                  <span className="text-slate-500">(wt: {n.weight})</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-slate-500 italic text-[11px]">No direct links.</div>
          )}
        </div>

        {two_hop_neighbors && two_hop_neighbors.length > 0 && (
          <div>
            <div className="text-purple-400 font-semibold mb-1">Extended (2-Hop) Inferences:</div>
            <ul className="list-disc pl-4 space-y-1 text-slate-400 text-[11px]">
              {two_hop_neighbors.map((n, i) => (
                <li key={i}>
                  <span>~ {n.entity.name}</span>{' '}
                  <span className="text-slate-500 font-mono">[{n.relation_type}]</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
