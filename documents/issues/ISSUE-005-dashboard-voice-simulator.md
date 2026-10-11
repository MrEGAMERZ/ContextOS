# Issue #5: Caregiver Trust Dashboard & Voice Simulator

**Status:** Closed (Resolved by [PR #5](../pull_requests/PR-005-dashboard-voice-simulator.md))  
**Shipment:** Shipment 5  
**Labels:** `frontend`, `ui`, `react-flow`, `voice-harness`, `shipment-5`

## Description
Develop the Next.js Caregiver Trust Dashboard featuring an interactive React Flow graph visualizer, real-time event updates via SSE, an inspectable "Why Did You Do That?" Chain of Thought drawer, and a web-based Simulated Alexa+ Voice Harness for fail-safe demo presentations.

## Acceptance Criteria
1. Next.js 14+ application with Tailwind CSS in dark-mode theme.
2. React Flow visualizer rendering the ContextOS Memory Graph (Nodes: People, Rooms, Devices, Objects; Edges: typed directional relationships).
3. SSE client subscribing to `/api/events/stream` and smoothly animating graph transitions upon receiving new events.
4. Simulated Event Injector panel with instant buttons to trigger hackathon demo scenarios.
5. "Why Did You Do That?" drawer displaying Claude 3.5 Sonnet `<thinking>` reasoning logs on click of any alert node.
6. Simulated Alexa+ Voice Harness:
   - Voice/text query bar that dispatches tool requests against the local MCP server.
   - Speech synthesis (Web Speech API) to speak back the agent's answer, mimicking Alexa hardware.
