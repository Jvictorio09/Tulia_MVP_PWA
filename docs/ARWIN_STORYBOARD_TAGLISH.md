# Tulia Storyboard (Taglish, Friendly) – Para kay Arwin

Goal: Ipakita kung paano gagana ang app end-to-end, saan papasok ang RAG (AI Coach), at paano siya mag-iinteract sa Learn flow at sa speech feedback. Conversational Taglish para mabilis i-share sa team.

---

## Personas
- Learner (Juan/Anna): gustong ma-improve ang high‑stakes communication skills.
- AI Coach (Tulia Coach): nagbibigay ng sagot, tips, at feedback (via RAG + prompts).

---

## Learn vs AI Coach (Ano pinagkaiba?)
- Learn: Ito ang structured path – Levels → Units → Lessons → Exercises. Guided practice.
- AI Coach: On-demand helper. Puwede mong tanungin: “Explain RICE,” “Give me a hint,” or “How to improve my intro?”

Think: Learn = courses/lesson flow. AI Coach = helper/guide na may citations galing sa Tulia content.

---

## High-Level Flow
1) Onboarding → pick goal + daily minutes → create profile.
2) Home (City View) → makikita streak, quests, at Level 1 card.
3) Enter Lesson → do exercises (select, match, rewrite, etc.).
4) Need help? Click AI Coach → send query to RAG → receive answer + citations.
5) Milestone (speech) → record → get rubric-based feedback (clarity, structure, presence, influence).
6) XP + rewards → streak update → balik sa next lesson.

---

## Where does RAG fit?
- Inside Lesson: “Explain this,” “Give me a hint,” or “Summarize tip sheet.”
- Outside Lesson: General Q&A about concepts within your level.
- Webhook Design: App → n8n (trigger) → n8n → App (answer), with HMAC signature.

---

## Scenes (Step-by-step)

### Scene 1: Onboarding (1 min)
- UI: Simple form. “What’s your goal?” “Daily goal (5/10/15 mins)?”
- Result: Create profile; show Level 1 unlocked.

### Scene 2: Home (City)
- Copy: “Ready ka na for Level 1: Awareness & Foundations.”
- CTA: “Start Lesson 1.”

### Scene 3: Lesson Runner – Concept Intro
- Content: Brief explainer + tip sheet snippet.
- Button: “AI Coach: Explain this.”
- Action: App sends POST to `N8N_RAG_WEBHOOK_URL` with filters (level=1, lesson=1).
- Expect: Answer with citations (e.g., Lesson 1 Notes). If queued, UI shows “Thinking…” then updates.

### Scene 4: Exercise – Select/Match/Rewrite
- Learner tries. If nahihirapan → click “Give me a hint.”
- App sends `type=lesson_help` with lesson filter.
- Reply: Short hint, 1–2 citations, encourage try-again.

### Scene 5: Milestone – Speech Recording (30s Intro)
- Learner records. App processes audio (ASR → text).
- AI Coach feedback (prompted on rubric):
  - “Clarity: …”
  - “Structure: …”
  - “Presence: …”
  - “Influence: …”
- Output: Actionable tips + 1 citation (rubric/tip sheet). Score + XP.

### Scene 6: Rewards + Next Step
- Show XP earned, coins, updated streak.
- Suggest next lesson or optional AI Coach Q&A.

---

## Sample Microcopy (Taglish)
- AI Coach button: “Tulungan mo ‘ko dito” / “Explain this”
- Loading: “Saglit lang, tinitignan ko notes…”
- Hint style: “Try mong i-compare ‘Impact’ vs ‘Risk’ gamit ang RICE.”
- Refusal (out of scope): “Wala sa lesson natin ‘yan. Gusto mo bang tingnan ang tip sheet?”

---

## Observability & Guardrails (quick)
- Each AI Coach call: store request_id, user_hash, filters, latency, cost.
- Rate limits: 5/min, 20/day per user.
- Safety: If walang context match, say “di ko sure” + citation to tip sheet.

---

## Educational Pillar Overview (6 Levels)

| Level | Focus | Core Skills | Sample Milestone | Coach Persona |
|-------|-------|-------------|-------------------|----------------|
| 1 | Awareness & Foundations | High-stakes comms, audience psychology, clarity | 30-sec self-intro (pitch) | Philosopher / Senator / Merchant |
| 2 | Message Crafting | Structure + storytelling + emotional rhythm | 90-sec structured story | Storyteller / Town Leader |
| 3 | Delivery & Presence | Voice, body language, nerves | 2-min persuasive talk | Actor / Comedian / Parliament Speaker |
| 4 | Strategic Influence | Read the room, framing, persuasion | Reframe proposal convincingly | CEO / Diplomat |
| 5 | Negotiation & Impact | Trust, empathy, assertive persuasion | 5-min negotiation sim | Statesman / Investor |
| 6 | Integration & Mastery | Inspire & mobilize action | 3-5 min signature talk | TED Coach / AI Holo-Mentor |

---

## RAG Content Sources (Support Content Library)

| Tag / Topic | Reference Block | Used For |
|-------------|------------------|----------|
| Persuasion / Structure | Aristotle – Rhetoric | Golden Principle, message checks |
| Presence / State | Amy Cuddy – Presence | Preparation (Mind) |
| Clarity / Hook | Chris Anderson – TED Talks | Definition & Contrast |
| Story Arc / Visuals | Nancy Duarte – Resonate | Message crafting preview |
| Purpose / Why | Simon Sinek – Start with Why | Opening hooks |
| Emotional Regulation | Daniel Goleman – EQ | Preparation (Mind) |
| Frameworks | STAR, Ethos-Pathos-Logos | Exercises & feedback |
| Proprietary Anchors | High-Stakes Equation™, Preparation Ritual™ | Core difficulty engine |

Each block ≈ 120 words + tags + exercise seeds for RAG vector index.

---

## Implementation Priorities for Arwin

### Priority 1 (Core RAG Infrastructure)
- Build `/api/rag/query` + `/api/rag/lesson_help` triggers
- Handle `/api/hooks/rag/answer|error` with HMAC signature
- Create FAISS vector store with Level 1 content blocks
- Implement basic retrieval (top-k=6, MMR rerank)

### Priority 2 (Lesson Integration)
- Add lesson widget (Explain/Hint buttons) to lesson runner
- Implement queued/loading states + citations modal
- Create lesson-specific prompt templates
- Add rate limiting (5/min, 20/day per user)

### Priority 3 (Milestone Feedback)
- Build milestone feedback prompt template aligned to rubric
- Implement speech-to-text → RAG → rubric scoring pipeline
- Add 4-pillar feedback (clarity, structure, presence, influence)
- Create actionable tips with citations

### Priority 4 (Content Expansion)
- Seed remaining levels (2-6) with coach personas
- Expand Support Content Library with tagged blocks
- Add proprietary frameworks (High-Stakes Equation™, Preparation Ritual™)
- Implement content versioning and updates

### Priority 5 (Advanced Features)
- Add semantic caching for common queries
- Implement evaluation harness with golden set
- Create admin dashboard for RAG metrics
- Add hybrid search (BM25 + embeddings)

---

## Sample RAG Response Format

```json
{
  "answer": "Clarity could improve by simplifying your main message into one 'Why'.",
  "citations": [
    {"id": "sinek_why", "title": "Simon Sinek – Start with Why", "snippet": "People don't buy what you do..."},
    {"id": "aristotle_rhetoric", "title": "Aristotle – Rhetoric", "snippet": "The art of persuasion..."}
  ],
  "rubric": {"clarity": 7, "structure": 8, "presence": 6, "influence": 7},
  "next_action": "Try the Preparation Ritual™ before your next recording",
  "related_lessons": ["lesson_1_2", "lesson_1_3"]
}
```

---

## Quick Success Criteria
- Learner can press "Explain this" → gets 2–3 sentence answer with 1–2 citations < 2s P95 (cached)
- Hint returns within lesson context with actionable advice
- Milestone feedback lists the 4 rubric pillars with 1 actionable tip each
- RAG responses stay within scope (refuse out-of-lesson topics)
- All responses include proper citations to Support Content Library
