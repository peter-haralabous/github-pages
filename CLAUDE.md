# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Thrive Prototypes - Django + HTMX Architecture Documentation

## Overview

This is a **healthcare prototyping platform** built with Django and HTMX, featuring:
- **Patient portal** for managing health records and documents
- **Provider interface** for healthcare professionals to manage patients, encounters, and forms
- **AI-powered document processing** using LLMs (Claude, Gemini)
- **Real-time task processing** with Procrastinate (background job queue)
- **Multi-tenant organization support** with granular permissions
- **Server-sent events** for live UI updates

## Personal Health Connect (Patient-Facing Features)

This repository includes a **personal health record (PHR) system** that allows patients to:
- Chat with an AI assistant to add health information naturally
- Upload documents (PDFs, images) with automatic data extraction
- View all health records organized by category (medications, conditions, allergies, etc.)
- Receive AI-generated health summaries and insights
- See a dynamic feed of health updates with source attribution

**Key Documentation**:
- [Product Requirements Document (PRD)](./docs/personal-health-connect/PRD.md) - Complete product vision and features
- [Implementation Plan](./docs/personal-health-connect/IMPLEMENTATION_PLAN.md) - Django + HTMX rebuild strategy

**Implementation Status**: Planning phase - features are being rebuilt from a React prototype into Django + HTMX to match the existing tech stack.

**Core Principles** (from PRD):
1. **Primacy of the Individual** - The person is the center of design, not clinical workflows
2. **One Person, One Truth** - Single, unified health record for each individual
3. **The Person Owns Their Data** - Fundamental right to all personal data

## Application Structure

### Core Django Apps

The codebase is organized into main Django apps:

```
sandwich/
├── users/          # Authentication and user management
├── core/           # Shared models, services, utilities
├── patients/       # Patient-specific features and views (provider-facing)
├── providers/      # Provider/staff interface
└── personal/       # Personal health connect (patient-facing) - IN PLANNING
```

**Note**: The `personal/` app is in planning phase. See [Implementation Plan](./docs/personal-health-connect/IMPLEMENTATION_PLAN.md) for details.

### Key Directories

```
config/
├── settings/
│   ├── base.py     # Shared settings
│   ├── local.py    # Development settings
│   ├── production.py
│   └── test.py
├── urls.py         # Main URL router
└── wsgi.py / asgi.py

sandwich/
├── models/         # Django ORM models (core app)
├── service/        # Business logic layer
├── views/          # HTTP view handlers
├── middleware/     # HTTP middleware
├── templates/      # Jinja2 templates
├── static/         # CSS/JS assets (Webpack bundled)
├── fixtures/       # Test data
└── factories/      # Factory Boy model factories
```

## 1. Overall Application Architecture

### Architectural Layers

```
┌─────────────────────────────────────┐
│     Frontend (Templates + HTMX)     │  JavaScript + TailwindCSS
├─────────────────────────────────────┤
│        Django Views & Forms         │  Request handling, validation
├─────────────────────────────────────┤
│      Service Layer (Business)       │  Domain logic, permissions
├─────────────────────────────────────┤
│       Models & QuerySets            │  Data access layer
├─────────────────────────────────────┤
│    PostgreSQL + Pg Extensions       │  Full-text search, history tracking
└─────────────────────────────────────┘
        Background Tasks (Procrastinate)
```

### URL Routing Strategy

Routes are **namespace-based** for consistency and middleware targeting:

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),                    # namespace="admin"
    path("users/", include("sandwich.users.urls")),      # namespace="users"
    path("accounts/", include("allauth.urls")),          # NO namespace (allauth limitation)
    path("patients/", include("sandwich.patients.urls")), # namespace="patients"
    path("providers/", include("sandwich.providers.urls")), # namespace="providers"
    path("", include("sandwich.core.urls")),             # namespace="core"
]
```

### Authentication & Authorization

**Multi-layered authentication:**

1. **Authentication** (who are you?)
   - Django's `AbstractUser` extended with email-based login
   - AllAuth for social login (Google OAuth)
   - Session-based authentication

2. **Authorization** (what can you do?)
   - **Django Guardian**: Object-level permissions (per-resource)
   - **Role-based access**: Users assigned to Roles within Organizations
   - **Decorator-based view permission**: `@authorize_objects()` decorator validates access

**Permission Model:**
- Each `Organization` auto-creates 4 default roles: OWNER, ADMIN, STAFF, PATIENT
- Roles are Django `Group` objects with assigned permissions
- Permissions are both model-level and organization-scoped

```python
# sandwich/core/models/role.py
class Role(BaseModel):
    name = models.CharField(max_length=255)
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
```

### Request Flow Example

```
HTTP Request → Middleware Stack → View → Service Layer → Models → DB
     ↓
1. AuthenticationMiddleware: Attach user to request
2. ConsentMiddleware: Check if user consented to policies
3. PatientAccessMiddleware: Ensure patient user has a patient record
4. TimezoneMiddleware: Set timezone from cookie
     ↓
5. @authorize_objects() decorator: Validate permissions, inject objects
     ↓
6. View function: Process request, call services
     ↓
7. Service layer: Business logic (permissions, calculations, events)
     ↓
8. Models: Database access
```

---

## 2. Key Models & Relationships

### Core Data Model

**Key Entities:**

```
User (from Django auth)
  ├─ Many-to-One → Patient (patients the user owns)
  └─ Many-to-Many → Group (via Role)

Organization (multi-tenant container)
  ├─ Many-to-One ← Patient (belongs to one org)
  ├─ Many-to-One ← Form (templates scoped to org)
  ├─ Many-to-Many ← User (via Role/Group)
  └─ One-to-Many → Role (OWNER, ADMIN, STAFF, PATIENT)

Patient (healthcare subject)
  ├─ Many-to-One → User (owner)
  ├─ Many-to-One → Organization
  ├─ One-to-Many → Document
  ├─ One-to-Many → Encounter
  ├─ One-to-Many → Task
  ├─ One-to-Many → FormSubmission
  └─ Search Vector (full-text search)

Document (uploaded file)
  ├─ Many-to-One → Patient
  ├─ Many-to-One → HealthRecord
  └─ PrivateFileField (encrypted storage)

Encounter (clinical visit)
  ├─ Many-to-One → Patient
  ├─ Many-to-One → Organization
  ├─ One-to-Many → Task
  └─ Status: IN_PROGRESS, COMPLETED

Task (form to complete)
  ├─ Many-to-One → Encounter
  ├─ Many-to-One → Form (the template)
  ├─ One-to-Many → FormSubmission
  └─ Status: PENDING, COMPLETED

Form (SurveyJS template)
  ├─ Many-to-One → Organization
  ├─ JSON schema (SurveyJS format)
  └─ VersionMixin (history tracking via pghistory)

FormSubmission (user responses)
  ├─ Many-to-One → Task
  ├─ JSON data
  └─ Status: DRAFT, SUBMITTED
```

### Model Features

**Auditing & History:**
- Uses `pghistory` and `pgtrigger` for automatic audit trails
- `@pghistory.track()` decorator records all changes
- VersionMixin provides version access methods

```python
@pghistory.track()
class Form(VersionMixin, BaseModel):
    name = models.CharField(max_length=255)
    schema = models.JSONField(default=dict)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    
    def get_versions(self):
        """Get all historical versions"""
        return self.events.order_by("-pgh_id")
```

**Full-Text Search:**
- PostgreSQL `SearchVectorField` for Patient name search
- Triggered database updates via triggers
- Rank-based results

```python
class Patient(BaseModel):
    search_vector = SearchVectorField(null=True, blank=True)
    
    class PatientQuerySet(models.QuerySet):
        def search(self, query: str) -> Self:
            search_query = to_search_query(query)
            return self.filter(search_vector=search_query)\
                       .annotate(rank=SearchRank(F("search_vector"), search_query))\
                       .order_by("-rank")
```

---

## 3. HTMX Integration with Django

### HTMX Philosophy in This App

HTMX is used for **partial page updates** without full page reloads:
- **Search/filter**: Live table updates as user types
- **Modal dialogs**: Load forms dynamically
- **Progressive enhancement**: Forms work with standard POST, but enhanced with HTMX
- **Server-sent events**: Real-time status updates for background tasks

### Template Structure

**Base template includes HTMX configuration:**

```html
<!-- sandwich/templates/base.html -->
<meta name="htmx-config" content='{"inlineScriptNonce":"{{ request.csp_nonce }}"}' />
<body hx-ext="sse">
  <!-- HTMX SSE extension for server-sent events -->
  
  <script nonce="{{ request.csp_nonce }}">
    // Auto-attach CSRF token to HTMX requests
    document.body.addEventListener('htmx:configRequest', (event) => {
      const csrfToken = '{{ csrf_token }}';
      if (event.detail.method !== 'get') {
        event.detail.headers['X-CSRFToken'] = csrfToken;
      }
    });
  </script>
</body>
```

### HTMX Attribute Examples

**Real-time search with debouncing:**

```html
<!-- sandwich/templates/provider/patient_list.html -->
<form hx-get="{% url 'providers:patient_list' organization_id=organization.id %}"
      hx-target="#patient_table_container"
      hx-push-url="true"
      hx-trigger="keyup changed delay:300ms from:input[name='search'], 
                  change from:select[name='has_active_encounter'], 
                  filtersChanged from:body">
  <input name="search" type="text" placeholder="Search" />
  <select name="has_active_encounter">
    <option value="">All Patients</option>
    <option value="true">Active</option>
    <option value="false">Archived</option>
  </select>
</form>

<div id="patient_table_container">
  {% include "provider/partials/patient_list_table.html" %}
</div>
```

**Modal form submission:**

```html
<!-- sandwich/templates/provider/partials/patient_add_modal.html -->
<dialog id="patient-add-modal" class="modal">
  <div class="modal-box">
    <form method="post"
          hx-post="{% url 'providers:patient_add_modal' organization_id=organization.id %}"
          hx-target="#modal-container"
          hx-swap="innerHTML">
      {% csrf_token %}
      {% crispy form %}
    </form>
  </div>
</dialog>
```

**Server-sent events for real-time updates:**

```html
<!-- sandwich/templates/patient/chatty/app.html -->
<div hx-ext="sse"
     sse-connect="{% url 'patients:eventstream' patient_id=patient.id %}"
     sse-swap="ingest_progress:#ingest-progress-container">
  <div id="ingest-progress-container"></div>
</div>
```

### HTMX View Response Patterns

**Returning partial templates for HTMX requests:**

```python
from sandwich.core.util.http import AuthenticatedHttpRequest

def patient_list(request: AuthenticatedHttpRequest, organization_id: UUID):
    # Fetch and filter data
    patients = Patient.objects.filter(organization_id=organization_id)
    
    # Detect if HTMX request
    if request.headers.get("HX-Request") == "true":
        # Return only the table partial, not full page
        return render(request, "provider/partials/patient_list_table.html", {
            "patients": patients
        })
    
    # Standard request: return full page
    return render(request, "provider/patient_list.html", {
        "patients": patients
    })
```

**Context processor for HTMX detection:**

```python
# sandwich/core/context_processors.py
def htmx_context(request: HttpRequest):
    """Make HTMX headers available to templates."""
    return {
        "hx_request": request.headers.get("HX-Request") == "true",
    }
```

### Form Handling with Crispy Forms

Uses **crispy_tailwind** for form rendering:

```python
# sandwich/providers/views/patient.py
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit

class PatientEdit(forms.ModelForm[Patient]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("first_name", "last_name", css_class="flex gap-4"),
            "date_of_birth",
            "province",
            "phn",
            "email",
            Submit("submit", "Submit"),
        )
```

---

## 4. Background Task Processing with Procrastinate

### Architecture

**Procrastinate** is a Python task queue using PostgreSQL:
- No separate message broker (Redis not required)
- Atomic transactions with database
- Built-in job retries and monitoring
- JSON serialization

### Task Definition Pattern

**Custom decorator for pghistory context:**

```python
# sandwich/core/util/procrastinate.py
from procrastinate.contrib.django import app
import pghistory

def define_task(original_func=None, **kwargs):
    """Decorator that:
    1. Registers task with procrastinate
    2. Adds pghistory context for audit trails
    3. Manages database connections
    """
    
    def decorator(func):
        @functools.wraps(func)
        def new_func(context: JobContext, *job_args, **job_kwargs):
            close_old_connections()
            reset_queries()
            try:
                with pghistory.context(job=context.job.id, task_name=context.job.task_name):
                    return func(*job_args, **job_kwargs)
            finally:
                close_old_connections()
```

### Task Examples

**Document processing pipeline:**

```python
# sandwich/core/service/ingest_service.py
@define_task
def process_document_job(document_id: str):
    """Main job that spawns parallel extraction tasks"""
    extract_facts_from_document_job.defer(document_id=document_id)
    extract_records_from_document_job.defer(document_id=document_id)

@define_task
def extract_facts_from_document_job(document_id: str, llm_name: str = ModelName.CLAUDE_SONNET_4_5):
    """Extract structured facts using LLM"""
    document = Document.objects.get(id=document_id)
    llm_client = get_llm(ModelName(llm_name))
    
    # Send progress update via SSE
    send_ingest_progress(document.patient.id, text=f"Processing {document.original_filename}...")
    
    # Extract facts from PDF/text
    with document.file.open("rb") as f:
        content = f.read()
    
    if document.content_type == "application/pdf":
        triples = extract_facts_from_pdf(content, llm_client, patient=document.patient, document=document)
    else:
        triples = extract_facts_from_text(content, llm_client, patient=document.patient, document=document)

@define_task(lock="expire_invitations_lock")
def expire_old_invitations_job():
    """Periodic task with locking to prevent duplicate execution"""
    invitations = Invitation.objects.filter(
        created_at__lt=timezone.now() - timedelta(days=30),
        status=InvitationStatus.PENDING
    )
    invitations.delete()
```

### Task Auto-Discovery

```python
# sandwich/core/tasks.py
# Procrastinate auto-detects this file and imports all @task-decorated functions

import sandwich.core.service.ingest_service
import sandwich.core.service.invitation_service
```

### Real-time UI Updates via SSE

**Server sends progress updates:**

```python
def send_ingest_progress(patient_id: UUID, *, text: str, done=False):
    """Send Server-Sent Event to update UI"""
    from django_eventstream import send_event
    
    context = {"text": text, "done": done}
    content = loader.render_to_string("patient/partials/ingest_progress.html", context)
    # Sends event to client listening on "patient/{patient_id}" channel
    send_event(f"patient/{patient_id}", "ingest_progress", content, json_encode=False)
```

**Client receives updates:**

```html
<div hx-ext="sse"
     sse-connect="{% url 'patients:eventstream' patient_id=patient.id %}"
     sse-swap="ingest_progress:#ingest-progress-container">
  <div id="ingest-progress-container">
    Waiting for progress...
  </div>
</div>
```

---

## 5. Unique Architectural Patterns

### A. Permission Authorization Decorator

**Custom decorator for view-level permission checking:**

```python
# sandwich/core/service/permissions_service.py
@dataclass
class ObjPerm:
    model: type[BaseModel]
    pk_param: str           # URL parameter name
    perms: list[str]        # Required permissions
    object_name: str | None # Kwarg name (defaults to model name)

def authorize_objects(rules: list[ObjPerm]):
    """
    Extracts URL parameters, validates permissions, injects objects.
    
    Example usage:
    """
    def decorator(view_func):
        def view_wrapper(request, *args, **kwargs):
            # Extract IDs from URL
            objects = {}
            for rule in rules:
                pk = kwargs.pop(rule.pk_param)
                # Check permission and fetch
                obj = get_authorized_object_or_404(request.user, rule.perms, rule.model, id=pk)
                objects[rule.object_name or rule.model._meta.model_name] = obj
            return view_func(request, *args, **objects, **kwargs)
        return view_wrapper
    return decorator

# Usage:
@login_required
@authorize_objects([
    ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"]),
    ObjPerm(Organization, "organization_id", ["view_organization"])
])
def patient_edit(request, organization: Organization, patient: Patient):
    # organization and patient are already validated and authorized
    ...
```

### B. Middleware-Based Request Routing

**Consent middleware checks policy acceptance:**

```python
# sandwich/core/middleware/consent.py
class ConsentMiddleware:
    """Redirect to consent page if user hasn't accepted required policies"""
    
    exempt_namespaces = {"admin", "accounts", "static"}
    required_policies = {ConsentPolicy.THRIVE_PRIVACY_POLICY, ConsentPolicy.THRIVE_TERMS_OF_USE}
    
    def __call__(self, request):
        if self.should_process(request, match):
            if not _has_consented_to_policies(request.user, self.required_policies):
                return _handle_missing_consent(request)  # Redirect to consent page
        return self.get_response(request)
```

**Patient access middleware ensures patient record exists:**

```python
# sandwich/patients/middleware/patient_access.py
class PatientAccessMiddleware:
    """Ensure user has a patient record before accessing patient routes"""
    
    def __call__(self, request):
        if request.user.is_authenticated:
            match = cached_resolve(request)
            if match.namespace == "patients" and match.view_name not in self._allowed_routes:
                if not Patient.objects.filter(user=request.user).exists():
                    # Redirect to patient creation
                    return HttpResponseRedirect(reverse("patients:patient_onboarding_add"))
        return self.get_response(request)
```

### C. Service Layer Architecture

**Services encapsulate business logic, separate from views:**

```
views.py (HTTP handling) → service/ (business logic) → models.py (data)

Examples:
- sandwich/core/service/organization_service.py
- sandwich/core/service/patient_service.py
- sandwich/core/service/form_service.py
- sandwich/core/service/invitation_service.py
- sandwich/core/service/document_service.py
```

**Service example:**

```python
# sandwich/core/service/organization_service.py
def create_default_roles_and_perms(organization: Organization) -> None:
    """Called automatically when Organization is created"""
    for role_name, org_perms in DEFAULT_ORGANIZATION_ROLES.items():
        group = Group.objects.create(name=f"{role_name}_{organization.id}")
        role = Role.objects.create(organization=organization, name=role_name, group=group)
        for perm in org_perms:
            assign_perm(perm, group, organization)

def assign_organization_role(organization: Organization, role_name: str, user: User) -> None:
    """Assign user to role"""
    role = organization.get_role(role_name)
    user.groups.add(role.group)
```

### D. QuerySet Customization with Managers

**Custom managers for complex queries:**

```python
# sandwich/core/models/patient.py
class PatientQuerySet(models.QuerySet):
    def search(self, query: str) -> Self:
        """Full-text search on patient names"""
        search_query = to_search_query(query)
        return self.filter(search_vector=search_query)\
                   .annotate(rank=SearchRank(F("search_vector"), search_query))\
                   .order_by("-rank")

class PatientManager(models.Manager):
    def get_queryset(self):
        return PatientQuerySet(self.model, using=self._db)
    
    def create(self, **kwargs) -> "Patient":
        """Auto-assign permissions when patient created"""
        patient = super().create(**kwargs)
        if patient.organization and patient.user:
            assign_organization_role(patient.organization, RoleName.PATIENT, patient.user)
        assign_default_patient_permissions(patient)
        return patient
```

### E. Type Hints for HTTP Request

**Custom types for authenticated vs. unauthenticated requests:**

```python
# sandwich/core/util/http.py
class UserHttpRequest(WSGIRequest):
    """Use when @login_required is NOT applied"""
    user: User | AnonymousUser

class AuthenticatedHttpRequest(HttpRequest):
    """Use when @login_required IS applied (guarantees user is authenticated)"""
    user: User
```

**Usage:**

```python
@login_required
def my_view(request: AuthenticatedHttpRequest):
    # Type checker knows request.user is User, not User | AnonymousUser
    print(request.user.email)  # No type error
```

### F. List Preference Management

**User preferences for list views (filtering, sorting, column visibility):**

```
ListViewType (enum): "patient_list", "encounter_list", etc.
ListViewPreference:
  - scope: PERSONAL, ORGANIZATION
  - list_type: str
  - columns: JSONField (which columns to show)
  - sort_by: str
  - filters: JSONField (applied filters)
```

**Views auto-apply preferences:**

```python
def patient_list(request, organization_id):
    # Get user's saved preferences
    preferences = get_list_view_preference(request.user, "patient_list", organization_id)
    
    # Auto-apply sort, filters
    patients = Patient.objects.filter(organization_id=organization_id)
    patients = apply_sort_with_custom_attributes(patients, preferences.sort_by)
    patients = apply_filters_with_custom_attributes(patients, preferences.filters)
    
    return render(request, "...", {"patients": patients})
```

### G. Custom Attributes System

**Organizations can define custom fields for patients:**

```python
class CustomAttribute(BaseModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization)
    field_type: EnumField[CustomAttributeType]  # TEXT, DATE, SELECT, etc.
    enum_values: JSONField  # For SELECT type

class CustomAttributeValue(BaseModel):
    patient = models.ForeignKey(Patient)
    attribute = models.ForeignKey(CustomAttribute)
    value: JSONField
```

**Service automatically applies custom attributes to queries:**

```python
def annotate_custom_attributes(queryset, organization):
    """Add custom attribute values as annotations"""
    for attr in organization.customattribute_set.all():
        queryset = queryset.annotate(**{
            f"custom_{attr.id}": Subquery(...)
        })
    return queryset
```

### H. Version Control with pghistory

**Automatic audit trail for important models:**

```python
@pghistory.track()
class Form(VersionMixin, BaseModel):
    """All changes are automatically tracked"""
    name = models.CharField(max_length=255)
    schema = models.JSONField()

# Access versions:
form.get_versions()  # All versions
form.get_current_version()  # Latest
form.restore_to(version_id)  # Revert to old version
```

### I. Multi-Tenant Organization Scoping

**Every entity scoped to an organization:**

- Organization is the "boundary" for multi-tenancy
- Users belong to orgs via Role/Group
- Models enforce organization FK relationship
- Queries automatically filtered by org in views

```python
@authorize_objects([
    ObjPerm(Organization, "organization_id", ["view_organization"])
])
def organization_home(request, organization: Organization):
    # organization is validated; user has permission
    patients = Patient.objects.filter(organization=organization)
    return render(request, "...", {"patients": patients})
```

---

## 6. Technology Stack

### Backend
- **Framework**: Django 5.0+
- **Database**: PostgreSQL with extensions (pghistory, pgtrigger, pg_trgm)
- **ORM**: Django ORM + QuerySet customization
- **Auth**: Django AllAuth (email + Google OAuth)
- **Permissions**: django-guardian (object-level)
- **Background Jobs**: Procrastinate
- **API**: Django Ninja (async-ready)
- **Forms**: Django Forms + Crispy Forms + Tailwind theme
- **History Tracking**: django-pghistory + pgtrigger
- **Real-time Updates**: django-eventstream (SSE)

### Frontend
- **Templating**: Jinja2 templates
- **Interactivity**: HTMX (hypermedia exchanges)
- **Styling**: TailwindCSS
- **Icons**: Lucide icons (template tag integration)
- **Bundler**: Webpack (CSS/JS)

### Infrastructure
- **Container**: Docker
- **Task Queue**: Procrastinate (PostgreSQL-backed)
- **Redis**: Optional (for django-eventstream caching)
- **File Storage**: Private storage (encrypted) + S3 (production)
- **LLM Backends**: Claude (Bedrock), Gemini

---

## 7. Important Files Reference

### Configuration
- `config/settings/base.py` - Shared Django settings
- `config/urls.py` - Main URL configuration

### Apps
- `sandwich/users/` - User authentication
- `sandwich/core/` - Shared models, services, utilities
- `sandwich/patients/` - Patient portal
- `sandwich/providers/` - Provider interface

### Key Services
- `sandwich/core/service/organization_service.py` - Org & role management
- `sandwich/core/service/patient_service.py` - Patient operations
- `sandwich/core/service/permissions_service.py` - Permission checking
- `sandwich/core/service/ingest_service.py` - Document processing jobs
- `sandwich/core/service/form_service.py` - Form management
- `sandwich/core/service/list_preference_service.py` - List view preferences

### Models
- `sandwich/core/models/` - Core data model definitions
  - `patient.py` - Patient model
  - `organization.py` - Organization model
  - `form.py` - Form template model
  - `document.py` - Document/file model
  - `task.py` - Task model (form to complete)
  - `role.py` - Role/permission model

### Views
- `sandwich/providers/views/` - Provider-facing views
- `sandwich/patients/views/` - Patient-facing views
- `sandwich/core/views/` - Shared views

### Middleware
- `sandwich/core/middleware/` - Core middleware
- `sandwich/patients/middleware/` - Patient-specific middleware

---

## 8. Common Development Patterns

### Creating a New View with Permissions

```python
from sandwich.core.service.permissions_service import authorize_objects, ObjPerm
from sandwich.core.util.http import AuthenticatedHttpRequest

@login_required
@authorize_objects([
    ObjPerm(Organization, "organization_id", ["view_organization", "create_patient"]),
])
def create_patient(request: AuthenticatedHttpRequest, organization: Organization):
    if request.method == "POST":
        form = PatientCreateForm(request.POST)
        if form.is_valid():
            patient = form.save(organization=organization)
            return redirect("providers:patient_details", patient_id=patient.id)
    else:
        form = PatientCreateForm()
    return render(request, "providers/patient_form.html", {"form": form})
```

### Creating a Task

```python
from sandwich.core.util.procrastinate import define_task

@define_task
def process_pdf_document(document_id: str):
    """Background job to process uploaded PDF"""
    document = Document.objects.get(id=document_id)
    # Do work...

# Trigger job:
process_pdf_document.defer(document_id=str(doc.id))
```

### Custom QuerySet/Manager

```python
from django.db import models

class MyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def for_user(self, user):
        return self.filter(user=user)

class MyManager(models.Manager):
    def get_queryset(self):
        return MyQuerySet(self.model)
    
    def active(self):
        return self.get_queryset().active()

class MyModel(BaseModel):
    objects = MyManager()
```

---

## 9. Testing Patterns

- **Test files**: Suffix with `_test.py`
- **Test runner**: pytest with Django plugin
- **Factories**: Factory Boy for model creation
- **Fixtures**: JSON fixtures in `sandwich/fixtures/`

```python
# pytest configuration in pyproject.toml
[tool.pytest.ini_options]
addopts = "--ds=config.settings.test --reuse-db"
python_files = ["*_test.py"]
markers = ["e2e: end-to-end tests"]
```

---

## 10. Security Features

- **CSRF Protection**: HTMX auto-attaches CSRF token
- **CSP (Content Security Policy)**: django-csp
- **HTTPS**: Enforced in production
- **SQL Injection**: Django ORM parameterization
- **XSS**: Template auto-escaping
- **Object-level Permissions**: Guardian + custom decorator
- **Audit Trail**: pghistory tracks all changes
- **Private Files**: Encrypted storage with permission checks
