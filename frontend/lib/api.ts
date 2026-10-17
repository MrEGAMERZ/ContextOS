/**
 * ContextOS Frontend API Client.
 * Communicates with FastAPI backend proxy endpoints.
 */

export type EntityType = 'person' | 'location' | 'object' | 'device' | 'routine';

export interface Entity {
  id: string;
  name: string;
  entity_type: EntityType;
  metadata: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface Relationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relation_type: string;
  weight: number;
  metadata?: Record<string, unknown>;
}

export interface NeighborhoodData {
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

export interface CaregiverHealthScore {
  autonomy_score: number;
  status_label: 'Excellent' | 'Stable' | 'Attention Needed' | 'Critical';
  medication_adherence_percent: number;
  social_interactions_count: number;
  anomalies_detected_count: number;
  events_count: number;
}

export interface CaregiverBriefing {
  generated_at: string;
  target_person: string;
  autonomy_score: number;
  status_label: string;
  medication_adherence_percent: number;
  social_interactions_count: number;
  anomalies_detected_count: number;
  summary_bullets: string[];
  bedrock_model_used: string;
  action_items: string[];
}

export interface AgentQueryResponse {
  query: string;
  response: string;
  thinking_process: string;
  audit_id: string;
  execution_ms: number;
  model_used: string;
  grounded_entity?: string;
}

export interface RingEventResult {
  ring_event_id: string;
  normalized_event_type: string;
  context_summary: string;
  threat_level: string;
  device_synced: string;
  persisted_event_id: string;
}

export interface PendingConfirmation {
  confirmation_token: string;
  action_type: string;
  target_entity?: string;
  parameters: Record<string, unknown>;
  reasoning?: string;
  created_at: string;
  status: string;
}

export async function fetchEntities(): Promise<Entity[]> {
  const res = await fetch('/api/graph/entities');
  if (!res.ok) throw new Error('Failed to fetch entities');
  return res.json();
}

export async function fetchRelationships(): Promise<Relationship[]> {
  const res = await fetch('/api/graph/relationships');
  if (!res.ok) throw new Error('Failed to fetch relationships');
  return res.json();
}

export async function fetchNeighborhood(name: string): Promise<NeighborhoodData> {
  const res = await fetch(`/api/graph/entities/${encodeURIComponent(name)}/neighborhood`);
  if (!res.ok) throw new Error(`Failed to fetch neighborhood for ${name}`);
  return res.json();
}

export async function fetchCaregiverHealthScore(): Promise<CaregiverHealthScore> {
  const res = await fetch('/api/caregiver/health-score');
  if (!res.ok) throw new Error('Failed to fetch health score');
  return res.json();
}

export async function fetchCaregiverBriefing(): Promise<CaregiverBriefing> {
  const res = await fetch('/api/caregiver/briefing');
  if (!res.ok) throw new Error('Failed to fetch caregiver briefing');
  return res.json();
}

export async function askAgent(query: string): Promise<AgentQueryResponse> {
  const res = await fetch('/api/agent/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error('Agent query failed');
  return res.json();
}

export async function injectScenario(scenario: string): Promise<Record<string, unknown>> {
  const res = await fetch('/api/events/inject', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario }),
  });
  if (!res.ok) throw new Error(`Failed to inject scenario ${scenario}`);
  return res.json();
}

export async function simulateRing(scenario: string): Promise<RingEventResult> {
  const res = await fetch('/api/ring/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario }),
  });
  if (!res.ok) throw new Error(`Ring simulation failed for ${scenario}`);
  return res.json();
}

export async function fetchPendingConfirmations(): Promise<PendingConfirmation[]> {
  const res = await fetch('/api/agent/confirmations/pending');
  if (!res.ok) return [];
  const data = await res.json();
  return data.pending_confirmations || [];
}

export async function resolveConfirmation(token: string, approved: boolean): Promise<Record<string, unknown>> {
  const res = await fetch(`/api/agent/confirmations/${encodeURIComponent(token)}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved }),
  });
  if (!res.ok) throw new Error('Failed to resolve confirmation');
  return res.json();
}
