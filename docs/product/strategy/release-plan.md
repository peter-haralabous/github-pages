# Thrive Health Release Plan

**PHR Vision → Product: Key Product Milestones**

**Document Date:** November 2025
**Subtitle:** Transforming Canadian Healthcare with AI-powered Universal PHR

---

## Overview

This document outlines the committed path to production for both Personal and Clinical product suites, built on the PHR platform foundation. These releases validate our PHR vision through real-world workflows with early adopter providers and patients.

---

## PHR Vision Context

### What is the "PHR Platform"?

- A universal PHR is the core of how we can transform healthcare and must drive our product design, architecture as well as fundamental decisions about licensing, go to market, privacy, consent and more.
- **The PHR is NOT a product in itself.** It is an idea, an outcome, a platform, an operating system. Our products use the power of the PHR at the core.
- The PHR vision is NOT an external message (yet). We must focus on the value propositions we can provide as a result of the PHR power, but our vision of achieving a network effect and de facto standard around a universal PHR should be internal only.
- PHR vision requires challenging current norms - solving familiar challenges and use cases in fundamentally different ways and accepting that the path to success will not be easy or direct.

### PHR Foundational Tenets

Guiding every decision and product priority:

1. **Primacy of the Individual.** The person, the patient, must be the centre of our design - defining our approach not just being part of workflows.

2. **One Person, One Truth.** There must be only one complete and accurate representation of the individual. Existing fragmented silos may remain, we will not create another.

3. **The Person Owns Their Data.** The individual has a fundamental right to all of their personal health data and are the owner. Thrive is not the data owner, but a trusted and transparent steward for the person and their data.

---

## Product Architecture

### PHR Platform vs Products vs Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│                  Clinical Product Suite                          │
│  - Referral Management    - Patient Intake                      │
│  - Waitlist Management    - Ongoing Patient Support             │
│  - Patient Insights       - Discharge Support                   │
│  - Future: Clinic & Organizational Data                         │
├─────────────────────────────────────────────────────────────────┤
│                  Personal Product Suite                          │
│  - Trusted Health Records Repository                            │
│  - Alerts, Actions, Summaries                                   │
│  - Care Network Communication                                   │
│  - Future: Chronic Cond. Mgmt, Senior Care, Personalized       │
│    guidance and recommendations                                 │
├─────────────────────────────────────────────────────────────────┤
│                    PHR PLATFORM                                  │
│              Person Centred | One Truth | Patient Owned         │
├─────────────────────────────────────────────────────────────────┤
│            Trusted Innovative Infrastructure                     │
│      World-class privacy, security and compliance               │
│              Responsible, effective AI                           │
└─────────────────────────────────────────────────────────────────┘
```

### Inside the PHR Platform

**PHR Content Core:**
- **Repository** (Long Term Memory): Organized documents and content
- **Health Facts** (Long Term Memory): Structured health information
- **Health Context** (Short Term Memory): AI interpretation, connections and insights - constantly learning and improving

**Application Layer:**
- Facts Edit
- Conversation
- Engagement
- Form Completion
- Structured Data Upload/Export
- Unstructured Data Ingest

**AI Agentic Layer:**
- Summaries
- Recommendations
- Actions/Alerts
- Investigation

---

## Milestone Release Timeline

```
Nov 28          Dec 15          Jan 30          Mar 31, 2026
────●──────────────●──────────────●──────────────●────────>

Personal:       Alpha           Beta            Release 1.0
                Internal        External        Public release
                pilot           beta pilot      Includes patient
                                               intake support

Clinical:                       Alpha           Beta            Release 1.0
                                Internal        Cont.           External release
                                validation      validation      Patient intake
                                with early      with early      early adopters
                                adopter         adopter         (PRATT, ENT)
                                providers       providers
                                                                Early validation:
                                                                referral & waitlist
                                                                management (CfHA)
```

---

## Personal Product: Alpha Release

**Release Date:** November 28, 2025

**Audience:** Internal Thrive staff, and possibly select friends/family users

### Release Summary
Establish the foundation for the Health Connect Personal experience. It validates that users can naturally add health documents and notes and start to see their unstructured health data organized into a personal health record.

### What's Included

- **Add multiple health documents and notes through natural conversation.** View data automatically summarized and linked to its source.
- **Refresh summary on demand.**
- **Edit, delete, and manage health records directly** (limited set at launch: Conditions, Practitioners, Immunizations).
- **Browse an organized repository of documents and notes in one place.**

### What's Not Yet Included

- Form completion and intake workflows (planned for Beta Release – Jan 2026)
- Viewing health data in different summary formats (planned for Beta Release – Jan 2026)

### Why It Matters

- Confirms the conversational model as the foundation for all user interaction.
- Establishes the "one record, one truth" data model.
- Demonstrates early comprehension, trust, and usability metrics ahead of Beta.

### Success Indicators (learning phase)

- 100% of users successfully upload and view records
- ≥80% describe the process as "clear and natural"
- Positive early feedback on comprehension and organization

---

## Clinical Product: Alpha Release

**Release Date:** December 15, 2025

**Audience:** Early adopter providers (PRATT, ENT)

### Release Summary
Lays the foundation for the Health Connect Clinical experience. Validates the end-to-end workflow for provider intake, structured summaries, and verification.

### What's Included

- **Organization & Users:** Create and manage clinic organizations, add and verify staff, and assign roles (Admin, Staff, Patient).
- **Forms:** Build and assign intake forms to patients with versioning support.
- **Worklist:** Review and manage patients through a centralized worklist.
- **Summaries:** Generate basic AI-assisted clinical summaries for form submissions with deterministic structure and provenance links.

### What's Not Yet Included

- Decision support & automation (planned for Beta Release – Jan 2026)
- Ingestion of documents and notes directly into patient records (planned for Beta Release – Jan 2026)

### Why It Matters

- Establishes a trusted environment for verified provider-patient interactions.
- Digitizes intake and form management for early specialty workflows (PRATT / ENT).
- Demonstrates foundational usability and reliability for real-world clinic adoption.

### Success Indicators (learning phase)

- Completed forms capture the correct data and appear as expected on summaries.
- Positive qualitative feedback around the patient discovery process.
- Positive qualitative feedback on worklist usage and clarity of summaries.

---

## Personal Product: Beta Release

**Release Date:** January 30, 2026

**Audience:** Internal Thrive users, family and friends, and select pilot patients.

### Release Summary
Expand the Personal experience from internal Thrive users to real patients to validate the full flow of adding documents, completing forms, and generating summaries. Validate that conversation and structured input work seamlessly together, creating a reliable personal health record across diverse data types.

### What's Included

- **Personal Health Record:** Add or update health data through conversation or structured forms; browse a unified repository with improved search and organization.
- **Conversation:** Receive clarifying questions from the assistant to complete missing details.
- **Forms:** Complete intake forms that automatically populate a personal health record.
- **Summaries:** Generate different types of summaries (e.g., visit prep, overview).

### What's Not Yet Included

- Personalized insights or proactive reflection prompts (planned for Release 1.0 – Mar 2026)
- Health data querying (planned for Release 1.0 – Mar 2026)

### Why It Matters

- Validates the end-to-end personal health workflow in real patient contexts.
- Demonstrates that conversation and structured input can coexist naturally.
- Establishes trust and comprehension benchmarks before public launch.

### Success Indicators

- ≥90% of users successfully upload and review their records.
- ≥85% of summaries generated automatically with <10% manual correction.
- Positive qualitative feedback from real patient participants on trust and comprehension.

---

## Clinical Product: Beta Release

**Release Date:** January 30, 2026

**Audience:** Early evaluation of full intake workflow with early adopter providers.

### Release Summary
Extends clinical validation by introducing automation, decision support, and summary enhancements for real patient data and intake workflows.

### What's Included

- **PHR Access:** Ingest documents and notes directly into patient records.
- **Decision Support:** Support configurable decision-support calculations and conditionals for clinical summaries and surfacable in the worklist.
- **Automation:** Automate triggers from form submissions to apply decision support rules.
- **Summaries:** Improved summary authoring experience with ability to generate any time.

### What's Not Yet Included

- Resource authoring and automation (planned for Release 1.0 – Mar 2026)
- Referral / waitlist management (Next - early CfHA partner)

### Why It Matters

- Demonstrates a functional end-to-end intake workflow.
- Reduces manual work through automation and embedded logic.
- Builds confidence in decision-support accuracy and workflow scalability.

### Success Indicators

- 100% of clinicians agree that completed patient intakes and generated summaries meet their clinical review requirements.
- 100% of clinicians report the worklist improves visibility and reduces tracking overhead.
- Positive qualitative feedback received around the form and summary authoring experience.

---

## Personal Product: Release 1.0

**Release Date:** March 31, 2026

**Audience:** Verified external patients managing their health data through the first public Personal release.

### Release Summary
Enable real patients to access and manage their health data through the full Personal experience. This release brings together conversational interaction, comprehensive health records, and an engagement layer that keeps users informed and active in managing their care.

### What's Included

- **Personal Health Record:** Add, edit, and delete health records with provenance and auditing. Query health data conversationally to find information quickly.
- **Conversation:** Receive next-step suggestions and follow-up prompts from the assistant.
- **Notifications:** View an engagement feed showing notifications, recent activity, and summaries.
- **Resources:** Access assigned educational and support resources.

### What's Not Yet Included

- Health data sharing with providers (Next)
- Family profile management (Next)

### Why It Matters

- Expands access to real patients beyond internal testers.
- Provides a single place to view, manage, and act on personal health data.
- Adds ongoing engagement features to encourage return use.

### Success Indicators

- ≥80% of users successfully complete an intake form with minimal support.
- ≥80% of users successfully access or update their records.
- ≥4.5/5 satisfaction rating for usability and comprehension.
- Positive feedback on engagement and health data management experience.

---

## Clinical Product: Release 1.0

**Release Date:** March 31, 2026

**Audience:** Launch intake workflows (PRATT / ENT), early validation of referral & waitlist workflows (CfHA).

### Release Summary
Launch full intake workflows with early adopter clinics and begin early validation of referral and waitlist management capabilities.

### What's Included

- **PHR Access:** Complete access to a patient's PHR within clinical workflows.
- **Decision Support:** Advanced clinical rules, calculations, and alerts surfaced in summaries and worklists to guide triage and prioritization.
- **Resources:** Create and manage educational resources with a built-in authoring tool.
- **Automation:** Automated form timing and resource distribution to reduce manual workload.
- **Referrals:** Initial external referral capabilities to support cross-clinic coordination.

### What's Not Yet Included

- Self-serve authoring tools (Next)
- Patient-facing referral and waitlist visibility (Next)

### Why It Matters

- Establishes a repeatable model with early adopter clinics (PRATT, ENT, CfHA) to validate real-world performance.
- Demonstrates the value of our connected PHR platform in improving efficiency and coordination at the clinic level.
- Expands Thrive's reach by onboarding real patients onto the platform to continue validating our PHR vision.

### Success Indicators

- Intake submissions and summaries processed successfully ≥95% of the time without system issues.
- Positive qualitative feedback (>70% satisfaction) on efficiency and ease of reviewing patient information.
- Clinicians report reduced administrative effort and higher workflow clarity.

---

## PHR Platform Architecture

### Technical Architecture (Alternate View)

**Data Ingestion:**
- Structured Data Ingestion (FHIR, EMR, Provider Data Lakes)
- Unstructured Data Ingestion (PDFs, forms, conversation, wearables)

**Core Storage:**
- **Health Record Store:** Patient/provider attested and editable, audit trail, facts/standards
- **Source Document Repository:** Original documents and content
- **AI Context Store (invisible):** Provenance tracking, complex insights, details, dynamic, growing, powerful

**Intelligence Layer:**
- **Agentic AI "Router":** Routes data between systems
- **LLM - Insight Engine:** Recommendations, patterns, actions

**Presentation Layer:**
- Static facts (edit), dynamic insights, conversational AI, document viewer

---

## Document Control

**Document Date:** November 2025
**Source Document:** PHR to Products Q4 2025.pdf
**Document Owner:** Product Leadership Team

---

**Questions or Feedback?**
Contact: product@thrive.health
