# [Feature Name]

**Team**: [Clinical / Patient / Product Area]
**Owner**: [PM Name]
**Contributors**: [Eng Lead, Design Lead, other key stakeholders]

**Status**: 🔍 DISCOVER / 📋 DEFINE / 🛠️ DEVELOP / 🚀 DELIVER / 📊 SHIPPED

**Dates**:
- Created: [Date]
- Last Updated: [Date]
- Target Ship: [Date]

---

## Quick Navigation

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Hypothesis & Success Metrics](#hypothesis--success-metrics)
- [Context & Constraints](#context--constraints)
- [Solution Approach](#solution-approach)
- [Technical & Design](#technical--design-notes)
- [Rollout Plan](#rollout-plan)
- [Results & Learnings](#results--learnings)

---

## Overview

<!-- ✏️ FILL IN: DISCOVER phase - Write this after initial discovery -->
<!-- This is your executive summary. Keep it to 2-3 sentences. -->

**Purpose**: [What are we trying to achieve?]

**Background**: [Why is this initiative important? Link to product strategy.]

**Related documents**:
- [Discovery research](./discovery.md) - Full discovery findings and impact analysis
- [Product strategy](../product/product-strategy.md) - Strategic context

---

## Problem Statement

<!-- ✏️ FILL IN: DISCOVER → DEFINE phase -->
<!-- Start drafting during discovery, finalize in Define phase -->
<!-- This section should NEVER change once Define phase is complete -->

### User Personas

<!-- List primary and secondary personas affected -->

**Primary**: [e.g., Providers at referred-to clinics]
- Context: [When/where they experience this]
- Current behavior: [What they do today]

**Secondary**: [e.g., Patients waiting for referrals]
- Context: [When/where they experience this]
- Current behavior: [What they do today]

### The Problem

<!-- Describe the pain point clearly in 2-3 paragraphs -->
<!-- Focus on the problem, not the solution -->

[User persona] experiences [specific problem] when [context/situation].

**Impact on users**:
- [Pain point 1: e.g., Time wasted]
- [Pain point 2: e.g., Errors/frustration]
- [Pain point 3: e.g., Risk or missed opportunity]

**Current state**:
- [How users cope today - workarounds]
- [Why current solutions fall short]

**Why this matters**:
- **To users**: [User impact - time, success rate, satisfaction]
- **To business**: [Business impact - revenue, cost, strategy]
- **Strategically**: [How this aligns with product strategy goals]

### Evidence & Insights

<!-- Link to detailed findings in discovery.md -->
<!-- Summarize the most compelling evidence here -->

**Quantitative evidence**:
- [Data point 1: e.g., "30% of clinic time spent on manual referral management"]
- [Data point 2: e.g., "Average referral takes 14 days to complete"]
- [Data point 3: e.g., "40% of churned users cited this issue"]

**Qualitative insights**:
- [Interview finding 1 with quote]
- [Survey theme 2]
- [Support ticket pattern]

**Sources**:
- User research: [N interviews, N surveys] - [Link to discovery.md]
- Analytics: [Dashboard link]
- Competitive analysis: [Key findings] - [Link to discovery.md]

**See full research synthesis**: [discovery.md](./discovery.md)

### Why Now

<!-- Explain timing and urgency -->

**Strategic importance**:
- [Link to OKR or strategic goal]
- [Competitive pressure or market timing]

**Urgency factors**:
- [Regulatory deadline or compliance requirement]
- [Customer risk or competitive threat]
- [Technical enabler now available]

---

## Hypothesis & Success Metrics

<!-- ✏️ FILL IN: DEFINE phase -->
<!-- This is your prediction of what will happen if you solve the problem -->

### Hypothesis Statement

**We believe that** by [doing/building X] for [user type],

**We will achieve** [desired outcome],

**Measured by** [specific metric improvement].

<!-- Example: "We believe that by providing a unified referral dashboard for clinic providers, we will reduce referral completion time by 30%, measured by average days-to-completion in our EHR logs." -->

### Success Metrics

<!-- 🧠 Keep this focused: 1 primary + 2-3 secondary metrics -->
<!-- Define how you'll measure success BEFORE you build -->

| Objective | Metric | Baseline | Target | Timeline | Source |
|-----------|--------|----------|--------|----------|--------|
| **PRIMARY** | | | | | |
| [Main outcome] | [Metric name] | [Current] | [Goal] | [When] | [Where measured] |
| **SECONDARY** | | | | | |
| [Supporting outcome 1] | [Metric name] | [Current] | [Goal] | [When] | [Where measured] |
| [Supporting outcome 2] | [Metric name] | [Current] | [Goal] | [When] | [Where measured] |

**Leading indicators** (early signals we're on track):
- [Early metric 1: e.g., "Feature adoption rate"]
- [Early metric 2: e.g., "First-week engagement"]

**Counter-metrics** (watch for negative impacts):
- [Metric to monitor: e.g., "Ensure provider time per patient doesn't increase"]
- [Threshold: e.g., "Alert if increases >10%"]

### Analytics & Tracking

<!-- Define what events you need to track -->

**Events to instrument**:
- [ ] [Event 1]: Fires when [user action]
- [ ] [Event 2]: Fires when [user action]
- [ ] [Event 3]: Fires when [user action]

**Dashboard**: [Link to analytics dashboard]

**Measurement plan**:
- Week 1-2: Daily review
- Week 3-4: Every 2-3 days
- Month 2+: Weekly review

---

## Context & Constraints

<!-- ✏️ FILL IN: DEFINE phase -->
<!-- Document constraints that will shape the solution -->

### Technical Constraints

**System limitations**:
- [e.g., "EMR API has 2-second latency"]
- [e.g., "Data available only in batch updates, not real-time"]

**Architecture considerations**:
- [e.g., "Must work within existing authentication system"]
- [e.g., "Performance requirement: <500ms page load"]

**Technical dependencies**:
- [ ] [Dependency 1: e.g., "Requires EMR integration upgrade"]
- [ ] [Dependency 2: e.g., "Depends on new API from Team X"]

### Operational Constraints

**Workflow considerations**:
- [e.g., "Different clinics have different referral processes"]
- [e.g., "Training required for 300+ providers"]

**Integration timing**:
- [e.g., "Must launch before Q4 clinic onboarding wave"]
- [e.g., "Cannot disrupt during peak flu season"]

**Resource constraints**:
- [e.g., "Support team capacity for 2 weeks post-launch"]
- [e.g., "Design resources shared with other project"]

### Regulatory & Privacy

**Compliance requirements**:
- [e.g., "PHIPA compliant - no PHI in logs"]
- [e.g., "HIPAA security protocols required"]
- [e.g., "Audit trail for all data access"]

**Data handling**:
- [e.g., "Patient data retention policy: 7 years"]
- [e.g., "Encryption at rest and in transit"]

**Privacy considerations**:
- [e.g., "Caregiver access requires explicit consent"]

### Risks & Dependencies

**Key risks**:
- **[Risk 1]**: [e.g., "Adoption - Providers resistant to workflow change"]
  - Likelihood: 🔴 High / 🟡 Medium / 🟢 Low
  - Impact: 🔴 High / 🟡 Medium / 🟢 Low
  - Mitigation: [Strategy]

- **[Risk 2]**: [e.g., "Performance - Dashboard slow with large referral volume"]
  - Likelihood: 🟡 Medium
  - Impact: 🔴 High
  - Mitigation: [Strategy]

**External dependencies**:
- [e.g., "Team X must deliver API by [date]"]
- [e.g., "Legal review of consent flow"]

---

## Solution Approach

<!-- ✏️ FILL IN: DEVELOP phase -->
<!-- This section evolves as you prototype and test solutions -->

### Solution Evolution

<!-- 🧠 Show the journey - what you tested and what you learned -->
<!-- This helps future teams understand why decisions were made -->

#### Exploration: Concepts Tested

**Approach 1: [Name]**
- **Concept**: [Brief description]
- **Tested via**: [Figma prototype / Paper sketch / Working prototype]
- **Results**:
  - ✅ What worked: [Finding]
  - ❌ What didn't: [Finding]
- **Key learning**: [1-2 sentence insight]

**Approach 2: [Name]**
- **Concept**: [Brief description]
- **Tested via**: [Method]
- **Results**: [Summary]
- **Key learning**: [Insight]

**See detailed prototype feedback**: [prototype-feedback.md](./prototype-feedback.md)

---

### Final Solution: [Name]

<!-- ✏️ FINALIZE IN: DELIVER phase -->
<!-- This is what you're actually building -->

#### Solution Summary

<!-- High-level description in 2-3 paragraphs -->

[Describe the solution approach that emerged from prototyping]

**Why this approach**:
- [Reason 1: Based on prototype testing]
- [Reason 2: Balances feasibility with impact]
- [Reason 3: Aligns with technical constraints]

**Core value proposition**:
- [Main benefit to users]
- [How it solves the problem]

---

#### Core Features (MVP)

<!-- User-centered feature descriptions -->

**Feature 1: [Name]**

**User story**: As a [user type], I want to [action] so that [outcome].

**What it does**: [Clear description]

**Why it matters**: [How it solves problem from problem statement]

**Acceptance criteria**:
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

---

**Feature 2: [Name]**

[Same structure]

---

**Feature 3: [Name]**

[Same structure]

---

#### In Scope for V1

<!-- Clear boundaries for MVP -->

**Included**:
- [Capability 1]
- [Capability 2]
- [Capability 3]

**Not Included** (out of scope for V1):
- [Feature X] - Reason: [Why deferred]
- [Feature Y] - Reason: [Why deferred]
- [Feature Z] - Reason: [Won't do - explain why]

---

#### User Experience

**Key user flows**:
1. [Flow 1: e.g., "Provider reviews referral queue"]
   - [Step 1]
   - [Step 2]
   - [Step 3]

2. [Flow 2: e.g., "Patient checks referral status"]
   - [Step 1]
   - [Step 2]

**Edge cases & error handling**:
- **Scenario 1**: [What happens when X]
  - Expected behavior: [How system responds]
  - Error message: [What user sees]

- **Scenario 2**: [What happens when Y]
  - Expected behavior: [How system responds]

---

## Technical & Design Notes

<!-- ✏️ FILL IN: DEVELOP → DELIVER phase -->
<!-- Links to detailed specs and designs -->

| Area | Document | Status | Notes |
|------|----------|--------|-------|
| **Design** | [Figma prototype](link) | ✅ Complete | Final designs approved |
| **Technical Spec** | [Engineering doc](link) | 🔄 In progress | API design under review |
| **Analytics Plan** | [Tracking spec](link) | ✅ Complete | Events instrumented |
| **API Documentation** | [API spec](link) | ✅ Complete | |
| **Security Review** | [Security doc](link) | 🔄 Pending | Scheduled for [date] |

### Architecture Overview

<!-- High-level technical approach -->

[Brief description or diagram of technical architecture]

**Key technical decisions**:
- [Decision 1: e.g., "Using PostgreSQL for referral data"]
- [Decision 2: e.g., "Real-time updates via WebSockets"]

### Data Model

<!-- If relevant, describe key data structures -->

**Key entities**:
- [Entity 1: e.g., "Referral"] - [Key attributes]
- [Entity 2: e.g., "Provider"] - [Key attributes]

### Performance Requirements

- Page load: [<2 seconds]
- API response: [<500ms]
- Concurrent users: [500+]
- Data freshness: [Real-time / 5-minute delay / etc.]

---

## Rollout Plan

<!-- ✏️ FILL IN: DELIVER phase -->
<!-- How you'll release this to users -->

### Release Strategy

| Phase | Timeline | Audience | Goal | Success Criteria |
|-------|----------|----------|------|------------------|
| **Internal Beta** | [Week 1-2] | [Team members] | Catch critical bugs | No blockers found |
| **Pilot** | [Week 3-4] | [2-3 clinics, 50 providers] | Validate in real environment | 80%+ satisfaction, no major issues |
| **Limited Launch** | [Week 5-6] | [25% of users] | Monitor metrics, gather feedback | Metrics trending toward targets |
| **Full Rollout** | [Week 7+] | [All users] | Achieve success metrics | Hit targets within 90 days |

### Feature Flags & Controls

**Flags in use**:
- `enable_referral_dashboard` - Controls access to new UI
- `enable_real_time_updates` - Controls WebSocket connections

**Rollback plan**:
- [How to disable feature if critical issue found]
- [Data preservation strategy]

### Launch Checklist

**Pre-launch**:
- [ ] Security review complete
- [ ] Analytics instrumented and tested
- [ ] Documentation updated (user guides, support docs)
- [ ] Support team trained
- [ ] Monitoring dashboards set up
- [ ] Stakeholders notified

**Launch communications**:
- [ ] In-app announcement: [Draft link]
- [ ] Email to users: [Draft link]
- [ ] Support team briefing: [Scheduled for date]
- [ ] Changelog update: [Link]

**Post-launch**:
- [ ] Day 1 health check
- [ ] Week 1 metrics review
- [ ] Week 4 success analysis
- [ ] Feedback collection and synthesis

---

## Results & Learnings

<!-- ✏️ FILL IN: POST-LAUNCH -->
<!-- Update this as data comes in -->

### Launch Summary

**Launched**: [Date]
**Rollout**: [Pilot → Limited → Full, with dates]
**Adoption**: [X users, Y% of target segment]

---

### Metrics Performance

<!-- Update this at 30/60/90 days post-launch -->

**Measured at**: [30 days / 60 days / 90 days post-launch]

| Metric | Target | Actual | Variance | Status | Notes |
|--------|--------|--------|----------|--------|-------|
| **PRIMARY** | | | | | |
| [Primary metric] | [Goal] | [Result] | [+/- X%] | 🟢/🟡/🔴 | [Context] |
| **SECONDARY** | | | | | |
| [Secondary 1] | [Goal] | [Result] | [+/- X%] | 🟢/🟡/🔴 | [Context] |
| [Secondary 2] | [Goal] | [Result] | [+/- X%] | 🟢/🟡/🔴 | [Context] |

**Overall assessment**: [On track / Needs attention / Exceeding expectations]

---

### User Feedback

**Sentiment**: [NPS score or CSAT]

**Top positive themes**:
- [Theme 1: e.g., "Love the unified view"]
- [Theme 2: e.g., "Much faster than before"]

**Top concerns**:
- [Concern 1: e.g., "Notification timing confusing"]
- [Concern 2: e.g., "Missing filter by urgency"]

**Representative quotes**:
> "[Positive user quote]" - [User segment]
> "[Critical user quote]" - [User segment]

---

### What We Learned

**Validated assumptions**:
- ✅ [Assumption 1: e.g., "Providers would adopt unified dashboard"]
  - Evidence: [What we observed]
- ✅ [Assumption 2: e.g., "Would reduce completion time"]
  - Evidence: [What we observed]

**Invalidated assumptions**:
- ❌ [Assumption 3: e.g., "Thought patients would check status daily"]
  - Reality: [What actually happened]
  - Implication: [What this means]

**Surprises**:
- 💡 [Unexpected finding 1: e.g., "Caregivers became primary users"]
- 💡 [Unexpected finding 2: e.g., "Peak usage at 8am, not midday"]

---

### Issues Encountered

**Issue 1: [Name]**
- **What happened**: [Description]
- **Impact**: [Severity and user impact]
- **Resolution**: [How we fixed it]
- **Timeline**: [Detected → Fixed]

**Issue 2: [Name]**
[Same structure]

---

### Next Steps

**Immediate priorities** (next 30 days):
1. [Priority 1: e.g., "Fix notification timing based on feedback"]
2. [Priority 2: e.g., "Add filter by urgency (top user request)"]

**V1.1 scope** (next quarter):
- [Enhancement 1]
- [Enhancement 2]

**Future considerations** (V2+):
- [Idea 1: Based on learnings]
- [Idea 2: Adjacent problem space]

**Retrospective insights**:
- What went well: [Process/decision that worked]
- What to improve: [Learning for next feature]

---

## Open Questions

<!-- ✏️ USE THROUGHOUT: Track unknowns that need resolution -->
<!-- Remove questions as they're answered, keep log of decisions -->

**Active questions**:
- [ ] [Question 1: e.g., "What permission model for caregiver access?"]
  - Owner: [Who's resolving this]
  - By when: [Deadline]
  - Blocking: Yes / No

- [ ] [Question 2: e.g., "Do we support patient-initiated referrals in MVP?"]
  - Owner: [Who's resolving]
  - By when: [Deadline]
  - Blocking: Yes / No

**Resolved questions**:
- ✅ ~~[Question 3: e.g., "Which EHR integration approach?"]~~
  - **Decision**: [What was decided]
  - **Rationale**: [Why]
  - **Date**: [When decided]

---

## Alignment & Approvals

<!-- ✏️ FILL IN: DEFINE phase (for go/no-go) and DELIVER phase (for spec approval) -->

### Define Phase: Go/No-Go Decision

| Role | Name | Date | Decision |
|------|------|------|----------|
| Product | [Name] | [Date] | ✅ Proceed / ❌ Kill |
| Engineering | [Name] | [Date] | ✅ Feasible / 🟡 Concerns / ❌ Not feasible |
| Design | [Name] | [Date] | ✅ Approved / 🔄 Needs work |
| Leadership | [Name] | [Date] | ✅ Approved / 🔄 More info needed |

**Decision**: [Proceed to Develop / Need more research / Kill]

**Notes**: [Key discussion points or conditions]

---

### Deliver Phase: Spec Approval

| Role | Name | Date | Status |
|------|------|------|--------|
| Product | [Name] | [Date] | ✅ Approved |
| Engineering | [Name] | [Date] | ✅ Approved |
| Design | [Name] | [Date] | ✅ Approved |
| Security | [Name] | [Date] | ✅ Approved / 🔄 Review pending |
| Legal | [Name] | [Date] | ✅ Approved / N/A |

**Final approval date**: [Date ready for development]

---

## Document History

| Date | Phase | Change | Author |
|------|-------|--------|--------|
| [Date] | Discover | Created PRD with problem statement | [Name] |
| [Date] | Define | Added hypothesis and success metrics | [Name] |
| [Date] | Develop | Added solution approach from prototyping | [Name] |
| [Date] | Deliver | Finalized spec and rollout plan | [Name] |
| [Date] | Post-launch | Added 30-day results | [Name] |

---

## Related Documents

- **Discovery research**: [discovery.md](./discovery.md) - Full research synthesis and impact analysis
- **Prototype feedback**: [prototype-feedback.md](./user-feedback.md) - Detailed testing iterations
- **Product strategy**: [product-strategy.md](../strategy/product-strategy.md)
- **Release notes**: [release-notes.md](./release-notes.md) - Public-facing launch notes
