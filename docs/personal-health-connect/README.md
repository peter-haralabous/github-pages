# Personal Health Connect Documentation

This directory contains documentation for the **Personal Health Connect** features - a patient-facing personal health record (PHR) system being built within the thrive-prototypes platform.

## Documentation Index

### 📄 [Product Requirements Document (PRD)](./PRD.md)
**Complete product vision, features, and user experience design.**

This document defines:
- Product vision and philosophy
- Three core principles (Primacy of Individual, One Truth, Person Owns Data)
- Feature requirements organized by release (0, 0.5, 1.0, 2.0)
- UX patterns and design system
- Technical requirements
- Success metrics

**Audience**: Product managers, designers, stakeholders

### 🛠️ [Implementation Plan](./IMPLEMENTATION_PLAN.md)
**Technical strategy for rebuilding features in Django + HTMX.**

This document outlines:
- Architecture strategy (Django app structure, model reuse)
- HTMX interaction patterns
- Integration with existing codebase
- Implementation phases aligned with PRD releases
- Testing strategy
- Security and privacy considerations

**Audience**: Developers, technical leads

### 📊 [Feature Gap Analysis](./FEATURE_GAP_ANALYSIS.md)
**Detailed comparison of React prototype vs Django implementation.**

This document analyzes:
- Side-by-side feature comparison (90+ features)
- Missing features prioritized by importance
- Data model gaps
- Quick wins that can be implemented immediately
- Technical debt to address
- Estimated implementation time (6-9 weeks)

**Audience**: Product managers, technical leads

### 🗺️ [Releases 0 to 2.0 Roadmap](./RELEASES_0_TO_2_ROADMAP.md)
**Comprehensive 10-week implementation roadmap for all PRD releases.**

This document provides:
- Detailed task breakdowns for each release
- Code examples and HTMX patterns
- Model structures and service designs
- Week-by-week implementation sequence
- Testing strategy and success metrics
- Risk mitigation plan

**Audience**: Development team, project managers

## Quick Overview

### What is Personal Health Connect?

A conversational personal health record platform that allows patients to:
- **Add health data naturally** through chat with an AI assistant
- **Upload documents** (PDFs, images) with automatic data extraction
- **View organized records** across categories (medications, conditions, allergies, etc.)
- **Receive intelligent summaries** that connect information and reveal insights
- **See a living feed** of updates with source attribution and suggested actions

### Key Differentiators

Unlike traditional health portals, Personal Health Connect:
- Uses **conversation over forms** for data entry
- Focuses on **reflection over compliance**
- Provides **transparency over opacity** (all insights link to source data)
- Emphasizes **calm over complexity** in design

### Technology Stack

**Original Prototype**: React + TypeScript + Vite + Claude AI
**Rebuild Target**: Django + HTMX + Tailwind + Claude AI

The features are being rebuilt to match the existing thrive-prototypes tech stack for better integration and maintainability.

## Implementation Status

🟢 **Ready to Build**

- ✅ Product vision (PRD) complete
- ✅ Feature gap analysis complete
- ✅ Detailed roadmap (Releases 0-2.0) complete
- ✅ Django infrastructure ready (models, LLM, HTMX, SSE)
- 🔨 Development starting

**Current Phase**: Week 1 of Release 0 (Alpha)

See [Releases 0 to 2.0 Roadmap](./RELEASES_0_TO_2_ROADMAP.md) for detailed implementation plan.

## Core Principles

From the PRD:

1. **Primacy of the Individual**
   - The person is the center of design, not clinical workflows
   - Prioritize comprehension, engagement, empowerment

2. **One Person, One Truth**
   - Single, unified health record per individual
   - Every interaction contributes to and draws from this record

3. **The Person Owns Their Data**
   - Fundamental right to all personal data
   - Thrive is a steward, not an owner
   - Shapes all sharing, privacy, and access decisions

## Feature Releases

### Release 0 (Alpha) - Foundation
- Health summary panel
- Core health record types (meds, conditions, allergies, etc.)
- Basic chat interface
- Health records repository
- PDF document upload

### Release 0.5 (Beta) - Engagement Loop
- Dynamic feed panel
- Summary cards with source attribution
- Inline suggestions
- Streamlined responses

### Release 1.0 - Intelligence
- Notifications system
- Record notes & context
- Improved formatting

### Release 2.0 - Advanced Features
- In-chat action buttons
- Enhanced document processing
- Record deduplication
- Contextual follow-ups
- Smart contextual summaries

## Quick Start for Developers

### Prerequisites
1. Django development environment running (`make dev`)
2. Feature flag enabled: `FEATURE_PATIENT_CHATTY_APP=True` in `.env`
3. Access to Anthropic Claude API key

### Week 1 Tasks (Release 0)
1. Create missing HealthRecord models (Medication, Allergy, Procedure, LabResult, VitalSign, HospitalVisit)
2. Enhance left panel with categorized records view
3. Build HealthSummary model and generation service
4. Implement right panel health summary display

See [Releases 0 to 2.0 Roadmap](./RELEASES_0_TO_2_ROADMAP.md#week-1-2-release-0-foundation) for detailed tasks.

## Next Steps

1. ✅ **Review** documentation (PRD, Gap Analysis, Roadmap)
2. **Prioritize** features if timeline needs adjustment
3. **Create tickets** in GitHub project board
4. **Begin Week 1** implementation
5. **Schedule** user testing after Release 0

## Questions?

For questions about:
- **Product vision/features**: See [PRD.md](./PRD.md)
- **Technical implementation**: See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
- **Existing architecture**: See [/CLAUDE.md](../../CLAUDE.md)

---

**Last Updated**: November 2025
