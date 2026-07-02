# EchoMind Frontend

Next.js 14 (app router) + Tailwind + framer-motion. Dark theme only.

## Develop
```bash
npm install --legacy-peer-deps
npm run dev      # http://localhost:3000
npm run build    # static export -> out/
```

## Structure
- `app/page.tsx` — orchestrates landing <-> chat states, /chat fetch
- `components/Landing.tsx` — swipeable scroll-snap info sections
- `components/VideoBackground.tsx` — fixed video backdrop with scroll parallax
- `components/TracePanel.tsx` — live retrieval-trace sidebar + memory banner
- `components/FoundersBadge.tsx` — persistent bottom-right team credit

## Notes
- Video background falls back to a CSS gradient on error.
- `prefers-reduced-motion` disables parallax/autoplay; app stays fully usable.
- All fetch calls hit `NEXT_PUBLIC_API_URL` (defaults to `localhost:8000`).
