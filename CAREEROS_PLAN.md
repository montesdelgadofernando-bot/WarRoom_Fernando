# CareerOS Full System Plan

## 1) Vision and Product Scope
CareerOS is an AI-native career operating system that helps professionals discover goals, build execution plans, practice skills, and prove outcomes with measurable artifacts.

### Core value propositions
- **Career strategy in one place:** goals, role targets, skill gaps, and progression plan.
- **Execution engine:** weekly actions, habits, interview prep, networking, and portfolio milestones.
- **Proof of growth:** evidence vault, quantified wins, and readiness scores.
- **Adaptive coaching:** personalized guidance from user signals and outcomes.

## 2) Target Users and Jobs-to-be-Done

### Primary segments
1. **Career switchers** (e.g., operations to product).
2. **Early-career builders** (0–5 years experience).
3. **Mid-career accelerators** (IC to manager transition).
4. **Leaders in transition** (manager to director/VP).

### Jobs-to-be-done
- Define a realistic target role and map skill gaps.
- Build a practical 30/60/90-day plan with milestones.
- Practice communication and interview scenarios.
- Track progress and generate promotion-ready narratives.

## 3) Product Modules (MVP → V2)

### MVP modules
1. **Identity + onboarding**
   - Profile, career stage, preferred industries, constraints, availability.
2. **Career diagnostic**
   - Baseline assessment on skills, experience, outcomes, confidence.
3. **Goal and roadmap builder**
   - Target role, timeline, skill-gap map, weekly plan.
4. **Learning and practice hub**
   - Curated learning paths, micro-drills, scenario practice.
5. **Execution tracker**
   - Tasks, streaks, checkpoints, progress score.
6. **Evidence vault**
   - STAR stories, quantified wins, project outcomes.
7. **Coach chat**
   - AI guidance anchored to user profile + history.
8. **Analytics dashboard**
   - Readiness score, consistency trend, milestone completion.

### V2 modules
- Mentor marketplace and peer accountability pods.
- Resume/LinkedIn optimization and auto-tailored narratives.
- Job matching and application copilot.
- Team/enterprise portal for internal mobility programs.

## 4) System Architecture

### Front-end
- **Web app:** Streamlit for rapid iteration (current codebase), then optional React migration after PMF.
- **State management:** Session state for immediate interactions + persistent backend state.
- **UI primitives:** Reusable cards for goals, practice sessions, evidence, and analytics.

### Backend services
- **User profile service** (profile, preferences, permissions).
- **Assessment service** (rubrics, test sessions, scoring).
- **Planning service** (goal generation, weekly roadmap, recalibration).
- **Coaching service** (LLM orchestration, memory retrieval, guardrails).
- **Progress service** (tasks, events, streaks, KPIs).
- **Artifact service** (evidence vault, documents, interview stories).

### Data layer
- **Operational DB:** Firestore collections for users, plans, tasks, sessions, artifacts.
- **Analytics store:** Daily aggregates for cohort and individual insights.
- **Vector memory (optional in V2):** retrieval of user history and evidence snippets.

### Integrations
- LLM providers (Gemini/OpenAI/Anthropic adapter pattern).
- Calendar APIs for schedule-aware planning.
- Learning content providers (courses/articles).
- ATS/job board APIs (V2).

## 5) Data Model Blueprint

### Key entities
- `User` (identity, stage, role goals, constraints).
- `Assessment` (type, questions, scores, dimension-level feedback).
- `CareerPlan` (horizon, milestones, skills, dependencies).
- `WeeklySprint` (tasks, commitments, completion, blockers).
- `PracticeSession` (scenario, transcript, score, rubric feedback).
- `EvidenceItem` (STAR draft, metric, context, link/file).
- `ReadinessScore` (dimension scores + confidence + trend).

### Collection strategy for Firestore
- `/users/{userId}`
- `/users/{userId}/assessments/{assessmentId}`
- `/users/{userId}/plans/{planId}`
- `/users/{userId}/weekly_sprints/{sprintId}`
- `/users/{userId}/practice_sessions/{sessionId}`
- `/users/{userId}/evidence/{evidenceId}`
- `/users/{userId}/readiness/{snapshotId}`

## 6) AI Orchestration Design

### Prompting and control
- Use role-specific system prompts (career coach, interviewer, planner).
- Structured outputs (JSON schema) for deterministic rendering.
- Ground responses in user profile and progress snapshots.

### Safety and quality
- Input/output moderation.
- Hallucination controls with retrieval constraints.
- Explainability notes for high-impact recommendations.

### Evaluation framework
- Offline eval sets for advice quality and actionability.
- Rubric-based scoring for coaching outputs.
- Human review loop for edge cases.

## 7) Security, Privacy, and Compliance
- Least-privilege access to user data.
- Encryption in transit and at rest.
- Signed audit events for key actions.
- Data retention controls and export/delete flows.
- Consent management for AI personalization.

## 8) Metrics and Success Criteria

### North-star metric
- **Weekly Career Progress Rate (WCPR):** % users completing at least 3 high-impact actions/week.

### Supporting metrics
- Activation rate (onboarding → first plan).
- 4-week retention.
- Practice completion rate.
- Evidence items created/user.
- Readiness score improvement over 8 weeks.

## 9) Implementation Roadmap (16 Weeks)

### Phase 0 (Week 1–2): Foundations
- Define product requirements and UX wireframes.
- Normalize current Streamlit architecture into modular files.
- Set up environment config, secrets, and telemetry.

### Phase 1 (Week 3–6): MVP Core
- Build profile + onboarding + diagnostic engine.
- Implement career plan generator and weekly sprint tracker.
- Add persistence model for plans, tasks, and assessments.

### Phase 2 (Week 7–10): Coaching + Practice
- Add AI coach chat with context retrieval.
- Build scenario practice with rubric scoring.
- Implement evidence vault and STAR artifact generation.

### Phase 3 (Week 11–13): Analytics + Reliability
- Release readiness dashboard and trend insights.
- Add error tracking, retries, and quality monitors.
- Introduce admin controls for content/rubric updates.

### Phase 4 (Week 14–16): Launch Readiness
- Growth loops: reminders, weekly digest, re-engagement flows.
- Security review and data governance checks.
- Beta launch with feedback instrumentation.

## 10) Engineering Workstreams
1. **Platform:** auth, data model, config, observability.
2. **AI systems:** orchestration, prompt registry, eval tooling.
3. **Product features:** onboarding, planning, coaching, evidence.
4. **Data and analytics:** events, dashboards, cohort analysis.
5. **Quality:** test automation, regression suites, release checklist.

## 11) Risks and Mitigations
- **Risk:** Generic AI advice lowers user trust.
  - **Mitigation:** context-rich prompts + rubric checks + user feedback loop.
- **Risk:** Scope creep delays launch.
  - **Mitigation:** strict MVP boundaries and milestone-based gates.
- **Risk:** Weak retention after onboarding.
  - **Mitigation:** weekly sprint rituals, reminders, and milestone celebration.

## 12) Immediate Next 10 Tasks
1. Break `app.py` into modules (`ui`, `services`, `models`, `data`).
2. Define typed schemas for the entities above.
3. Build onboarding + diagnostic screens in isolated components.
4. Implement plan generation service with structured output parser.
5. Add weekly sprint CRUD and completion tracking.
6. Create evidence vault schema and upload/link support.
7. Build readiness score computation with explainable factors.
8. Add instrumentation events for key user actions.
9. Create regression tests for core user journeys.
10. Run closed beta with 20 users and collect qualitative feedback.
