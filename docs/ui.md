# UI / Design System

## Palette
- base `#0a0a12` · panel `#0f1520` · edge `#1c2636`
- electric violet `#8b5cf6` · cyan `#22d3ee` · warm amber `#f59e0b` (memory hits)

## Typography
- Inter for UI/headings, monospace for scores and labels.

## Three states
1. **Landing** — video background + swipeable scroll-snap info sections.
2. **Chat** — 65/35 split: chat pane + retrieval-trace sidebar; background dims/blurs.
3. **Thinking** — glowing orb + cycling microcopy while awaiting /chat.

## Signature components
- Retrieval-trace cards: type badge, year, fused score, rerank delta (up/down).
- Amber "Recalled from memory" banner for agent_memory hits.
- Bottom-right founders badge (expands on hover/tap).
