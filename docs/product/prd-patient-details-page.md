# PRD: Patient Details Page - Unified Encounter Navigation

## 1. Overview

| Field | Details |
|-------|---------|
| **Title** | Patient Details Page Redesign - Unified Encounter Navigation |
| **Team** | Clinical / Provider |
| **Author(s)** | Product Team, Engineering Team |
| **Status** | ✅ **SHIPPED** |
| **Date Created / Updated** | November 20, 2025 |

## Changelog

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| Nov 20, 2025 | 1.0 | Initial implementation: Folder navigation pattern, unified encounter view, removed standalone encounter details page, added responsive "View Patient" button in slideout | Engineering Team |

---

## 2. Problem Statement — The Why

### User Persona(s):
- **Primary**: Healthcare providers viewing patient records and encounter details
- **Secondary**: Clinical staff managing patient encounters from worklist

### Problem Summary:
Providers are confused by multiple similar views for encounter details and struggle to navigate between patient context and encounter information. The standalone encounter details page creates a disjointed experience where providers lose patient context when viewing encounter information, leading to inefficient workflows and navigation confusion.

### Evidence / Insights:
- **Usability feedback**: Users reported confusion about which view they're in (patient details vs. encounter details)
- **Navigation patterns**: Providers frequently needed to switch between patient context and encounter details
- **Workflow inefficiency**: Standalone encounter page required extra clicks to access patient information

### Why Now:
- **Strategic importance**: Aligns with product goal to create unified, context-aware clinical workflows
- **User experience**: Reduces cognitive load and navigation complexity for providers
- **Foundation for future work**: Establishes folder navigation pattern for other clinical entities (Forms, Summaries, Documents)

---

## 3. Hypothesis & Objectives

### Hypothesis
We believe that by **consolidating encounter details within the patient details page** for **healthcare providers**, we will achieve **faster access to patient context and reduced navigation confusion**, measured by **reduced clicks to access patient information and improved user satisfaction**.

### Objectives & Success Metrics

| Objective | Metric | Baseline | Target | Source / Tool |
|-----------|--------|----------|--------|---------------|
| Reduce navigation clicks | Average clicks to view patient from encounter | 2-3 clicks | 1 click | Analytics |
| Improve context awareness | User confusion incidents | Multiple reported issues | Zero reported issues | User feedback |
| Streamline workflow | Time to access encounter details with patient context | N/A (new feature) | < 2 seconds | Performance monitoring |

---

## 4. Context & Constraints

### Technical Constraints:
- Django + HTMX architecture requires shared templates for slideout and inline views
- Need to maintain existing slideout functionality from encounter worklist
- URL parameter handling for deep linking to specific encounters

### Operational Constraints:
- Must maintain clear navigation path back to worklist
- Primary action ("Start New Encounter") must remain visually prominent
- Responsive design required for mobile/desktop views

### Regulatory / Privacy:
- Standard PHIPA/PIPEDA compliance for patient data display
- No additional privacy considerations beyond existing implementation

### Risks & Dependencies:
- **Adoption risk**: Users accustomed to standalone encounter page may need adjustment period
- **Navigation complexity**: Folder navigation pattern is new - requires clear visual design
- **Performance**: Inline encounter view must load quickly to maintain UX quality

---

## 5. Proposed Solution — The What

### Solution Summary:
Redesign the patient details page with a folder-style navigation sidebar that allows providers to view encounter details inline within patient context. Remove the standalone encounter details page and ensure all encounter views maintain patient context. Add a back button in the top navigation to clearly show "Encounters List" as the parent view.

### Core User Stories / Use Cases:

1. **As a provider**, I want to click "View Patient" from the worklist so I can see encounter details within full patient context
2. **As a provider**, I want to navigate between Overview, Encounters, Forms, Summaries, and Documents using a sidebar so I can quickly access different patient information
3. **As a provider**, I want a clear back button to return to the Encounters List so I know how to navigate back to my worklist
4. **As a provider**, I want to see the "View Patient" button in the encounter slideout (on desktop) so I can quickly navigate to the full patient view
5. **As a provider**, I want the encounter slideout to still work from the worklist so I can quickly preview encounter details without navigating away

### In Scope:
- ✅ Folder navigation sidebar (Overview, Encounters, Forms, Summaries, Documents)
- ✅ Inline encounter details view within patient details page
- ✅ Back button in top navigation showing "← Encounters List"
- ✅ "View Patient" outline button in slideout (desktop) and dropdown (mobile)
- ✅ Remove standalone encounter details page
- ✅ Shared encounter content template for slideout and inline views
- ✅ Status label consistency ("Archived" instead of "Completed")
- ✅ Remove duplicate navigation buttons (close buttons, redundant back arrows)
- ✅ Deep linking support via `?encounter_id=` parameter
- ✅ Responsive "View Patient" button (outline on desktop, dropdown on mobile)

### Out of Scope:
- Forms, Summaries, Documents folder implementations (future work)
- Active state indicators for sidebar navigation items
- Encounter list filtering/sorting within patient details
- Patient-level action menu redesign (maintaining existing pattern)

---

## 6. Design & Technical Notes

| Area | Links / Notes |
|------|---------------|
| **Design** | Folder navigation pattern with independent sidebar/content scrolling |
| **Technical Design Doc** | Django templates with HTMX for partial page updates. Shared `patient_encounter_content.html` template used for both slideout and inline views with `in_slideout` parameter |
| **Key Templates** | • `patient_details_new.html` - main page with custom top nav<br>• `patient_encounter_content.html` - shared encounter content<br>• `patient_sidebar_nav.html` - folder navigation<br>• `encounter_content_actions.html` - responsive action menu |
| **URL Routing** | • `?encounter_id=<uuid>` - display specific encounter<br>• `?slideout=true` - render for slideout modal<br>• `?from_list=true` - navigation context flag |
| **Migration** | `0084_alter_encounter_status.py` - Changed COMPLETED label to "Archived" |

---

## 7. Rollout Plan

| Phase | Description |
|-------|-------------|
| **Implementation** | ✅ Complete - All templates and views implemented |
| **Testing** | Manual testing in local environment |
| **Deployment** | Pushed to `prototype/patient-details-page` branch |
| **Post-Launch Review** | Monitor for navigation confusion or usability issues |

---

## 8. Measurement & Learnings

### Post-Launch Results

| Metric | Target | Actual | Variance | Notes |
|--------|--------|--------|----------|-------|
| Navigation clicks | 1 click | TBD | TBD | To be measured post-deployment |
| User confusion | Zero issues | TBD | TBD | Monitor support tickets and feedback |
| Performance | < 2s load | TBD | TBD | Monitor page load metrics |

### Key Learnings:
*To be filled post-launch*

- How do users respond to folder navigation pattern?
- Are there any unexpected navigation patterns?
- Does the responsive "View Patient" button work well on mobile?

### Next Steps:
*To be determined based on findings*

- Implement active state indicators for sidebar navigation
- Add Forms, Summaries, Documents folder views
- Consider adding encounter filtering within patient details

---

## 9. Open Questions

✅ **Resolved:**
- ✓ Should we remove the standalone encounter details page? **Yes - all flows through patient details**
- ✓ How should "View Patient" appear in slideout? **Outline button on desktop, dropdown on mobile**
- ✓ What should the status label be for completed encounters? **"Archived" to match Archive action**
- ✓ Should Overview show active state when viewing an encounter? **No - only show active when actually viewing overview**

**Outstanding:**
- Should we add filtering/sorting for encounters within patient details?
- What's the interaction pattern for Forms, Summaries, Documents folders?
- Should sidebar navigation items show active state for the selected folder?

---

## 10. Alignment & Approvals

| Role | Name | Date | Decision / Notes |
|------|------|------|------------------|
| Product | Peter Haralabous | Nov 20, 2025 | Approved design direction |
| Engineering | Engineering Team | Nov 20, 2025 | Implementation complete |
| Design | Design Team | Nov 20, 2025 | Design validated through iterative feedback |

---

## Implementation Details

### Key Changes Made:

**Navigation Pattern:**
- Replaced HealthConnect logo with "← Encounters List" back button in top nav for nested views
- Removed duplicate back buttons from patient header and content areas
- Added folder-style sidebar navigation (Overview, Encounters, Forms, Summaries, Documents)
- Independent scrolling for sidebar and main content area

**Encounter Management:**
- Reused encounter content template between patient details page and slideout modal (`in_slideout` parameter)
- Added "View Patient" outline button in encounter slideout (desktop) and dropdown menu (mobile)
- Removed standalone encounter details page - all flows now go through patient details
- Removed "View Details" from encounter list dropdown (slideout still accessible via row click)
- Simplified encounter actions: back button navigation instead of close buttons

**Status & Display:**
- Changed `EncounterStatus.COMPLETED` display label to "Archived" to match Archive action
- Use consistent status badges across lists and detail views
- Updated all redirects to use patient details page with `?encounter_id=` parameter

**Files Changed:**
- 16 files modified/created
- 834 insertions, 26 deletions
- 8 new template files for redesigned patient details page
- 1 migration for status label change
