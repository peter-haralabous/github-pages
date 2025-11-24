# Features

This folder contains feature-specific documentation. Each feature has its own subfolder with discovery, definition, development, and delivery documentation.

## 📁 Current Features

```
features/
├── README.md                          # This file
├── template-feature/                  # Template for new features
│   ├── discovery.md                   # Discovery phase template
│   ├── prd.md                         # PRD template
│   ├── release-notes.md               # Release notes template
│   └── user-feedback.md               # User feedback template
└── personal-health-records/           # Personal health records feature (planned)
```

## 🎯 Feature Template

The `template-feature/` folder contains templates for documenting features through their lifecycle:

1. **discovery.md** - Problem validation and opportunity sizing
2. **prd.md** - Product Requirements Document
3. **user-feedback.md** - User testing and feedback
4. **release-notes.md** - Release communication

## 🚀 Starting a New Feature

### 1. Copy the Template

```bash
cp -r docs/product/features/template-feature docs/product/features/[your-feature-name]
```

Use descriptive names like:
- `ai-health-summaries`
- `document-auto-extraction`
- `care-coordination-hub`

### 2. Work Through Documents

Follow this workflow:

```
Discovery → PRD → User Feedback → Release Notes
```

### 3. Update as You Go

Keep documentation current throughout the feature lifecycle.

## 📋 Document Workflow

### Discovery Phase
- **File**: `discovery.md`
- **Purpose**: Validate problem and size opportunity
- **Output**: Go/no-go decision

### Define Phase
- **File**: `prd.md`
- **Purpose**: Define solution and requirements
- **Output**: Feature specification and success criteria

### Develop Phase
- **File**: `user-feedback.md`
- **Purpose**: Test with users, iterate on design
- **Output**: Validated design and insights

### Deliver Phase
- **File**: `release-notes.md`
- **Purpose**: Communicate feature to users
- **Output**: User-facing documentation

## 🔍 Current Features

### template-feature/
Template files for documenting new features. Contains:
- Discovery template
- PRD template
- User feedback template
- Release notes template

**Use this**: Copy this folder when starting a new feature

### personal-health-records/
Planned feature folder (currently empty)

**Status**: Planning phase

## 💡 Best Practices

1. **Start with discovery** - Validate the problem before defining solutions
2. **Keep it updated** - Update docs as you learn and iterate
3. **Link to research** - Connect to user studies and personas
4. **Show evidence** - Include data and user quotes
5. **Be concise** - Focus on decisions and rationale

## 📊 Feature Lifecycle

Each feature progresses through phases with clear gates:

```
Discovery          Define            Develop           Deliver
    ↓                 ↓                  ↓                 ↓
Problem          Solution         Prototype         Release
Validated        Defined           Tested           Shipped
    ↓                 ↓                  ↓                 ↓
[discovery.md]   [prd.md]     [user-feedback.md]  [release-notes.md]
```

## 🔗 Related Resources

- [Product Strategy](../strategy/product-strategy.md) - Overall product direction
- [User Personas](../strategy/) - Who we're building for
- [Research Studies](../research/user-studies/) - User insights

---

**Questions?** See the template files for detailed guidance on each phase.
