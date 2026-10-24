# SwasthyaAI Frontend

A responsive React + TypeScript + Vite frontend for the SwasthyaAI healthcare navigation hackathon project. This directory is designed to be copied into the team's GitHub repository as `frontend/`.

## Included screens

- **Overview:** product introduction and guided entry points.
- **Care check:** multi-turn intake UI, language selection, follow-up options, speech input where supported, read-aloud, safety alert state and structured result display.
- **Find care:** searchable caregiver cards, sorting, explainable weighted ranking, demo booking request.
- **Future radar:** clearly labelled synthetic demand chart and proposed roadmap features.
- **Privacy & safety:** prototype consent controls and data-handling limitations.

## Requirements

- Node.js 20 LTS or newer recommended
- npm

## Run locally

From this directory:

```bash
npm install
cp .env.example .env.local
npm run dev
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env.local
npm install
npm run dev
```

Vite will print the local URL, usually `http://localhost:5173`.

## Demo mode vs connected API

The frontend starts in **explicit demo mode** by default because the backend/model are separate workstreams. The interface marks simulated results and synthetic caregiver profiles. Demo keyword checks are for UI walkthroughs only and are **not clinically validated**.

`.env.example`:

```env
VITE_DEMO_MODE=true
VITE_API_BASE_URL=http://localhost:8000
```

When the backend endpoint is ready, set:

```env
VITE_DEMO_MODE=false
VITE_API_BASE_URL=http://localhost:8000
```

The API client sends `POST {VITE_API_BASE_URL}/api/agent/message` with this proposed request shape:

```json
{
  "session_id": "session-id",
  "message": "User message",
  "language": "en",
  "history": [
    { "role": "user", "content": "Earlier message" }
  ]
}
```

The response contract expected by the frontend is described in `src/types/agent.ts`. Coordinate exact field names and statuses with Member 2 (agent) and Member 3 (backend) before integration. If the backend returns a different schema, update the shared types and API adapter together rather than adding business logic to UI components.

### Response status values

- `needs_followup`
- `routed`
- `possible_emergency`
- `unavailable`
- `error`

A response can include `follow_up_question`, `safety`, `triage`, `caregiver_matches`, `explanation`, `session_id`, `source`, and `error`. Keep the API contract stable across the frontend, agent and backend.

## Caregiver ranking

The demo implementation in `src/utils/rankingFormula.ts` uses these configurable engineering weights:

```text
S = 0.35K + 0.25D + 0.20A + 0.10L + 0.10R
```

- `K`: skill fit
- `D`: distance suitability
- `A`: slot suitability
- `L`: language match
- `R`: rating

The formula is illustrative and is not clinically validated. Mandatory qualification, service-area and availability filters must happen before ranking. A weighted score is not a probability of good care. Synthetic profile cards are labelled and are not verified providers.

## Speech

Voice input uses the browser's Web Speech API if available. Browser support and language accuracy vary. Text input remains available. Read-aloud uses browser speech synthesis where available. No third-party voice service is configured by this frontend.

## Important safety and privacy limitations

- This is a hackathon UI prototype, not a diagnostic or treatment service.
- Demo keyword logic is not a medical triage model and must not be used for real patient decisions.
- Never enter real patient information while demo mode is active.
- Do not claim zero data retention unless the complete backend, logs, analytics and connected services have been verified.
- A demo booking creates no real appointment and does not contact a provider.
- Local demo data and chart values are synthetic.
- Before any real-world healthcare use, the routing policy, emergency behavior, provider data, privacy/security controls, accessibility, and language-specific performance require appropriate review and validation.

## Project structure

```text
frontend/
├── package.json
├── index.html
├── vite.config.ts
├── tsconfig.json
├── .env.example
├── README.md
└── src/
    ├── App.tsx
    ├── main.tsx
    ├── index.css
    ├── components/
    │   ├── Navbar.tsx
    │   ├── CaregiverCard.tsx
    │   ├── ExplainabilityPanel.tsx
    │   ├── PrivacyDisclaimerModal.tsx
    │   └── SafetyShieldUrgentModal.tsx
    ├── i18n/translations.ts
    ├── services/
    │   ├── agentApi.ts
    │   └── demoFixtures.ts
    ├── types/agent.ts
    └── utils/rankingFormula.ts
```

## Scripts

- `npm run dev` — start local development server.
- `npm run build` — type-check and build production bundle.
- `npm run preview` — preview the production build.
- `npm run lint` — run the TypeScript compiler in no-emit mode.

## GitHub integration

Copy this entire folder into your repository at `frontend/`. Do not commit `.env.local`, API keys, real patient data, or backend credentials. Commit `.env.example` instead.
