# Implementation Plan: Personal Health Connect
## Django + HTMX Rebuild

This document outlines the plan to rebuild the personal health connect features (from the React prototype) using Django + HTMX to integrate with the existing thrive-prototypes codebase.

---

## Overview

**Goal**: Create a patient-facing personal health record (PHR) interface within the existing Django + HTMX application, following the product vision defined in [PRD.md](./PRD.md).

**Key Principles**:
- Reuse existing Django architecture (models, services, permissions)
- Leverage HTMX for dynamic interactions (instead of React)
- Integrate with existing LLM services (already using Claude/Gemini)
- Share models between provider and patient interfaces where possible
- Maintain separate UX patterns for patient vs provider experiences

---

## Architecture Strategy

### 1. Django App Structure

Create a new Django app: `sandwich/personal/`

```
sandwich/personal/
├── __init__.py
├── urls.py              # Patient-facing URL routes (/personal/...)
├── views.py             # HTMX-powered views
├── services/
│   ├── chat.py          # Chat assistant logic
│   ├── extraction.py    # Health data extraction from documents/text
│   └── summarization.py # Health summary generation
├── templates/personal/
│   ├── base.html        # Patient interface base template
│   ├── dashboard.html   # Main 3-panel layout
│   ├── chat.html        # Chat interface
│   ├── records.html     # Health records panel
│   └── feed.html        # Feed/summary panel
└── static/personal/
    ├── css/
    └── js/
```

### 2. Reuse Existing Models

The existing `sandwich/core/` and `sandwich/patients/` apps already have health record models:
- `Patient` - patient records
- `Document` - uploaded documents
- `Encounter` - visit records

**Strategy**: Extend these models with new fields needed for personal health connect, or create complementary models for patient-entered data.

Potential new models in `sandwich/personal/models.py`:
```python
class PersonalHealthRecord(models.Model):
    """Patient-entered health records (medications, conditions, etc.)"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    record_type = models.CharField(...)  # medication, condition, allergy, etc.
    data = models.JSONField()  # Structured health data
    source = models.CharField(...)  # chat, document, manual
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    """Chat conversation history"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    role = models.CharField(...)  # user, assistant
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class HealthSummary(models.Model):
    """Generated health summaries"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    summary_type = models.CharField(...)  # overall, update, insight
    content = models.TextField()
    source_records = models.JSONField()  # Links to source data
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3. LLM Integration

**Good News**: The codebase already uses Claude/Gemini for document processing!
- Located in: `sandwich/core/services/ingest/`
- Can reuse the LLM client setup and patterns

Create new services in `sandwich/personal/services/`:

```python
# chat.py
async def process_chat_message(message: str, patient: Patient) -> dict:
    """
    Process user message and extract health data
    - Call Claude API with structured extraction prompt
    - Parse response into health records
    - Generate conversational response
    """

# extraction.py
async def extract_from_document(document: Document) -> list[dict]:
    """
    Extract structured health data from uploaded document
    - Reuse existing document text extraction
    - Call Claude with health data extraction schema
    - Return structured records
    """

# summarization.py
async def generate_health_summary(patient: Patient) -> str:
    """
    Generate AI summary of patient's complete health record
    - Gather all health records
    - Call Claude to generate natural language summary
    - Include relevant context and insights
    """
```

### 4. HTMX Interaction Patterns

**Chat Interface**:
```html
<!-- Chat input form -->
<form hx-post="/personal/chat"
      hx-target="#chat-messages"
      hx-swap="beforeend"
      hx-on::after-request="this.reset()">
  <input type="text" name="message" />
  <button type="submit">Send</button>
</form>

<!-- Chat messages container -->
<div id="chat-messages">
  <!-- Messages loaded here -->
</div>
```

**Health Records Panel**:
```html
<!-- Records list with HTMX search -->
<input type="search"
       name="q"
       hx-get="/personal/records/search"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#records-list">

<div id="records-list">
  <!-- Record cards loaded here -->
</div>
```

**Feed Panel (with SSE)**:
```html
<!-- Real-time feed updates using Server-Sent Events -->
<div hx-ext="sse"
     sse-connect="/personal/feed/stream"
     sse-swap="feed-update"
     hx-target="#feed-cards"
     hx-swap="afterbegin">
  <div id="feed-cards">
    <!-- Feed cards loaded here -->
  </div>
</div>
```

### 5. Layout Structure

The patient interface uses a 3-panel layout (PRD Release 0.5+):

```html
<!-- templates/personal/dashboard.html -->
<div class="personal-dashboard">
  <!-- Left Panel: Health Records Repository -->
  <aside class="records-panel">
    {% include "personal/records.html" %}
  </aside>

  <!-- Center Panel: Chat Interface -->
  <main class="chat-panel">
    {% include "personal/chat.html" %}
  </main>

  <!-- Right Panel: Feed/Summary -->
  <aside class="feed-panel">
    {% include "personal/feed.html" %}
  </aside>
</div>
```

Use Tailwind CSS (already in the project) for styling to match the calm, clean aesthetic from the PRD.

---

## Implementation Phases

### Phase 1: Foundation (Release 0 - Alpha)
**Goal**: Basic chat interface with health record extraction

**Tasks**:
1. Create `sandwich/personal/` app
2. Add models: `PersonalHealthRecord`, `ChatMessage`
3. Create basic 3-panel dashboard template
4. Implement chat service with Claude API
5. Build HTMX chat interface
6. Add health records repository view
7. Create health summary generation

**Deliverables**:
- ✅ Chat with AI assistant
- ✅ Extract health data from text
- ✅ View all health records
- ✅ AI-generated health summary

### Phase 2: Document Upload (Release 0 cont.)
**Goal**: PDF document processing

**Tasks**:
1. Reuse existing document upload infrastructure
2. Create personal document extraction service
3. Add HTMX file upload component
4. Link extracted data to chat interface

**Deliverables**:
- ✅ Upload PDF documents
- ✅ Auto-extract health data from PDFs
- ✅ Link documents to health records

### Phase 3: Feed System (Release 0.5 - Beta)
**Goal**: Dynamic feed with summaries and engagement

**Tasks**:
1. Create `HealthSummary` model
2. Build feed card components
3. Implement SSE for real-time updates
4. Add source attribution links
5. Create inline suggestion system

**Deliverables**:
- ✅ Dynamic feed panel
- ✅ Summary cards with source links
- ✅ Real-time updates
- ✅ Inline action suggestions

### Phase 4: Notifications (Release 1.0)
**Goal**: Proactive notifications and record notes

**Tasks**:
1. Create notification system
2. Add notes to health records
3. Build notification panel UI
4. Implement notification triggers

**Deliverables**:
- ✅ Notification bell
- ✅ Smart health notifications
- ✅ Record notes functionality

### Phase 5: Advanced Features (Release 2.0)
**Goal**: Advanced chat actions and intelligence

**Tasks**:
1. Add in-chat action buttons
2. Implement image upload (OCR)
3. Build deduplication logic
4. Create contextual follow-ups
5. Enhance summaries with trends

**Deliverables**:
- ✅ Photo upload for prescriptions
- ✅ Duplicate detection
- ✅ Smart follow-up questions
- ✅ Contextual summaries

---

## Integration Points with Existing Code

### 1. Authentication & Permissions
- Use existing `User` model from `sandwich/users/`
- Create new permission groups for personal health access
- Reuse Guardian for object-level permissions

### 2. Background Tasks
- Use existing Procrastinate setup for:
  - Document processing
  - LLM API calls
  - Summary generation
- Create tasks in `sandwich/personal/tasks.py`

### 3. LLM Services
- Reuse `sandwich/core/services/ingest/` patterns
- Share Claude/Gemini client configuration
- Extend with personal health prompts

### 4. Document Storage
- Use existing S3/private storage setup
- Reuse `Document` model
- Add personal health document types

### 5. Real-time Updates
- Use existing SSE infrastructure (`django-eventstream`)
- Create personal health event channels
- Reuse patterns from provider interface

---

## Design System

### Colors & Themes
Follow the calm, minimal aesthetic from PRD:
- Soft color palettes (leverage DaisyUI themes)
- Generous whitespace
- Smooth animations
- Clear visual hierarchy

### Typography
- Use existing Tailwind typography plugin
- Clear heading levels
- Optimized readability

### Components
Reuse existing component patterns where possible:
- Modal system
- Form components (Crispy Forms + Tailwind)
- Icon system (Lucide icons)
- Card components

### Tone & Voice
Per PRD requirements:
- Conversational and friendly
- Empathetic and supportive
- Clear (no jargon)
- Empowering
- Calm (no anxiety-inducing language)

---

## Testing Strategy

### Unit Tests
- Test LLM extraction logic
- Test record deduplication
- Test summary generation
- Test chat message processing

### E2E Tests (Playwright)
- Test complete chat flow
- Test document upload flow
- Test feed updates
- Test search functionality

### LLM Tests (with VCR)
Reuse existing VCR pattern:
```bash
pytest --record-mode=all sandwich/personal/services/chat_test.py
```

---

## Security & Privacy

### Data Ownership
Per PRD: "The person owns their data"
- Patient has full control over their health records
- Can delete records at any time
- Can export all data
- Clear data retention policies

### Permissions
- Patients can only see their own records
- Providers can request access (future)
- Audit trail for all access

### HIPAA Compliance
- Build on existing HIPAA-compliant infrastructure
- Encrypted storage (S3, database)
- Audit logs (pghistory)
- Secure communication (HTTPS, CSP)

---

## Migration Path

### For Existing Provider Data
- Existing `Patient` records continue to work
- Providers can still manage patient data
- Personal health records are patient-entered, separate but linked

### For Existing Documents
- Documents already uploaded by providers remain
- Patients can view and add notes to existing documents
- New patient-uploaded documents are clearly attributed

---

## Next Steps

1. **Review this plan** with the team
2. **Create ticket breakdown** for Phase 1
3. **Set up development environment**
4. **Begin Phase 1 implementation**
5. **Iterate based on feedback**

---

## Questions to Resolve

1. **User Model**: Should patients have separate accounts from providers, or can one user be both?
2. **Data Separation**: Should patient-entered data be completely separate from provider-entered data, or merged?
3. **LLM Costs**: What's the budget for Claude API calls? Should we cache summaries aggressively?
4. **Mobile**: Is mobile responsiveness required for Phase 1?
5. **Offline**: Do we need offline support (PWA)?

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Owner**: Diane
