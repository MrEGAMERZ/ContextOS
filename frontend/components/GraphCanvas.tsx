'use client';

import React from 'react';
import { Entity, Relationship, EntityType } from '../lib/api';

interface GraphCanvasProps {
  entities: Entity[];
  relationships: Relationship[];
  selectedEntityName: string | null;
  onSelectEntity: (name: string) => void;
}

function getNodeIcon(type: EntityType): string {
  switch (type) {
    case 'person':
      return '👤';
    case 'location':
      return '📍';
    case 'object':
      return '👓';
    case 'device':
      return '📹';
    case 'routine':
      return '💊';
    default:
      return '⚪';
  }
}

function getNodeColor(type: EntityType, isSelected: boolean): string {
  if (isSelected) {
    return 'stroke-white stroke-2 fill-emerald-600';
  }
  switch (type) {
    case 'person':
      return 'stroke-emerald-400/80 fill-emerald-950/80';
    case 'location':
      return 'stroke-cyan-400/80 fill-cyan-950/80';
    case 'object':
      return 'stroke-amber-400/80 fill-amber-950/80';
    case 'device':
      return 'stroke-purple-400/80 fill-purple-950/80';
    case 'routine':
      return 'stroke-rose-400/80 fill-rose-950/80';
    default:
      return 'stroke-slate-400 fill-slate-900';
  }
}

export default function GraphCanvas({
  entities,
  relationships,
  selectedEntityName,
  onSelectEntity,
}: GraphCanvasProps) {
  const width = 640;
  const height = 400;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = 150;

  // Compute circular layout for nodes
  const nodePositions = new Map<string, { x: number; y: number; entity: Entity }>();
  entities.forEach((entity, idx) => {
    // Put Arthur in center if present
    if (entity.name.toLowerCase() === 'arthur') {
      nodePositions.set(entity.id, { x: centerX, y: centerY, entity });
    } else {
      const angle = (idx / Math.max(entities.length - 1, 1)) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      nodePositions.set(entity.id, { x, y, entity });
    }
  });

  return (
    <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 shadow-xl relative overflow-hidden">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-base">🕸️</span>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Semantic Memory Graph ({entities.length} Nodes • {relationships.length} Edges)
          </h2>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          Click any node to inspect 2-hop neighborhood
        </span>
      </div>

      <div className="w-full flex justify-center bg-slate-900/40 rounded-xl border border-slate-800/60 p-2">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full max-h-[380px] select-none"
        >
          {/* Edges */}
          <g className="edges">
            {relationships.map((rel) => {
              const src = nodePositions.get(rel.source_entity_id);
              const tgt = nodePositions.get(rel.target_entity_id);
              if (!src || !tgt) return null;

              const midX = (src.x + tgt.x) / 2;
              const midY = (src.y + tgt.y) / 2;

              return (
                <g key={rel.id}>
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke="#334155"
                    strokeWidth="1.5"
                    strokeDasharray="4 2"
                    className="opacity-70"
                  />
                  <text
                    x={midX}
                    y={midY}
                    fill="#94a3b8"
                    fontSize="9"
                    fontFamily="monospace"
                    textAnchor="middle"
                    className="opacity-80"
                  >
                    {rel.relation_type}
                  </text>
                </g>
              );
            })}
          </g>

          {/* Nodes */}
          <g className="nodes">
            {Array.from(nodePositions.values()).map(({ x, y, entity }) => {
              const isSelected = selectedEntityName === entity.name;
              return (
                <g
                  key={entity.id}
                  transform={`translate(${x}, ${y})`}
                  onClick={() => onSelectEntity(entity.name)}
                  className="cursor-pointer transition transform hover:scale-110"
                >
                  <circle
                    r="22"
                    className={`${getNodeColor(entity.entity_type, isSelected)} transition`}
                  />
                  <text
                    textAnchor="middle"
                    dy="-3"
                    fontSize="13"
                    className="select-none pointer-events-none"
                  >
                    {getNodeIcon(entity.entity_type)}
                  </text>
                  <text
                    textAnchor="middle"
                    dy="14"
                    fontSize="8"
                    fontFamily="monospace"
                    fontWeight="bold"
                    fill="#f8fafc"
                    className="select-none pointer-events-none"
                  >
                    {entity.name.length > 10 ? `${entity.name.slice(0, 8)}..` : entity.name}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>
    </div>
  );
}
