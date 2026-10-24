# SwasthyaAI Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable local/demo healthcare coordination platform with conservative multilingual triage, explainable caregiver matching, role-based demo workflows, and an animated responsive frontend.

**Architecture:** FastAPI exposes a versioned API backed by local SQLite; an agent service applies deterministic safety checks before optional model adapters and bounded session logic. A React/TypeScript client uses the API for patient, clinician, discovery, records, appointments, reminders, education, and model-status views; unsupported clinical capabilities remain explicitly unavailable.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, SQLite, pytest/httpx; React, TypeScript, Vite, browser Web Speech APIs where available.

**Spec:** `docs/superpowers/specs/2026-10-24-swasthya-platform-design.md`

## Global Constraints

- The supplied Sanocare examples and caregiver roster are synthetic and are not clinical ground truth.
- Deterministic emergency checks run before every model; emergency results use `emergency_112`, advise calling 112, and have no caregiver matches.
- Never provide a diagnosis, prescription, treatment plan, fabricated model output, or claim of clinical validation.
- Follow-up conversation is bounded to at most two questions total per session; there is no autonomous tool-call loop.
- Patient/clinician records are synthetic and local/demo only; never commit datasets, model artifacts, uploads, secrets, or real patient data.
- Caregiver Stage 1 eligibility filters cannot be bypassed by Stage 2 ranking; use the screenshot formula by default and measure the dataset baseline separately.
- Run all registered models relevant to a request concurrently with per-adapter timeouts; do not call unrelated models or blindly average different tasks.
- Combine datasets for training only after task, labels/schema, language coverage, provenance, and license compatibility checks; keep incompatible datasets separate.
- Gemini is optional, disabled without local `GEMINI_API_KEY`, cannot alter structured safety/triage fields, and receives no health data without explicit consent.
- Appointment requests remain `requested` unless a real scheduling integration exists; browser voice support is best-effort with text fallback.
- Respect role ownership, accessible keyboard/screen-reader behavior, and `prefers-reduced-motion`.
- Work on `feature/swasthya-platform`; every increment must pass its focused tests before a separate commit/push.

## Review Focus

- Negated, quoted, and historical red-flag language must not silently trigger or suppress emergency escalation — test these through the owning safety tests.
- Hinglish and mixed-script Unicode input must not crash or become an empty match — test normalization and unsupported-language fallback in the agent task.
- Missing, malformed, or out-of-range coordinates must not break triage or leak matches — test request validation and location-free fallback in the API/matcher tasks.
- Expired, fabricated, or cross-role session IDs must not reveal another user's records — test auth and ownership boundaries in the account task.
- Duplicate/replayed appointment requests, parallel model disagreement/timeouts, and unavailable browser speech must not imply success — test idempotent status, isolated adapter failures, uncertainty outcomes, and explicit unavailable states in the owning tasks.

---

## File Structure

- `backend/swasthyaai/main.py` — FastAPI app construction and router registration.
- `backend/swasthyaai/config.py` — local/demo settings and dataset path configuration.
- `backend/swasthyaai/db.py` — SQLite connection and schema initialization.
- `backend/swasthyaai/api/` — versioned API routes for health, agent, auth, patient, clinician, appointments, reminders, education, and model status.
- `backend/swasthyaai/agent/` — public contract, session state, deterministic safety, model adapters, concurrent dispatcher/arbiter, and caregiver matching.
- `backend/swasthyaai/datasets.py` — dataset manifest loading and compatibility validation; never stores raw datasets in Git.
- `backend/swasthyaai/providers/gemini.py` — optional, consent-gated Gemini wording adapter.
- `backend/swasthyaai/services/` — auth, records, discovery, appointment, reminders, and education operations.
- `backend/swasthyaai/models/` — Pydantic request/response contracts and DB row models kept separate by purpose.
- `backend/tests/` — isolated unit tests and API contract/authorization tests.
- `frontend/src/` — typed API client, route/layout, feature views, reusable accessible primitives, styling, and browser speech hooks.
- `frontend/e2e/` — end-to-end flows for patient triage and demo coordination.
- `docs/` — setup, model/dataset inventory, API examples, limitations, and privacy boundaries.

### Task 1: Runnable API and web foundations

**Files:**
- Create: `backend/requirements.txt`, `backend/swasthyaai/__init__.py`, `backend/swasthyaai/main.py`, `backend/swasthyaai/config.py`, `backend/swasthyaai/db.py`, `backend/swasthyaai/api/health.py`, `backend/tests/test_health.py`
- Create: `frontend/package.json`, `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`, `frontend/src/styles.css`, `frontend/vite.config.ts`
- Modify: `.gitignore`

**Interfaces:**
- `create_app() -> FastAPI` registers `/api/v1/health` and app routers.
- `get_settings() -> Settings` reads local config without logging secrets.
- `init_db(path: str) -> None` creates the local demo schema directory/database.
- `GET /api/v1/health -> {"status":"ok","mode":"demo"}`.

- [ ] **Step 1: Add failing API health test** in `backend/tests/test_health.py`; assert status 200 and exact JSON shape.
- [ ] **Step 2: Run `pytest backend/tests/test_health.py -q`** and confirm it fails because the app/route is absent.
- [ ] **Step 3: Add the minimal FastAPI app, config, and SQLite initializer** with explicit demo defaults and no startup side effects outside the configured data directory.
- [ ] **Step 4: Run the health test** and verify it passes.
- [ ] **Step 5: Scaffold the Vite client and verify the app shell starts** with `npm run build`; use a light responsive foundation and honor reduced motion.
- [ ] **Step 6: Run backend and frontend checks, then commit/push only the foundation files.**

### Task 2: Safe agent, matching, and compatibility endpoint

**Files:**
- Create: `backend/swasthyaai/agent/{__init__,contracts,safety,state,models,dispatcher,matcher,service}.py`, `backend/swasthyaai/datasets.py`, `backend/swasthyaai/providers/gemini.py`, `backend/requirements-gemini.txt`
- Create: `backend/swasthyaai/api/agent.py`, `backend/tests/agent/{test_safety,test_state,test_matcher,test_service,test_dispatcher}.py`, `backend/tests/{test_agent_api,test_datasets}.py`
- Modify: `backend/swasthyaai/main.py`, `backend/app.py` (preserve legacy `/assess` route and compatible response keys)

**Interfaces:**
- `run_healthcare_agent(session_id: str, user_message: str, context: dict | None = None) -> AgentResponse`.
- `detect_red_flags(text: str) -> list[str]`.
- `rank_caregivers(caregivers: list[Caregiver], care_type: CareType, location: Location | None, language: Language) -> list[CaregiverMatch]`.
- `ModelAdapter.predict(text: str, context: dict) -> Awaitable[ModelResult]`; adapters declare task, languages, input/output schema, and timeout.
- `run_relevant_models(registry: ModelRegistry, request: AgentInput) -> list[ModelResult]` starts every matching adapter concurrently, isolates per-model errors/timeouts, and never dispatches unrelated capabilities.
- `aggregate_triage(results: list[ModelResult]) -> AggregatedTriage` returns `agreed`, `single_model`, `disagreement`, or `fallback`; compatible results may be combined only under the task's configured rule, and disagreement/low confidence requires human review.
- `load_dataset_manifests(directory: Path) -> list[DatasetManifest]`; `compatible_datasets(items: list[DatasetManifest], task: str) -> list[list[DatasetManifest]]` groups only compatible task/schema/language/license manifests.
- `AgentInput.external_ai_consent: bool = False` is an explicit per-turn consent field; no provider call occurs unless it is true.
- `GeminiWordingAdapter.rephrase(result: AgentResponse, consent: bool) -> str | None` is disabled without `GEMINI_API_KEY` or consent; its text cannot mutate structured fields.
- `ModelRegistry.status() -> list[ModelStatus]` reports model and dataset metadata without secrets or raw paths.
- `POST /api/v1/agent/turn` accepts bounded input and returns the spec's `AgentResponse` schema including per-model statuses.

- [ ] **Step 1: Write failing tests** for English/Hindi/Hinglish red flags, emergency override/no matches, non-emergency follow-up, two-question stop, parallel dispatch, isolated timeout/failure, task mismatch, compatible/incompatible dataset manifests, aggregation disagreement, and Gemini disabled/consent behavior.
- [ ] **Step 2: Run focused tests and confirm expected failures** before implementation.
- [ ] **Step 3: Implement deterministic emergency handling and typed response contracts.** Emergency always exits before model invocation and returns 112 guidance.
- [ ] **Step 4: Implement session state with at most two follow-ups total** and return human-review fallback after exhaustion.
- [ ] **Step 5: Implement eligibility-first caregiver filtering and both ranking formulas.** Test that ineligible candidates are never returned; expose score factors in reasons.
- [ ] **Step 6: Implement concurrent capability-aware dispatch and task-specific aggregation.** Every applicable adapter starts in one turn; timeout/failure is isolated, schemas are validated, and disagreement or low confidence returns human review instead of a blind average.
- [ ] **Step 7: Implement dataset manifest compatibility checks** for task, labels/schema, language, license, and provenance; only compatible manifests are grouped for a task.
- [ ] **Step 8: Add the optional Gemini wording adapter** with a local environment key, explicit consent gate, request timeout, output-only wording scope, and deterministic template fallback.
- [ ] **Step 9: Add `/api/v1/agent/turn` and adapt the legacy `/assess` route without removing its legacy fields.**
- [ ] **Step 10: Run agent/API, dispatcher, dataset, and Gemini tests plus holdout evaluation over synthetic data; document non-clinical status; commit/push this increment.**

### Task 3: Demo accounts, records, discovery, and coordination

**Files:**
- Create: `backend/swasthyaai/services/{auth,records,discovery,appointments,reminders}.py`
- Create: `backend/swasthyaai/api/{auth,patient,clinician,appointments,reminders}.py`
- Create: `backend/swasthyaai/models/{auth,records,appointments}.py`
- Create: `backend/tests/api/{test_auth,test_records,test_discovery,test_appointments,test_reminders}.py`
- Modify: `backend/swasthyaai/db.py`, `backend/swasthyaai/main.py`

**Interfaces:**
- `create_user(email: str, password: str, role: Literal["patient", "clinician"]) -> User`.
- `authenticate(email: str, password: str) -> Session` and `require_role(*roles)` dependency.
- Record endpoints scope reads/writes to the authenticated patient or explicitly authorized clinician.
- `POST /api/v1/appointments -> Appointment(status="requested")`; no endpoint returns `confirmed` without an integration.

- [ ] **Step 1: Write failing auth tests** for registration, login, logout, invalid credentials, role access, and expired sessions.
- [ ] **Step 2: Implement password hashing and opaque server-side sessions** using well-maintained dependencies; store only session-token digests.
- [ ] **Step 3: Write failing ownership tests** for cross-patient records, unauthorized clinician access, and role mismatch.
- [ ] **Step 4: Implement patient-owned demo record CRUD** for history, allergies, medications, and report metadata; do not implement file uploads.
- [ ] **Step 5: Write and implement caregiver/clinician discovery tests** for filters, languages, specialties, availability, and no-coordinate behavior.
- [ ] **Step 6: Write and implement appointment and reminder CRUD tests**; ensure appointment status remains `requested` and reminder delivery is in-app/demo only.
- [ ] **Step 7: Run all API and authorization tests; commit/push this increment.**

### Task 4: Patient/clinician frontend and dashboard flows

**Files:**
- Create: `frontend/src/{app,components,features,styles}/...` with focused modules for navigation, chat, dashboard, records, appointments, discovery, and reminders.
- Create: `frontend/src/api/{agent,auth,records,appointments,discovery}.ts`, `frontend/e2e/{triage,patient-records,appointments}.spec.ts`
- Modify: `frontend/src/App.tsx`, `frontend/src/styles.css`, `frontend/package.json`

**Interfaces:**
- Typed API client functions mirror `/api/v1` request/response schemas and return explicit API errors.
- Route guards consume authenticated role; UI guards supplement but never replace backend authorization.

- [ ] **Step 1: Add failing UI/API-client tests** for response parsing, safe error display, and role-gated navigation.
- [ ] **Step 2: Implement patient and clinician layouts** with a calm light palette, responsive navigation, readable hierarchy, and reduced-motion support.
- [ ] **Step 3: Implement conversational triage UI** for follow-up, emergency, decision, and unavailable states; display emergency guidance without animation delay.
- [ ] **Step 4: Implement dashboard, record, discovery, appointment-request, and reminder flows** against the versioned API; visibly label synthetic/demo content.
- [ ] **Step 5: Add keyboard and accessible-label checks plus end-to-end happy/failure flows.**
- [ ] **Step 6: Run `npm test` and `npm run build` plus backend API tests; commit/push this increment.**

### Task 5: Education, browser voice, and model capability status

**Files:**
- Create: `backend/swasthyaai/api/{education,models}.py`, `backend/swasthyaai/services/education.py`, `backend/tests/api/{test_education,test_models}.py`
- Create: `frontend/src/features/{education,voice,models}/...`, `frontend/e2e/education.spec.ts`
- Modify: `backend/swasthyaai/main.py`, `frontend/src/App.tsx`

**Interfaces:**
- `GET /api/v1/models -> list[ModelStatus]` includes registered models and reports unsupported capabilities as unavailable; `GET /api/v1/datasets -> list[DatasetManifestSummary]` returns safe metadata only.
- `GET /api/v1/education/cases` returns explicitly synthetic learning cases.
- Gemini provider status reports `disabled`, `ready`, or `unavailable`; it never reveals the API key.
- Browser voice interface returns recognized text or a typed `unsupported`/`permission_denied` result and always permits text entry.

- [ ] **Step 1: Test empty model registry, dataset metadata privacy, Gemini disabled/key-unavailable status, and unsupported capability responses.**
- [ ] **Step 2: Implement education case APIs and tests** using synthetic cases only.
- [ ] **Step 3: Add browser speech recognition/synthesis best-effort support** for `hi-IN` and `en-IN`, with permission/error handling and text fallback; do not claim reliable Hinglish recognition.
- [ ] **Step 4: Add model-status and education views**; show image/report analysis as unavailable unless a real adapter is registered and validated.
- [ ] **Step 5: Test supported/unsupported browser paths and build; commit/push this increment.**

### Task 6: Documentation and release verification

**Files:**
- Create/modify: `README.md`, `docs/setup.md`, `docs/api.md`, `docs/models-and-data.md`, `docs/safety-and-limitations.md`, `backend/tests/test_end_to_end.py`, `frontend/e2e/`.

**Interfaces:**
- Document exact setup/run commands, local data configuration, API schemas/errors, adapter registration, and known limitations.

- [ ] **Step 1: Add integration tests** for normal, ambiguous, incomplete, unsupported language, urgent, unavailable model, records ownership, and appointment request paths.
- [ ] **Step 2: Run full backend test suite and frontend tests/build** from documented clean setup commands.
- [ ] **Step 3: Verify `.gitignore` excludes local datasets, models, SQLite databases, secrets, and uploads; inspect `git status` and staged diff.**
- [ ] **Step 4: Update setup/API/model/data/safety docs with verified behavior only.**
- [ ] **Step 5: Commit/push final docs and verification changes; report commit hashes and any skipped capability.**

## Spec Coverage Self-Review

- Agent workflow, state, follow-up cap, output contract, emergency controls, multilingual fallback, concurrent model dispatch/arbitration, compatible dataset integration, optional Gemini guardrails, matching/explanations, data limits, and agent tests: Task 2.
- Doctor discovery, profile/role boundaries, appointments, records, reminders, and ownership: Task 3.
- Responsive animated dashboard, conversational UX, accessibility, and reduced motion: Task 4.
- Education, voice limitations, model/dataset/provider status, and unsupported report/image states: Task 5.
- Setup, APIs, dependencies/data inventory, safe limitations, full validation, and ignore rules: Tasks 1 and 6.
- Review Focus risks have direct test coverage in Tasks 2, 3, 4, and 5 as identified above.
- The existing standalone `backend/app.py` is retained as a compatibility surface until its `/assess` contract tests pass; only the agent task modifies it.
