# PRD: Personal Health Record (PHR) - Release 1

**JIRA**: [HC-225](https://new-hippo.atlassian.net/browse/HC-225) &nbsp;|&nbsp; **Author**: [Peter Haralabous](https://home.atlassian.com/o/787759e2-0bbc-494d-b27d-26930e7600ab/people/618e9ea320c676007090a9c0?cloudId=c7306235-0180-4269-ae60-6513d0ef7dd6) &nbsp;|&nbsp; **Date**: December 1, 2025

---

## Problem statement

### The core challenge

Healthcare information is profoundly fragmented. Providers navigate multiple disconnected systems, patients manually transport their medical histories, and critical information gets lost or duplicated in the process. This fragmentation creates three interrelated problems:

**1. Information scattering and "chart archaeology"**
- Providers spend 10-30 minutes per complex case gathering information across multiple systems
- Patient information exists in silos: primary care records, specialist notes, hospital systems, patient's own documents
- Repeated data entry as patients move between providers
- Critical information gaps leading to safety risks

**2. Context loss during navigation**
- Viewing encounter details separate from patient context
- Confusion about "where you are" in the application
- Mental overhead switching between patient overview and specific encounters/documents
- Risk of reviewing wrong patient's information

**3. Hidden labor of care coordination**
- Patients spending hours aggregating records for new providers
- Repeated intake forms asking identical questions
- Families managing binders of printed records
- Caregivers becoming "health information project managers"

### Impact

**Who**:
- **Physicians**: Primary care and specialist doctors
- **Nurses**: Emergency department and other nursing roles
- **Administrative Staff**: MOAs, clerks, and office coordinators

**Frequency**:
- Multiple times per patient encounter (high-frequency workflow)
- Every new provider relationship (patient burden)
- Every care transition or referral (coordination overhead)

**Current Workarounds**:
- Manual navigation between systems and pages
- Patients bringing binders of printed records to appointments
- Verbal history-taking consuming appointment time
- Providers using consumer AI tools (ChatGPT) for clinical notes due to gap in healthcare tools

### Research evidence

From provider interviews (n=22):
> "I feel like the optimal area to start with is just like helping people get it all in one place. That's it. Like because we don't do it well now." (JB, Exercise Physiologist)

> "Pre-prescribed, I probably spent sometimes 10 to 15 minutes for a complex case. If it's here in the hospital, it can be as long as half an hour sometimes—clicking on Cerner and clicking on Care Connect, opening, closing, opening, closing." (P4, Internal Medicine)

> "this is one of the biggest bug bears in medicine is um uh access to information, efficient use of medical information, communicating uh it's where a lot of mistakes happen." (MB, Family Physician)

From patient interviews (n=14):
> "I had to line up. Line up and wait and hopefully get the paper ready... and sometimes it's not timely either." (P04-JC)

> "Like every time I went to go see a new professional, whether it was an acupuncturist or a massage therapy person, you had to spend 15 minutes actually telling your story." (P13-MM)

---

## How might we...

We're solving two distinct but related problems for different clinical workflows:

### HMW 1: Enable specialists and physicians to focus on clinical decision-making while having quick, contextual access to patient health information?

Specialists and physicians spend excessive time on "chart archaeology"—navigating fragmented systems and manually gathering patient information. They need consolidated health information immediately accessible within their clinical workflows, while maintaining the patient context necessary for safe, efficient care.

### HMW 2: Enable administrative staff to efficiently prepare complete patient contexts before clinical encounters?

Medical office assistants and clerks are responsible for ensuring patient information is complete, organized, and ready for provider review. They manage pre-visit preparation, document coordination, encounter setup, and patient communication about documentation needs—all while juggling multiple patients and time-sensitive workflows.

**Key design principles:**
- **Consolidation over proliferation** - Reduce places to look, don't add another system
- **Context preservation** - Never separate encounters from patient identity
- **Workflow integration** - Meet users where they are, don't force new patterns
- **Role-appropriate access** - Same underlying data, interfaces optimized for each workflow
- **Progressive disclosure** - Essential information first, details on demand

---

## Executive summary

This PRD defines Release 1 of our Personal Health Record (PHR) system, which will be accessible from both patient-facing and clinical-facing applications. The release focuses on three core capabilities that address critical workflow inefficiencies identified through user research:

1. **Encounter management** - Streamlined patient encounter workflows within the PHR
2. **Document viewing** - Contextual access to encounter-related resources and documents
3. **Summary generation** - AI-powered health summaries from structured and unstructured data

The system serves multiple clinical user types with distinct needs: specialists requiring deep domain-specific information, clerks/MOAs managing administrative workflows, and nurses coordinating care. Release 1 prioritizes workflow validation over interface polish, focusing on core functionality that demonstrates measurable time savings and improved information access.

---

## User personas and needs

### Clinical users

**Specialists (Domain Experts)**
- **Profile**: Deep expertise in specific medical domains; focused information needs
- **Key Needs**:
  - Domain-specific summaries (e.g., orthopedic surgeon needs bleeding/clotting risk, not psychiatric history)
  - Quick access to specialty-relevant documents (imaging reports, lab results specific to their domain)
  - Ability to ingest and annotate specialist reports
- **Pain Points**: Generic summaries waste time; need configurable information depth
- **Success Metric**: Time from patient chart open to finding relevant specialist information

**Clerks / Medical office assistants (MOAs)**
- **Profile**: Administrative staff responsible for patient flow, pre-visit preparation, and ensuring clinical context is ready
- **Key needs**:
  - Quick patient verification and demographics access
  - Document upload and pre-visit form facilitation
  - Encounter management - creating encounters, adding relevant information, ensuring context is prepared for provider review
  - Patient communication tools for documentation needs and follow-ups
  - Referral management and triage capabilities
- **Pain points**: Repeated data entry; unclear which documents are already on file; time-sensitive pre-visit preparation; phone tag with patients about missing information; difficulty tracking what's ready for provider review
- **Success metric**: Time to prepare complete patient chart for appointment; reduction in day-of appointment delays due to missing information

**Nurses (Care Coordinators)**
- **Profile**: Coordinate care across providers; medication management; patient education
- **Key Needs**:
  - Comprehensive medication lists with reconciliation
  - Care plan visibility and coordination
  - Quick vital signs and assessment history
  - Document access for patient education
- **Pain Points**: Information scattered across systems; difficulty tracking patient progress; medication discrepancies between sources
- **Success Metric**: Time to complete medication reconciliation; care coordination efficiency

---

## Competitive analysis

### How do other healthcare systems solve information access and context problems?

&nbsp;

### Epic EMR: Tabs within patient chart

**Pattern**: All encounter information lives as tabs within the patient chart

**Key Features**:
- Patient context (demographics, allergies, key alerts) always visible in left sidebar
- Top-level tabs: Summary, Chart Review, Work List, MAR, Flowsheets, Notes, etc.
- Encounters filtered/sorted within patient chart, never separated from patient context
- Tabs within encounters: SnapShot, Chart Review, Immunizations, MAR, Communications

**Key Insight**: Never separate encounters from patient context

**Relevance to Our Design**: This pattern validates maintaining patient context while viewing encounter details. We should explore tab-based navigation within our PHR where appropriate.

**Visual Examples**: See Figures 1-2 in [Appendix](#visual-examples) for Epic EMR screenshots.

&nbsp;

### Master-detail pattern (industry standard)

**Pattern**: Parent view (master) maintains connection to child view (detail)

**Implementation Options**:
- **Split View**: Side-by-side panels (common on desktop)
- **Drill-down**: New page but with clear breadcrumb back (mobile-friendly)
- **Tabs**: Details embedded as tabs within parent
- **Slide-out**: Overlay panel maintains visual connection to master

**Key Insight**: Multiple implementation options depending on content complexity and device constraints

**Relevance to Our Design**: Applicable to encounter details, document viewing, and resource browsing. Choice of specific pattern depends on information density and user device context.

&nbsp;

### Drawer/side panel pattern (modern web apps)

**Used by**: Asana, Notion, Linear

**When to Use**: Showing detailed information without losing master list context

**Key Features**:
- User can interact with both master list and detail panel simultaneously
- Good for sequential review (next/prev navigation)
- Inline editing without full-page navigation
- Panel can be resized or collapsed

**Key Insight**: Works well when users need to review multiple items sequentially while keeping list visible

**Relevance to Our Design**: Strong candidate for document viewing within encounter context. Allows browsing document list while viewing document details.

**Visual Examples**: See Figures 3-6 in [Appendix](#visual-examples) for side panel implementations.

&nbsp;

### Research findings

**EHR Navigation Studies**:
- Providers navigate screens in highly variable patterns; reducing context switching improves efficiency
- Integrated views showing data from multiple sources within primary context improve workflow and reduce safety risks
- Progressive disclosure: Healthcare apps manage complexity by showing essentials first, details on demand

**Patient Research Insights**:
- Information consolidation is critical unmet need affecting both patients and providers
- Navigation efficiency matters - every click counts
- Context must be maintained to prevent errors and maintain situational awareness
- Solutions must consolidate within existing workflows, not create additional places to look

### Competitive summary table

| Pattern | Maintains Context | Screen Space | Complexity | Mobile-Friendly | Best For |
|---------|------------------|--------------|------------|-----------------|----------|
| Tabs Within Parent | ✓ High | Efficient | Low | ✓ Yes | Encounter details, resource categories |
| Split View | ✓ High | Needs more | Medium | Partial | Document viewing on desktop |
| Slide-out Panel | ✓ Medium | Efficient | Low | ✓ Yes | Document details, quick previews |
| Separate Page | ✗ Low | Maximum | Medium | ✓ Yes | Deep document editing/annotation |

&nbsp;

---

## Release 1: Core functionality

Release 1 focuses on three integrated work streams that establish the foundation for our PHR system. These capabilities work together to support clinician-driven encounter documentation and efficient information access.

### Work stream 1: Patient encounter details management

**Goal**: Streamline how clinicians access and navigate patient encounter information within the PHR

**Core Capabilities**:

**1.1 Encounter list and navigation**
- View all encounters for a patient in chronological order
- Filter encounters by date range, provider, encounter type
- Quick preview of encounter key details (date, provider, chief concern, status)
- Navigate between encounters while maintaining patient context

**1.2 Encounter detail view**
- Comprehensive encounter information organized into logical sections:
  - Chief concern / reason for visit
  - Subjective (patient-reported symptoms, history)
  - Objective (vital signs, observations, exam findings)
  - Assessment (diagnosis, clinical impression)
  - Plan (treatment plan, follow-up, medications prescribed)
- Associated resources (documents, lab results, imaging) linked to encounter
- Encounter timeline showing progression of care
- Patient context always visible (demographics, allergies, active conditions)

**1.3 Encounter creation and management**
- Create new encounter from worklist or patient chart
- Specify encounter type (office visit, telehealth, hospital admission, etc.)
- Associate providers and care team members
- Link existing documents and resources to encounter
- Edit and update encounter details
- Close/finalize encounter with summary

**UI Exploration**: Multiple prototypes being evaluated:
- Embedded tabs (Epic pattern) - encounter as tab within patient details
- Right-side drawer - encounter slides in while patient overview remains visible
- Split view - side-by-side patient overview and encounter details
- Enhanced slideout - improved modal with patient context embedded
- Drill-down with sticky header - separate page with patient context header

**Decision Criteria**: User testing will validate which pattern best supports:
- Maintaining patient context during encounter review
- Efficient navigation between multiple encounters
- Minimal clicks to access encounter details
- Intuitive workflow from worklist → patient → encounter

**Success Metrics**:
- Time to locate specific encounter information (target: <30 seconds)
- Navigation efficiency (clicks from worklist to encounter detail)
- Context retention (can users recall patient details while viewing encounter)
- User preference scores (SUS - System Usability Scale)

&nbsp;

### Work stream 2: Document viewing and resource management

**Goal**: Provide contextual access to documents and resources associated with patient encounters

**Core Capabilities**:

**2.1 Document organization**
- Documents organized by encounter (primary view)
- Alternative views: by date, by document type, by source
- Document categories: Lab results, imaging reports, consultation notes, patient-uploaded documents, care plans
- Visual indicators for document source (provider-uploaded vs patient-uploaded vs system-generated)
- Document status (pending review, reviewed, archived)

**2.2 Document viewing**
- In-line preview of common formats (PDF, images, text documents)
- Full-screen document viewer when needed
- Document metadata: upload date, source, associated encounter, document type
- Document versioning (if applicable)
- Next/previous navigation within document list

**2.3 Document linking and context**
- Link documents to specific encounters
- Tag documents with relevant conditions or health concerns
- Search documents by content (OCR for images, full-text search for PDFs)
- Related documents suggested based on context

**UI Pattern Considerations**:
- Drawer/side panel pattern strong candidate - browse document list while viewing details
- Split view for desktop users needing to reference multiple documents
- Mobile: full-screen viewer with clear back navigation

**Success Metrics**:
- Time to locate specific document (target: <45 seconds)
- Document view completion rate (users actually review documents they open)
- User satisfaction with document organization
- Reduction in "couldn't find document" incidents

&nbsp;

### Work stream 3: Summary generation

**Goal**: Automatically generate comprehensive, readable health summaries from both structured data and AI-extracted information

**Core Capabilities**:

**3.1 Health summary generation**
- On-demand summary generation (not automatic - performance considerations)
- Synthesis across multiple data sources:
  - Structured patient data (demographics, conditions, medications)
  - AI-extracted data from documents and conversations
  - Encounter history
  - Lab results and vital signs trends
- Organized by health domains:
  - Patient Information
  - Active Conditions
  - Medications (current and past)
  - Allergies and Intolerances
  - Recent Vital Signs
  - Care Team
  - Recent Encounters
  - Pending Actions/Follow-ups

**3.2 Summary customization** (Future consideration for specialists)
- Specialty-specific summaries (orthopedic surgeon sees relevant subset)
- Configurable information depth
- Custom templates by use case (new patient consultation vs routine follow-up)
- Learning from provider corrections over time

**3.3 Summary quality and trust**
- AI-extracted data clearly marked (⚠️ indicator)
- Source attribution where possible
- Timestamp showing when summary was generated
- Record count showing number of source records synthesized
- Confidence scoring for extracted information

**3.4 Summary performance**
- Caching: First generation 30-50 seconds, subsequent views instant (<1 second)
- Manual refresh to regenerate with updated data
- Cache expiration: 24 hours
- Loading indicators during generation

**3.5 Summary sharing**
- Patient can generate and share summary with new providers
- Exportable formats (PDF, printable)
- Shareable link with access controls
- Patient selects which information to include in shared summary

**Success Metrics**:
- Summary accuracy (validated against known patient data, target: >90%)
- Generation performance (time to generate initial summary)
- User satisfaction with summary content and organization
- Time saved in appointment preparation (patient-reported)
- Provider confidence in summary accuracy
- Reduction in repeated history-taking

&nbsp;

---

## PHR access context

**Critical Design Consideration**: The PHR will be available from both patient-facing and clinical-facing applications from Release 1.

### Patient-side access

**Primary Use Cases**:
- View own health information and history
- Upload documents from any source (other providers, pharmacies, personal records)
- Prepare for appointments by reviewing and updating information
- Generate shareable summaries for new providers
- Manage document sharing permissions

**Key Requirements**:
- Mobile-first design (patients often access from phones)
- Simplified terminology and explanations
- Clear privacy controls and sharing settings
- Patient-friendly document upload flow
- Easy-to-understand health summaries

### Clinical-side access

**Primary Use Cases**:
- Review patient information during encounters
- Upload and process clinical documents
- Generate summaries for referrals or care coordination
- Document encounter details
- Review patient-uploaded documents

**Key Requirements**:
- Desktop-optimized for clinical workflow
- Fast, efficient navigation (time-sensitive environment)
- Clinical terminology and detail appropriate for providers
- Integration with clinical workflows (worklist, scheduling, etc.)
- Provider tools for document review and data validation

### Shared design principles

**Consistency**: Core information architecture should be recognizable across patient and clinical interfaces

**Context-Appropriate**: Terminology, detail level, and feature access tailored to user type

**Data Symmetry**: Patients and providers see the same underlying health information, with appropriate permissions

**Collaboration**: Design supports patient-provider communication and shared decision-making

---

## Design patterns and prototypes

### Pattern exploration status

The team has been evaluating multiple prototypes with different approaches for structuring the interface, particularly for encounter details management. This exploration is ongoing and will inform final design decisions.

### Patterns under consideration

**1. Embedded Tabs (Epic Pattern)**
- Encounter details become tabs within Patient Details page
- Patient header always visible
- Clean, organized UI with familiar interaction pattern
- Risk: Tab bar clutter with multiple open encounters

**2. Right-Side Drawer (Modern App Pattern)**
- Encounter slides in from right, overlaying part of patient view
- Patient overview remains visible in background
- Maintains visual connection between patient and encounter
- Good for sequential encounter review

**3. Split View (Desktop Master-Detail)**
- Side-by-side: patient overview left, encounter details right
- Both views always visible
- Maximum information density
- Requires larger screens

**4. Enhanced Slideout with Patient Context**
- Improves existing slideout with embedded patient summary
- Progressive disclosure (quick preview → detailed view)
- Maintains current slideout muscle memory
- Risk: Still somewhat modal in nature

**5. Drill-Down with Sticky Patient Header**
- Navigate to encounter as full page
- Patient identity/context in sticky header
- Clear breadcrumb navigation
- Familiar pattern but doesn't fully solve context switching

### Decision framework

**Validation Through Prototype Testing**:
- Create interactive prototypes for top 2-3 patterns
- User testing with 4-6 clinical users (mix of specialists, nurses, clerks)
- Test tasks:
  - Navigate from worklist to specific encounter
  - Review encounter while referencing patient allergies
  - Compare details across multiple encounters for same patient
  - Return to worklist
- Measure:
  - Task completion time
  - Navigation efficiency (click count)
  - Context retention (memory tests)
  - User preference and confidence ratings

**Success Criteria**:
- Pattern maintains patient context throughout encounter review
- Minimizes navigation clicks (target: ≤3 clicks from worklist to encounter detail)
- Users can efficiently switch between encounters without losing orientation
- Mobile and desktop patterns may differ based on constraints

### Rationale documentation

Final design decision should document:
- Which patterns were prototyped and why
- User testing results and key findings
- Trade-offs considered
- Why chosen pattern best serves core use cases
- Known limitations and future improvements

---

## Development approach

### Work stream division

Given the complexity and breadth of Release 1, development will be divided into parallel work streams:

**Branch A: Patient encounter details management**
- Encounter list, navigation, detail views
- Patient context maintenance
- Encounter creation and editing
- UI pattern implementation

**Branch B: Document viewing**
- Document organization and viewing
- Document linking to encounters
- Document navigation and search
- UI pattern implementation for document access

**Branch C: Summary generation**
- Summary generation engine
- Data synthesis across sources
- Caching and performance optimization
- Summary customization (initial implementation)

**Integration points**:
- Encounter details link to associated documents (A ↔ B)
- Summaries pull from encounter data and documents (C depends on A & B)
- Document viewing provides context within encounters (B ↔ A)

### Technical considerations

**Performance**:
- Summary generation: 30-50 seconds first time, <1 second cached
- Page load times: <2 seconds for encounter views
- Mobile optimization: Lazy loading for document previews
- Document viewing: Fast preview rendering

**Data model**:
- Encounters as first-class objects linking patients, providers, documents
- Document provenance tracking (source, upload date)
- AI extraction metadata (confidence scores, review status)
- Summary cache with expiration

**AI/ML components**:
- NLP for structured data extraction from clinical text
- Entity recognition (medications, conditions, lab values)
- Summary generation LLM with prompt engineering

---

## Success metrics and validation

### Alpha testing (internal staff) - Week 1-2

**Participation Goals**:
- 100% of internal staff test at least one work stream
- At least 30 diverse test scenarios executed
- Coverage across encounter types, document types, patient profiles

**Quality Goals**:
- <5 critical bugs blocking core workflows
- >90% data accuracy in AI extraction (validated against known data)
- Performance within targets (summary generation, page loads)

**Feedback Goals**:
- Structured feedback from >10 staff members
- Top 5 improvement areas identified per work stream
- Edge cases documented

### Beta testing (select clinical users) - Week 3-4

**User groups**:
- 2-3 specialist physicians
- 1-2 nurses
- 1-2 MOAs/clerks

**Workflow validation**:
- End-to-end encounter documentation workflow
- Document viewing and navigation within encounters
- Summary generation for new patient consultations
- Multi-encounter review workflows

**Success Criteria**:
- >80% task completion rate
- Positive user satisfaction (SUS score >70)
- Measurable time savings vs. current workflow
- Users express willingness to adopt in production

### Release 1 success definition

The release will be considered successful when:

**Adoption**:
- ✅ >70% of active clinical users access PHR within first month
- ✅ >100 encounters documented using new system
- ✅ >200 health summaries generated

**Quality**:
- ✅ <10 critical bugs per month after launch
- ✅ >90% data accuracy in AI extraction
- ✅ >85% user satisfaction scores

**Impact**:
- ✅ Measurable time savings in patient chart preparation (target: 30% reduction)
- ✅ Reduction in repeated patient history-taking (patient-reported)
- ✅ Fewer "missing information" delays in appointments
- ✅ Positive provider feedback on information consolidation

---

## Known limitations and future roadmap

### Release 1 limitations

**Summary Generation**:
- Manual refresh only (no auto-update after conversations or uploads)
- No historical version tracking
- No source attribution click-through
- Single summary type (not yet customizable by specialty)

**Document Ingestion**:
- OCR accuracy varies by document quality
- AI extraction requires provider review for clinical decision-making
- No real-time processing (background jobs only)

**Encounter Management**:
- Basic encounter structure (not fully customizable)
- Limited encounter templates
- No multi-provider co-documentation

**Context Switching**:
- UI pattern not yet finalized (pending prototype testing)
- May not fully eliminate all navigation friction

### Future enhancements (post-release 1)

**Phase 2: Enhanced Customization**
- Specialty-specific summary templates
- Configurable encounter templates
- Custom document categorization rules
- Provider-specific default views

**Phase 3: Advanced Intelligence**
- Automated summary updates
- Predictive document linking
- Anomaly detection (missing expected documents)
- Trend analysis and visualization

**Phase 4: Collaboration & Communication**
- Multi-provider encounter co-documentation
- In-app secure messaging around encounters
- Patient feedback loop on AI-extracted data
- Shared decision-making tools

---

## Appendix

### Visual examples

**Figure A: Current State - Encounter Details**

![Current State: Encounter Details](images/current-state-encounter-details.png)

&nbsp;

**Figure B: Current State - Patient Details**

![Current State: Patient Details](images/current-state-patient-details.png)

&nbsp;

---

**Figure 1: Epic EMR - Patient Chart with MAR Tab**

![Epic EMR MAR View](images/EPIC-EMR-Chart.png)

This screenshot demonstrates Epic's tabbed approach within the patient chart. Key observations:
- Patient context (Ellie Johnson, demographics, allergies) always visible in left sidebar
- Top navigation tabs: Summary, Chart Review, Work List, MAR, Flowsheets, Notes, etc.
- Current view shows MAR (Medication Administration Record) without losing patient context
- User can switch between different data views (medications, encounters, labs) via tabs while maintaining awareness of which patient they're viewing

&nbsp;

**Figure 2: Epic EMR - Encounter Details Within Patient Chart**

![Epic EMR Encounter View](images/EPIC-EMR-Encounter.png)

This screenshot shows how Epic displays encounter details while maintaining patient context:
- Patient information (Test Test, demographics) remains in left sidebar
- Encounter-specific information shown in main content area: date "5/31/2022 visit with Danielle Joset, PharmD"
- Tabs within encounter: SnapShot, Chart Review, Immunizations, MAR, Communications, etc.
- Progress Notes displayed as primary content with encounter documentation
- Patient's medical history, medications, and social determinants visible in sidebar

**Key Pattern**: Both examples show how Epic never separates encounter details from patient context. Whether viewing medications, encounters, or documentation, the patient sidebar remains consistently visible, preventing users from losing context about which patient they're working with.

&nbsp;

---

**Figure 3: Asana - Side Panel Detail View**

![Asana Side Panel](images/Asana-Side-Panel.png)

Asana's implementation of the side panel pattern for task details:
- Task list remains visible on the left (master view)
- Task details slide in from the right (detail panel)
- Users can click through multiple tasks without losing context of the project/list
- Panel can be closed to return to full list view

&nbsp;

**Figure 4: Asana - Tab View Within Panel**

![Asana Tab View](images/Asana-tab-view.png)

Asana organizes task details using tabs within the side panel:
- Main task information in default view
- Additional tabs for subtasks, attachments, comments
- Tabs keep the panel organized while providing access to comprehensive information
- Pattern combines tabs + side panel for maximum organization

&nbsp;

**Figure 5: Notion - Side Panel for Page Details**

![Notion Side Panel](images/Notion-Side-Panel.png)

Notion's side panel pattern for viewing page details:
- Main workspace remains visible in background
- Page details open in right panel
- Users can reference multiple pages simultaneously
- Maintains context while drilling into specific content

&nbsp;

**Figure 6: Linear - Collapsible Side Panel**

![Linear Collapsible Side Panel](images/Linear-Collapsible-Side-Panel.png)

Linear's collapsible side panel for issue details:
- Issue list visible on left
- Issue details in expandable right panel
- Panel can be resized or collapsed as needed
- Supports rapid issue triage while maintaining list context

**Key Pattern Across Modern Apps**: All examples show detail panels that:
1. Maintain visual connection to the master list
2. Allow interaction with both master and detail simultaneously
3. Support sequential navigation (next/prev) within the panel
4. Can be closed/collapsed to return to full master view

&nbsp;

---

## References

### Research studies

**Provider User Interviews**
- [Provider User Interviews - Codebook Document](https://docs.google.com/document/d/1svSyUI48qHtXXlLGqaLLJGelYn2v9ipRxpRAUhzYpWg/edit?usp=drive_link)
- Provider Analysis Report (n=22 providers, November 2024)
- Provider Insights Library

**Patient User Interviews**
- Patient Analysis Report (n=14 patients/caregivers, September-October 2025)
- Patient Insights Library
- Thematic Analysis Codebook

### Epic EMR pattern

1. University of Iowa Epic Education - Chart Review: [https://epicsupport.sites.uiowa.edu/epic-resources/chart-review](https://epicsupport.sites.uiowa.edu/epic-resources/chart-review)
2. Johns Hopkins Medicine - Epic Tips and Tricks (2019): [https://www.hopkinsmedicine.org/news/articles/2019/08/epic-shortcuts-experts-share-their-favorite-tips](https://www.hopkinsmedicine.org/news/articles/2019/08/epic-shortcuts-experts-share-their-favorite-tips)

### Master-detail UI patterns

3. Oracle Alta UI - Master-Detail Pattern: [https://www.oracle.com/webfolder/ux/middleware/alta/patterns/MasterDetail.html](https://www.oracle.com/webfolder/ux/middleware/alta/patterns/MasterDetail.html)
4. Oracle Alta Mobile - Master Detail: [https://www.oracle.com/webfolder/ux/mobile/pattern/masterdetail.html](https://www.oracle.com/webfolder/ux/mobile/pattern/masterdetail.html)
5. Microsoft Windows Developer Blog - Master the Master-Detail Pattern (2017): [https://blogs.windows.com/windowsdeveloper/2017/05/01/master-master-detail-pattern/](https://blogs.windows.com/windowsdeveloper/2017/05/01/master-master-detail-pattern/)
6. Web App Huddle - Master-Detail UI Pattern Design (2019): [https://webapphuddle.com/master-detail-ui-pattern-design/](https://webapphuddle.com/master-detail-ui-pattern-design/)

### EHR navigation research

7. Coleman et al. - Analysing EHR navigation patterns and digital workflows among physicians during ICU pre-rounds: [https://pmc.ncbi.nlm.nih.gov/articles/PMC8435833/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8435833/)
8. Usability Challenges in Electronic Health Records: Impact on Documentation Burden and Clinical Workflow (2025): [https://pmc.ncbi.nlm.nih.gov/articles/PMC12206486/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12206486/)
9. Studying workflow and workarounds in EHR-supported work to improve health system performance: [https://pmc.ncbi.nlm.nih.gov/articles/PMC8061456/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8061456/)
10. Melton et al. - Usability Testing of Two Ambulatory EHR Navigators (2016): [https://pmc.ncbi.nlm.nih.gov/articles/PMC4941856/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4941856/)
