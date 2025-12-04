# Personal Health Connect: Releases 0 to 2.0 Implementation Roadmap

**Date**: November 2025
**Status**: Planning
**Goal**: Implement ALL features from PRD Releases 0, 0.5, 1.0, and 2.0 in Django + HTMX

---

## Overview

This roadmap covers the complete implementation of the Personal Health Connect patient-facing features as defined in the PRD, building on top of the existing Django chatty app infrastructure.

**Total Estimated Time**: 8-10 weeks
**Approach**: Incremental releases with user testing between each phase

---

## Existing Django Infrastructure ✅

**Good News**: We already have most of the foundation!

### Models
- ✅ `HealthRecord` base class with pghistory versioning
- ✅ `Condition` model (FHIR-compliant)
- ✅ `Immunization` model (FHIR-compliant)
- ✅ `Document` model
- ✅ `Patient` model
- ✅ `Encounter` model
- ✅ `Task` model
- ✅ `Provenance` tracking
- ✅ `Fact` knowledge graph model

### Services
- ✅ LLM integration (`sandwich/core/services/ingest/`)
- ✅ Document text extraction
- ✅ Background tasks (Procrastinate)
- ✅ Server-Sent Events (django-eventstream)
- ✅ Permissions (Guardian)

### Frontend
- ✅ HTMX integration
- ✅ Tailwind CSS + DaisyUI
- ✅ Webpack build system
- ✅ SurveyJS installed (for forms)

---

## Release 0 (Alpha) - Health Summary Foundation

**Duration**: 2-3 weeks
**Theme**: Establish the foundational data structure and introduce intelligent summarization

### Features to Build

#### 1. Core Health Record Types ✅ / 🔨

**What Exists**:
- ✅ Condition
- ✅ Immunization
- ✅ Document

**What to Add**:
- 🔨 Medication model
- 🔨 Allergy model
- 🔨 Procedure model
- 🔨 LabResult model
- 🔨 VitalSign model
- 🔨 HospitalVisit model

**Tasks**:
1. Create migration for new models extending `HealthRecord`
2. Add FHIR-compliant fields where applicable
3. Add pghistory tracking decorators
4. Create admin interfaces for each model
5. Update health records service to include new types

**Files to Create/Modify**:
```
sandwich/core/models/medication.py          [NEW]
sandwich/core/models/allergy.py             [NEW]
sandwich/core/models/procedure.py           [NEW]
sandwich/core/models/lab_result.py          [NEW]
sandwich/core/models/vital_sign.py          [NEW]
sandwich/core/models/hospital_visit.py      [NEW]
sandwich/core/models/__init__.py            [MODIFY - add exports]
```

#### 2. Health Records Repository (Left Panel) 🔨

**Current State**: Basic records list
**Target State**: Categorized, searchable repository

**Tasks**:
1. Create categorized view with sections for each record type
2. Add count badges for each category
3. Implement expand/collapse functionality
4. Add search across all records
5. Add filters (date range, source, status)
6. Show record source and entry method
7. Add "Add Record" buttons for each type

**Files to Create/Modify**:
```
sandwich/patients/templates/patient/chatty/partials/left_panel_records.html    [MODIFY]
sandwich/patients/views/patient/health_records.py                              [MODIFY]
sandwich/patients/urls.py                                                       [MODIFY - add routes]
```

**HTMX Patterns**:
```html
<!-- Expandable categories -->
<div hx-get="/patients/{{ patient.id }}/records/medications"
     hx-trigger="click"
     hx-target="#medications-list"
     hx-swap="innerHTML">
  <span>Medications (5)</span>
</div>

<!-- Search -->
<input type="search"
       hx-get="/patients/{{ patient.id }}/records/search"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#records-list">
```

#### 3. Health Summary Panel (Right Panel) 🔨

**Tasks**:
1. Create `HealthSummary` model
2. Build summary generation service using LLM
3. Create summary panel template
4. Add auto-refresh on data changes
5. Show loading states during generation
6. Cache summaries to avoid redundant LLM calls

**Files to Create/Modify**:
```
sandwich/core/models/health_summary.py                          [NEW]
sandwich/core/services/summarization.py                         [NEW]
sandwich/patients/templates/patient/chatty/partials/right_panel_summary.html  [NEW]
sandwich/patients/views/patient/summary.py                      [NEW]
```

**Model Structure**:
```python
class HealthSummary(BaseModel):
    patient = ForeignKey(Patient, on_delete=CASCADE)
    summary_type = CharField(choices=['basic', 'comprehensive', 'focused'])
    content = TextField()  # Markdown or HTML
    generated_at = DateTimeField(auto_now_add=True)
    data_hash = CharField()  # Hash of patient data to detect changes

    class Meta:
        ordering = ['-generated_at']
```

**Service**:
```python
async def generate_health_summary(patient: Patient) -> HealthSummary:
    # Gather all health records
    conditions = patient.condition_set.all()
    medications = patient.medication_set.all()
    # ... other records

    # Call Claude API
    prompt = f"Generate a health summary for {patient.name}..."
    summary_text = await call_claude(prompt)

    # Save to database
    return HealthSummary.objects.create(
        patient=patient,
        content=summary_text,
        data_hash=compute_hash(patient)
    )
```

#### 4. Basic Chat Interface ✅ / 🔨

**Current State**: Chat UI exists
**Target State**: AI assistant with data extraction

**Tasks**:
1. ✅ Chat message display (already exists)
2. 🔨 Persist chat messages to database
3. 🔨 Extract structured health data from user messages
4. 🔨 Show extracted records in chat response
5. 🔨 Add "What was extracted?" expandable section
6. 🔨 Link chat messages to created records

**Files to Create/Modify**:
```
sandwich/core/models/chat_message.py                [NEW]
sandwich/core/services/chat_extraction.py           [NEW]
sandwich/patients/views/chat.py                     [MODIFY]
```

**Chat Extraction Flow**:
```
User message → LLM analysis → Structured data → Save to DB → Show in chat
```

#### 5. Document Upload (PDF) ✅ / 🔨

**Current State**: Upload works via drag-and-drop
**Target State**: Upload + extraction + linking

**Tasks**:
1. ✅ File upload UI (already exists)
2. ✅ PDF text extraction (already exists)
3. 🔨 Extract health records from PDF using LLM
4. 🔨 Link extracted records back to document
5. 🔨 Show extraction progress via SSE
6. 🔨 Display extraction results in chat

**Files to Modify**:
```
sandwich/patients/views/document.py                 [MODIFY]
sandwich/core/services/ingest/extract_health_data.py    [NEW]
```

**Extraction Service**:
```python
async def extract_health_records_from_document(document: Document) -> ParsedHealthData:
    text = extract_text_from_pdf(document.file)

    # Call LLM with structured extraction prompt
    prompt = """
    Extract health records from this document:
    {text}

    Return JSON with:
    - medications: [...]
    - conditions: [...]
    - allergies: [...]
    etc.
    """

    result = await call_claude(prompt)
    return parse_health_data(result, document_id=document.id)
```

---

## Release 0.5 (Beta) - Feed & Engagement Loop

**Duration**: 2 weeks
**Theme**: Introduce the dynamic feed and feedback loop to create engagement

### Features to Build

#### 1. Dynamic Feed Panel (Right Panel) 🔨

**Tasks**:
1. Create `FeedItem` model
2. Build feed generation on data updates
3. Create feed card components
4. Implement chronological feed display
5. Add real-time updates via SSE
6. Show "New Update" badges

**Files to Create/Modify**:
```
sandwich/core/models/feed_item.py                           [NEW]
sandwich/patients/templates/patient/chatty/partials/right_panel_feed.html  [NEW]
sandwich/patients/views/patient/feed.py                     [NEW]
```

**Model Structure**:
```python
class FeedItem(BaseModel):
    patient = ForeignKey(Patient, on_delete=CASCADE)
    item_type = CharField(choices=['update', 'insight', 'suggestion'])
    title = CharField(max_length=255)
    content = TextField()
    created_at = DateTimeField(auto_now_add=True)

    # Links to related records
    related_records = JSONField(default=list)  # List of {type, id} dicts

    viewed = BooleanField(default=False)
```

#### 2. Summary Cards with Source Attribution 🔨

**Tasks**:
1. Add source links to feed cards
2. Implement click-to-highlight in records panel
3. Show record type icons and colors
4. Add "View Source" buttons
5. Implement HTMX swap-oob for highlighting

**HTMX Pattern**:
```html
<!-- Feed card with source links -->
<div class="feed-card">
  <p>Added 3 new medications</p>
  <ul>
    <li>
      <a hx-get="/patients/{{ patient.id }}/records/medications/123/highlight"
         hx-target="#left-panel"
         hx-swap="outerHTML">
        Lisinopril 10mg
      </a>
    </li>
  </ul>
</div>
```

#### 3. Inline Suggestions 🔨

**Tasks**:
1. Generate contextual suggestions based on recent activity
2. Display suggestion chips in chat
3. Make suggestions clickable to pre-fill input
4. Track suggestion acceptance for ML improvement

**Files to Create/Modify**:
```
sandwich/core/services/suggestion_service.py        [NEW]
sandwich/patients/templates/patient/chatty/partials/suggestions.html  [NEW]
```

**Suggestion Logic**:
```python
def generate_suggestions(patient: Patient, recent_activity: str) -> list[str]:
    # Examples:
    # - Recent activity: Added medication
    # - Suggest: "Add your next appointment", "Upload prescription image"

    # Use simple rules or LLM-based suggestions
    suggestions = []

    if patient.medication_set.exists() and not patient.immunization_set.exists():
        suggestions.append("Add your vaccination history")

    if patient.document_set.filter(created_at__gte=now() - timedelta(days=7)).exists():
        suggestions.append("Review recently uploaded documents")

    return suggestions[:3]  # Max 3 suggestions
```

#### 4. Streamlined Assistant Responses 🔨

**Tasks**:
1. Reduce verbosity in AI responses
2. Show only essential information
3. Use natural language patterns
4. Add visual hierarchy (summaries vs details)

**Response Format**:
```
✅ I found 2 medications in your message:
• Lisinopril 10mg daily
• Metformin 500mg twice daily

What else can you add?
[Upload Lab Results] [Add Appointment] [Tell me about symptoms]
```

---

## Release 1.0 - Notifications & Record Context

**Duration**: 2 weeks
**Theme**: Add proactive intelligence and deeper record context

### Features to Build

#### 1. Notifications System 🔨

**Tasks**:
1. Create `Notification` model
2. Build notification generation service
3. Create notifications modal/panel
4. Add notification bell icon with badge
5. Implement notification types (medication reminder, appointment, missing info)
6. Add notification preferences

**Files to Create/Modify**:
```
sandwich/core/models/notification.py                        [NEW]
sandwich/core/services/notification_service.py              [NEW]
sandwich/patients/templates/patient/chatty/partials/notifications_modal.html  [NEW]
sandwich/patients/views/patient/notifications.py            [NEW]
```

**Model Structure**:
```python
class Notification(BaseModel):
    patient = ForeignKey(Patient, on_delete=CASCADE)
    notification_type = CharField(choices=[
        'medication_reminder',
        'appointment_upcoming',
        'missing_information',
        'test_result_followup',
        'general'
    ])
    title = CharField(max_length=255)
    message = TextField()
    action_url = CharField(max_length=255, blank=True)
    action_text = CharField(max_length=100, blank=True)

    read = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

**Notification Generation**:
```python
# Background task runs daily
@define_task(queue='notifications')
def generate_daily_notifications(patient_id: int):
    patient = Patient.objects.get(id=patient_id)

    # Check for upcoming appointments
    upcoming = patient.appointment_set.filter(
        date__gte=now().date(),
        date__lte=now().date() + timedelta(days=3)
    )
    for appt in upcoming:
        Notification.objects.create(
            patient=patient,
            notification_type='appointment_upcoming',
            title='Upcoming Appointment',
            message=f'You have an appointment on {appt.date}',
            action_url=f'/appointments/{appt.id}',
            action_text='View Details'
        )
```

#### 2. Record Notes & Context 🔨

**Tasks**:
1. Add `notes` field to all HealthRecord models
2. Create note add/edit UI
3. Show notes in record detail view
4. Add notes to feed when updated
5. Allow rich text formatting (markdown)

**Files to Modify**:
```
sandwich/core/models/health_record.py                       [MODIFY - add notes field]
sandwich/patients/templates/patient/chatty/partials/record_detail.html  [NEW]
sandwich/patients/views/patient/health_records.py           [MODIFY]
```

**Model Update**:
```python
class HealthRecord(VersionMixin, BaseModel):
    # ... existing fields

    notes = TextField(
        blank=True,
        help_text="Personal notes about this record"
    )
    notes_updated_at = DateTimeField(null=True, blank=True)
```

**HTMX Note Editor**:
```html
<div id="record-notes-{{ record.id }}">
  <p>{{ record.notes|markdown }}</p>
  <button hx-get="/records/{{ record.id }}/notes/edit"
          hx-target="#record-notes-{{ record.id }}"
          hx-swap="outerHTML">
    Edit Notes
  </button>
</div>
```

#### 3. Improved Formatting 🔨

**Tasks**:
1. Add proper line breaks in assistant responses
2. Use visual hierarchy (headings, lists, spacing)
3. Add icons to suggestions
4. Improve mobile layout

**CSS Updates**:
```css
.assistant-message {
  line-height: 1.6;
}

.assistant-message h4 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.assistant-message ul {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}

.suggestion-chips {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}
```

---

## Release 2.0 - Advanced Chat Actions & Intelligence

**Duration**: 2-3 weeks
**Theme**: Move advanced functionality into the chat interface for seamless interaction

### Features to Build

#### 1. In-Chat Action Buttons 🔨

**Tasks**:
1. Add action buttons to chat footer
2. Implement modal/slideout workflows for each action
3. Add icons using Lucide
4. Make actions contextual based on conversation

**Files to Create/Modify**:
```
sandwich/patients/templates/patient/chatty/partials/chat_actions.html  [NEW]
sandwich/patients/views/patient/actions.py                             [NEW]
```

**Action Buttons**:
- 📄 Upload Document
- 📷 Take Photo
- 📊 View Insights
- 📅 Add Appointment
- 💊 Add Medication

**HTMX Implementation**:
```html
<div class="chat-actions">
  <button hx-get="/patients/{{ patient.id }}/actions/upload"
          hx-target="#action-modal"
          hx-swap="innerHTML"
          class="btn btn-ghost btn-sm">
    {% lucide "paperclip" class="size-5" %}
  </button>

  <button hx-get="/patients/{{ patient.id }}/actions/photo"
          hx-target="#action-modal"
          hx-swap="innerHTML"
          class="btn btn-ghost btn-sm">
    {% lucide "camera" class="size-5" %}
  </button>
</div>
```

#### 2. Enhanced Document Processing 🔨

**Tasks**:
1. Add image upload support (JPG, PNG)
2. Implement OCR for images
3. Support multi-page documents
4. Add document preview before processing
5. Improve extraction accuracy with better prompts

**Files to Create/Modify**:
```
sandwich/core/services/ingest/ocr_service.py                [NEW]
sandwich/core/services/ingest/image_processing.py           [NEW]
```

**OCR Integration**:
```python
from PIL import Image
import pytesseract

def extract_text_from_image(image_file) -> str:
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text
```

#### 3. Intelligent Record Deduplication 🔨

**Tasks**:
1. Build duplicate detection algorithm
2. Show "Possible duplicate" warnings
3. Allow user to confirm merge or keep separate
4. Update existing record instead of creating duplicate
5. Track merge history in audit trail

**Files to Create/Modify**:
```
sandwich/core/services/deduplication_service.py             [NEW]
sandwich/patients/templates/patient/chatty/partials/duplicate_warning.html  [NEW]
```

**Deduplication Logic**:
```python
def find_duplicates(new_record: Medication, patient: Patient) -> QuerySet[Medication]:
    # Fuzzy match on name + date
    existing = patient.medication_set.filter(
        name__icontains=new_record.name[:10],  # First 10 chars
        start_date=new_record.start_date
    )
    return existing

def handle_potential_duplicate(new_record, existing_record):
    # Show modal asking user:
    # "We found a similar medication (Lisinopril 10mg started 2023-01-15).
    #  Is this the same medication?"
    # [Yes, Update It] [No, Keep Both]
    pass
```

#### 4. Contextual Follow-Up Questions 🔨

**Tasks**:
1. Detect missing fields in extracted records
2. Generate natural follow-up questions
3. Show follow-up as chat message
4. Allow "I don't know" / "Skip" options
5. Pre-fill with user's response

**Files to Create/Modify**:
```
sandwich/core/services/followup_service.py                  [NEW]
```

**Follow-Up Logic**:
```python
def generate_followups(record: Medication) -> list[str]:
    questions = []

    if not record.dosage:
        questions.append("What dosage is your {record.name}?")

    if not record.start_date:
        questions.append("When did you start taking {record.name}?")

    if not record.prescriber:
        questions.append("Who prescribed {record.name}?")

    return questions

# In chat view:
if followups := generate_followups(new_medication):
    return ChatMessage(
        role='assistant',
        content=f"✅ Added {new_medication.name}. {followups[0]}"
    )
```

#### 5. Smart Summaries with Context 🔨

**Tasks**:
1. Enhance summaries to show connections
2. Highlight trends ("Your BP has improved")
3. Surface relevant context ("3rd visit for chest pain")
4. Link to related records
5. Personalize language and tone

**Enhanced Summary Prompts**:
```python
def generate_contextual_summary(patient: Patient, new_records: list) -> str:
    prompt = f"""
    Patient just added these records:
    {format_records(new_records)}

    Their existing health data includes:
    {format_patient_summary(patient)}

    Generate a brief summary that:
    1. Confirms what was added
    2. Highlights any connections to existing data
    3. Notes any trends or patterns
    4. Uses warm, personal language

    Example: "I've added your lab results from June 2024. I notice your
    hemoglobin A1C has improved from 7.2% to 6.5% since your last test
    in March—great progress on your diabetes management!"
    """

    return call_claude(prompt)
```

---

## Implementation Sequence

### Week 1-2: Release 0 Foundation
- [ ] Create missing HealthRecord models (Medication, Allergy, Procedure, etc.)
- [ ] Enhance left panel with categorized records view
- [ ] Build HealthSummary model and generation service
- [ ] Implement right panel health summary display
- [ ] Persist chat messages to database
- [ ] Build chat extraction service for structured data

### Week 3-4: Release 0 Completion
- [ ] Enhance document upload with health record extraction
- [ ] Link extracted records to source documents
- [ ] Add search functionality to records panel
- [ ] Implement real-time summary updates
- [ ] Add loading states and animations
- [ ] User testing and bug fixes

### Week 5-6: Release 0.5
- [ ] Create FeedItem model
- [ ] Build dynamic feed panel
- [ ] Implement source attribution in feed cards
- [ ] Add inline suggestions to chat
- [ ] Streamline assistant response formatting
- [ ] Add SSE for real-time feed updates
- [ ] User testing

### Week 7: Release 1.0
- [ ] Create Notification model and service
- [ ] Build notifications modal/panel
- [ ] Add notification bell with badge
- [ ] Implement notification generation (daily job)
- [ ] Add notes field to HealthRecord models
- [ ] Build note editor UI
- [ ] Improve formatting and visual hierarchy
- [ ] User testing

### Week 8-10: Release 2.0
- [ ] Add in-chat action buttons
- [ ] Implement image upload + OCR
- [ ] Build deduplication detection
- [ ] Create duplicate warning/merge UI
- [ ] Generate contextual follow-up questions
- [ ] Enhance summaries with trends and connections
- [ ] Multi-page document support
- [ ] Final polish and user testing

---

## Testing Strategy

### Unit Tests
- Test all model creation and validation
- Test LLM extraction with VCR cassettes
- Test deduplication logic
- Test notification generation

### Integration Tests
- Test complete chat → extraction → save flow
- Test document upload → extraction → linking
- Test feed generation on record updates
- Test SSE real-time updates

### E2E Tests (Playwright)
- Test user adds medication via chat
- Test user uploads PDF and sees extraction
- Test user receives notification
- Test user adds notes to record
- Test user resolves duplicate warning

### Load Tests
- Test with 100+ records per patient
- Test concurrent LLM calls
- Test SSE with multiple clients

---

## Success Metrics

### Engagement
- Number of records added per user
- Chat message frequency
- Document upload rate
- Time spent in app

### Comprehension
- User clicks on source links
- Time to find specific record
- Summary refresh rate

### Completion
- Records with complete fields
- Follow-up question response rate
- Duplicate resolution rate

---

## Risk Mitigation

### LLM Costs
- **Risk**: High API costs with many users
- **Mitigation**: Cache summaries aggressively, batch requests, use smaller models for simple tasks

### Extraction Accuracy
- **Risk**: LLM makes errors in health data extraction
- **Mitigation**: Show confidence scores, require user confirmation for critical data, allow easy editing

### Performance
- **Risk**: Slow page loads with many records
- **Mitigation**: Pagination, lazy loading, database indexing, caching

### Data Privacy
- **Risk**: Sensitive health data exposure
- **Mitigation**: Encryption at rest, HTTPS, audit logs, HIPAA compliance review

---

## Dependencies

### External Services
- Anthropic Claude API (or Google Gemini)
- OCR service (Tesseract or cloud service)
- PDF parsing library

### Python Packages
- ✅ django (5.2+)
- ✅ htmx
- ✅ django-eventstream (SSE)
- ✅ procrastinate (background tasks)
- ✅ pghistory (versioning)
- 🔨 pytesseract (OCR)
- 🔨 Pillow (image processing)

### JavaScript Packages
- ✅ htmx.org
- ✅ SurveyJS (forms)
- ✅ Lucide (icons)
- ✅ Tailwind + DaisyUI

---

## Next Steps

1. **Review this roadmap** with the team
2. **Prioritize features** if timeline needs adjustment
3. **Set up development environment** for contributors
4. **Create GitHub project board** with all tasks
5. **Begin Week 1 implementation** starting with models

---

## Questions & Decisions Needed

1. **LLM Provider**: Stick with Claude or add Gemini support?
2. **OCR**: Use Tesseract (free, local) or cloud service (paid, better accuracy)?
3. **Mobile**: Build native mobile apps or stick with responsive web?
4. **FHIR**: How strictly should we follow FHIR spec?
5. **Multi-language**: Support languages other than English?

---

**Status**: Ready to begin implementation
**Owner**: Diane + Development Team
**Last Updated**: November 2025
