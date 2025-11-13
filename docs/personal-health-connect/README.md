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

🟡 **Planning Phase**

The product vision (PRD) is complete. The implementation plan is defined. Development has not yet started.

See [Implementation Plan](./IMPLEMENTATION_PLAN.md) for phased rollout strategy.

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

## Next Steps

1. **Review** PRD and Implementation Plan
2. **Validate** approach with team
3. **Create tickets** for Phase 1 (Release 0)
4. **Begin development** of `sandwich/personal/` app
5. **Iterate** based on feedback

## Questions?

For questions about:
- **Product vision/features**: See [PRD.md](./PRD.md)
- **Technical implementation**: See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
- **Existing architecture**: See [/CLAUDE.md](../../CLAUDE.md)

---

**Last Updated**: November 2025
