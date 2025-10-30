# N8N API Specification for Arwin

## Overview
This document defines the exact API calls that Tulia will make to n8n and the expected JSON responses. All communication uses HMAC-SHA256 signatures for security.

---

## Security Headers (Required for all calls)

### Outgoing (Tulia → n8n)
```
X-Timestamp: <unix_timestamp>
X-Signature: <hmac_sha256_hex>
Content-Type: application/json
```

### Incoming (n8n → Tulia)
```
X-Timestamp: <unix_timestamp>
X-Signature: <hmac_sha256_hex>
Content-Type: application/json
```

**HMAC Calculation:**
```python
import hmac, hashlib
secret = "DJANGO_WEBHOOK_SIGNING_SECRET"
message = f"{timestamp}.{raw_body}"
signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
```

---

## API Endpoints

### 1. RAG Query Trigger
**Endpoint:** `POST ${N8N_RAG_WEBHOOK_URL}`

**Purpose:** General Q&A about lessons, concepts, or content

**Request Body:**
```json
{
  "request_id": "uuid-v4",
  "type": "query",
  "query": "What is the RICE framework?",
  "filters": {
    "level": 1,
    "unit": 1,
    "lesson": 1,
    "scope": "Lessons|Exercises|TipSheets|All"
  },
  "user_hash": "u_abc123",
  "session_id": "s_def456",
  "retrieval": {
    "top_k": 6,
    "mmr_lambda": 0.5
  }
}
```

**Expected Response (Success):**
```json
{
  "request_id": "uuid-v4",
  "type": "query",
  "query": "What is the RICE framework?",
  "filters": {
    "level": 1,
    "unit": 1,
    "lesson": 1
  },
  "answer": "RICE stands for Risk, Impact, Control, and Expectations. It's a framework for assessing communication stakes. Risk = what could go wrong, Impact = consequences, Control = your influence, Expectations = what others expect from you.",
  "citations": [
    {
      "id": "lesson_1_2",
      "title": "Stakes Assessment Framework",
      "url": null,
      "loc": "tip_sheet",
      "snippet": "Use the RICE framework: Risk (what could go wrong), Impact (consequences), Control (your influence), and Expectations (what others expect)."
    },
    {
      "id": "aristotle_rhetoric",
      "title": "Aristotle – Rhetoric",
      "url": null,
      "loc": "persuasion_principles",
      "snippet": "The art of persuasion requires understanding your audience's expectations and the stakes involved."
    }
  ],
  "usage": {
    "model": "gpt-4o-mini",
    "prompt_tokens": 512,
    "completion_tokens": 120,
    "total_tokens": 632
  },
  "latency_ms": 812,
  "cost_usd": 0.0016,
  "retrieval": {
    "top_k": 6,
    "mmr_lambda": 0.5,
    "sources_found": 4
  },
  "observability": {
    "trace_id": "trace_789",
    "logs_url": null
  },
  "ts": "2025-01-28T13:45:10Z"
}
```

---

### 2. Lesson Help Trigger
**Endpoint:** `POST ${N8N_RAG_WEBHOOK_URL}`

**Purpose:** Contextual hints for specific lessons or exercises

**Request Body:**
```json
{
  "request_id": "uuid-v4",
  "type": "lesson_help",
  "query": "I'm stuck on this exercise",
  "filters": {
    "level": 1,
    "unit": 1,
    "lesson": 1,
    "exercise_type": "select|match|rewrite|speak|scenario"
  },
  "user_hash": "u_abc123",
  "session_id": "s_def456",
  "retrieval": {
    "top_k": 4,
    "mmr_lambda": 0.7
  }
}
```

**Expected Response (Success):**
```json
{
  "request_id": "uuid-v4",
  "type": "lesson_help",
  "query": "I'm stuck on this exercise",
  "filters": {
    "level": 1,
    "unit": 1,
    "lesson": 1,
    "exercise_type": "select"
  },
  "answer": "Try comparing 'Impact' vs 'Risk' using the RICE framework. Impact focuses on consequences, while Risk focuses on what could go wrong. Think about which one has more weight in high-stakes situations.",
  "citations": [
    {
      "id": "lesson_1_2",
      "title": "Stakes Assessment Framework",
      "url": null,
      "loc": "exercise_hint",
      "snippet": "Impact measures consequences, Risk measures potential problems"
    }
  ],
  "usage": {
    "model": "gpt-4o-mini",
    "prompt_tokens": 380,
    "completion_tokens": 85,
    "total_tokens": 465
  },
  "latency_ms": 650,
  "cost_usd": 0.0012,
  "retrieval": {
    "top_k": 4,
    "mmr_lambda": 0.7,
    "sources_found": 2
  },
  "observability": {
    "trace_id": "trace_790",
    "logs_url": null
  },
  "ts": "2025-01-28T13:46:15Z"
}
```

---

### 3. Milestone Feedback Trigger
**Endpoint:** `POST ${N8N_RAG_WEBHOOK_URL}`

**Purpose:** Speech analysis and rubric-based feedback

**Request Body:**
```json
{
  "request_id": "uuid-v4",
  "type": "milestone_feedback",
  "query": "Analyze my 30-second introduction recording",
  "filters": {
    "level": 1,
    "milestone_id": "intro_30s",
    "rubric_type": "clarity_structure_presence_influence"
  },
  "user_hash": "u_abc123",
  "session_id": "s_def456",
  "transcript": "Hi, I'm Juan. I'm a software engineer with 5 years experience in building web applications. I'm passionate about creating user-friendly interfaces that solve real problems.",
  "retrieval": {
    "top_k": 8,
    "mmr_lambda": 0.6
  }
}
```

**Expected Response (Success):**
```json
{
  "request_id": "uuid-v4",
  "type": "milestone_feedback",
  "query": "Analyze my 30-second introduction recording",
  "filters": {
    "level": 1,
    "milestone_id": "intro_30s",
    "rubric_type": "clarity_structure_presence_influence"
  },
  "answer": "Your introduction shows good structure and clarity. Here's how to improve each pillar:",
  "citations": [
    {
      "id": "milestone_rubric_1",
      "title": "30-Second Introduction Rubric",
      "url": null,
      "loc": "rubric_guidelines",
      "snippet": "Clarity: Clear pronunciation, appropriate pace, easy to understand"
    },
    {
      "id": "cuddy_presence",
      "title": "Amy Cuddy – Presence",
      "url": null,
      "loc": "confidence_building",
      "snippet": "Presence comes from authentic confidence and clear communication"
    }
  ],
  "rubric_scores": {
    "clarity": 7,
    "structure": 8,
    "presence": 6,
    "influence": 7
  },
  "feedback_details": {
    "clarity": "Good pace and pronunciation. Consider simplifying technical terms for broader audiences.",
    "structure": "Excellent opening and clear progression. Well-organized information flow.",
    "presence": "Confident delivery. Try adding more energy and enthusiasm to your voice.",
    "influence": "Clear value proposition. Consider adding a memorable hook or personal story."
  },
  "next_action": "Try the Preparation Ritual™ before your next recording: Mind (visualize success), Message (simplify to one key point), Moment (breathe and ground yourself).",
  "usage": {
    "model": "gpt-4o-mini",
    "prompt_tokens": 720,
    "completion_tokens": 180,
    "total_tokens": 900
  },
  "latency_ms": 1200,
  "cost_usd": 0.0028,
  "retrieval": {
    "top_k": 8,
    "mmr_lambda": 0.6,
    "sources_found": 5
  },
  "observability": {
    "trace_id": "trace_791",
    "logs_url": null
  },
  "ts": "2025-01-28T13:47:30Z"
}
```

---

## Error Responses

### Generic Error Response
**Endpoint:** `POST /api/hooks/rag/error`

**Request Body:**
```json
{
  "request_id": "uuid-v4",
  "type": "query|lesson_help|milestone_feedback",
  "query": "What is the RICE framework?",
  "filters": {
    "level": 1
  },
  "error_code": "RATE_LIMIT_EXCEEDED|CONTENT_NOT_FOUND|MODEL_ERROR|TIMEOUT",
  "error_message": "Rate limit exceeded. Try again in 1 minute.",
  "ts": "2025-01-28T13:48:00Z"
}
```

### Rate Limit Error
```json
{
  "request_id": "uuid-v4",
  "type": "query",
  "query": "What is the RICE framework?",
  "filters": {
    "level": 1
  },
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_message": "Rate limit exceeded. You can make 5 requests per minute, 20 per day.",
  "retry_after_seconds": 60,
  "ts": "2025-01-28T13:48:00Z"
}
```

### Content Not Found Error
```json
{
  "request_id": "uuid-v4",
  "type": "query",
  "query": "How to cook pasta?",
  "filters": {
    "level": 1
  },
  "error_code": "CONTENT_NOT_FOUND",
  "error_message": "This topic is outside our lesson scope. Please ask about communication skills, lessons, or exercises.",
  "suggested_topics": ["RICE framework", "audience psychology", "clarity vs jargon"],
  "ts": "2025-01-28T13:48:00Z"
}
```

---

## Rate Limits & Constraints

### Per User Limits
- **Burst:** 5 requests per minute
- **Daily:** 20 requests per day
- **Reset:** Daily limit resets at midnight UTC

### Request Size Limits
- **Max query length:** 500 characters
- **Max transcript length:** 2000 characters
- **Timeout:** 25 seconds per request

### Content Scope
- **Allowed:** Lessons, exercises, tip sheets, rubrics, communication concepts
- **Blocked:** Personal information, unrelated topics, inappropriate content

---

## Testing Examples

### cURL Test for RAG Query
```bash
# Test RAG Query
curl -X POST "https://your-n8n-instance.com/webhook/rag" \
  -H "Content-Type: application/json" \
  -H "X-Timestamp: $(date +%s)" \
  -H "X-Signature: $(python -c "
import hmac, hashlib, time, os
secret = os.environ.get('DJANGO_WEBHOOK_SIGNING_SECRET', 'devsecret')
ts = str(int(time.time()))
body = '{\"request_id\":\"test-123\",\"type\":\"query\",\"query\":\"What is RICE?\",\"filters\":{\"level\":1},\"user_hash\":\"test_user\"}'
msg = (ts + '.' + body).encode()
print(hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest())
")" \
  -d '{
    "request_id": "test-123",
    "type": "query",
    "query": "What is RICE?",
    "filters": {
      "level": 1
    },
    "user_hash": "test_user",
    "session_id": "test_session",
    "retrieval": {
      "top_k": 6,
      "mmr_lambda": 0.5
    }
  }'
```

### Expected Test Response
```json
{
  "request_id": "test-123",
  "type": "query",
  "query": "What is RICE?",
  "filters": {
    "level": 1
  },
  "answer": "RICE stands for Risk, Impact, Control, and Expectations...",
  "citations": [
    {
      "id": "lesson_1_2",
      "title": "Stakes Assessment Framework",
      "url": null,
      "loc": "tip_sheet",
      "snippet": "Use the RICE framework..."
    }
  ],
  "usage": {
    "model": "gpt-4o-mini",
    "prompt_tokens": 400,
    "completion_tokens": 100,
    "total_tokens": 500
  },
  "latency_ms": 750,
  "cost_usd": 0.0015,
  "retrieval": {
    "top_k": 6,
    "mmr_lambda": 0.5,
    "sources_found": 3
  },
  "observability": {
    "trace_id": "trace_test_123",
    "logs_url": null
  },
  "ts": "2025-01-28T13:50:00Z"
}
```

---

## Implementation Notes for Arwin

### Required Environment Variables
```bash
DJANGO_WEBHOOK_SIGNING_SECRET=your-32-char-secret-here
N8N_RAG_WEBHOOK_URL=https://your-n8n-instance.com/webhook/rag
N8N_TIMEOUT_SECONDS=25
RAG_RATE_LIMIT_PER_MIN=5
RAG_RATE_LIMIT_PER_DAY=20
```

### Response Handling
1. **Success (200):** Process answer, citations, and metrics
2. **Queued (202):** Store request_id, poll for status
3. **Error (4xx/5xx):** Log error, show user-friendly message

### Idempotency
- Use `request_id` to prevent duplicate processing
- Store responses in database with `request_id` as unique key
- Return cached response if `request_id` already exists

This specification provides everything Arwin needs to implement the n8n integration with proper error handling, security, and response formatting.
