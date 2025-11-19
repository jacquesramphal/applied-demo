# VehicleOS Design Token System - Applied Token Audit

A comprehensive design token system with **403+ tokens** organized in a **6-layer architecture**, designed for enterprise-grade applications with Material Design 3 and WCAG 2.1 AA compliance.

## 🎯 Quick Start

### For Different Roles

- **👨‍💻 Developers**: Start with [DEV_WORKFLOW.md](_Docs/02_Workflows/DEV_WORKFLOW.md)
- **🎨 Designers**: Start with [DESIGN_WORKFLOW.md](_Docs/02_Workflows/DESIGN_WORKFLOW.md)
- **🏗️ Tech Leads**: Start with [TECHNICAL_REFERENCE.md](_Docs/04_Technical/TECHNICAL_REFERENCE.md)
- **Everyone else**: Start with [CLIENT_HANDOFF.md](_Docs/CLIENT_HANDOFF.md)

👉 **Main entry point:** [START_HERE](_Docs/00_START_HERE.md)

## 📊 What's Included

| Component | Count | Status |
|-----------|-------|--------|
| Design Tokens | 403+ | ✅ Production Ready |
| Components | 9 | ✅ Complete |
| Themes | 2 (Light/Dark) | ✅ Complete |
| Responsive Modes | 2 (Compact/Spacious) | ✅ Complete |
| Platform Outputs | 2 (Kotlin/XML) | ✅ Ready |

## 📁 Project Structure

```
applied-token-audit/
├── _Docs/                          # 📚 Complete documentation
│   ├── 00_START_HERE.md           # Entry point (read first!)
│   ├── CLIENT_HANDOFF.md          # What changed & why
│   ├── 01_Guides/                 # Guides & references
│   ├── 02_Workflows/              # Designer & Developer guides
│   ├── 03_Implementation/         # Implementation details
│   └── 04_Technical/              # Technical architecture
├── Tokens/                         # 🎨 Design token definitions
│   ├── Current/                   # Previous version (for reference)
│   └── New/                       # Latest token definitions (v1.0)
│       ├── _Base/                 # Layer 1: Primitives
│       ├── 01_Brand/              # Layer 2: Brand colors/values
│       ├── 02_Global.json         # Layer 3: Global design system
│       ├── 03_Semantics/          # Layer 4: Semantic tokens (Light/Dark)
│       ├── 04_Motion/             # Layer 5: Motion/animations
│       ├── 04_Responsive/         # Layer 5: Responsive modes
│       ├── 05_Interactions/       # Layer 5: Interactive states
│       └── 07_Components/         # Layer 6: Component compositions
├── _TransformedTokens/            # 🤖 Generated outputs
│   ├── kotlin/                    # Kotlin (.kt) files
│   └── xml/                       # XML (.xml) files
├── _Scripts/                      # 🔧 Transformation scripts
│   └── token_transformer_full_coverage.py  # Token transformer
└── requirements.txt               # Python dependencies
```

## 🏗️ 6-Layer Architecture

The token system is organized in 6 layers for scalability and maintainability:

1. **Layer 1 - Primitives**: Base color values (HEX codes)
2. **Layer 2 - Brand**: Brand-specific values (AppliedBlue, etc.)
3. **Layer 3 - Global**: Design system tokens (colors, spacing, typography)
4. **Layer 4 - Semantics**: Theme-aware tokens (Light/Dark modes)
5. **Layer 5 - Responsive**: Density modes (Compact/Spacious)
6. **Layer 6 - Components**: Component-specific compositions

## 🚀 Key Features

- ✅ **Material Design 3 Compliant** — Industry-standard design system
- ✅ **WCAG 2.1 AA Compliant** — Accessibility standards met
- ✅ **Multi-Platform Support** — Kotlin & XML transformations
- ✅ **Theme Support** — Light & Dark modes
- ✅ **Responsive Design** — Compact & Spacious modes
- ✅ **Enterprise Ready** — 403+ tokens, fully documented
- ✅ **Component Library** — 9 pre-built components

## ⚠️ Breaking Changes (v1.0)

### `AppliedBlue` → `BrandPrimary`

For white-label compliance, the main brand color token has been renamed:

- **Old**: `AppliedBlue` (for branding)
- **New**: `BrandPrimary` (generic, supports rebranding)
- **Migration**: Find & replace (< 5 minutes)
- **Visual Impact**: None (same color values)

For detailed migration steps, see [CLIENT_HANDOFF.md](_Docs/CLIENT_HANDOFF.md).

## 🔧 Development

### Prerequisites

- Python 3.8+
- No external dependencies required (uses standard library)

### Running the Token Transformer

```bash
python3 _Scripts/token_transformer_full_coverage.py /path/to/applied-token-audit
```

This generates:
- Kotlin files in `_TransformedTokens/kotlin/`
- XML files in `_TransformedTokens/xml/`

## 📚 Documentation Map

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [00_START_HERE.md](_Docs/00_START_HERE.md) | Choose your path | 2 min |
| [CLIENT_HANDOFF.md](_Docs/CLIENT_HANDOFF.md) | What changed & why | 15 min |
| [DESIGN_WORKFLOW.md](_Docs/02_Workflows/DESIGN_WORKFLOW.md) | Figma integration | 30 min |
| [DEV_WORKFLOW.md](_Docs/02_Workflows/DEV_WORKFLOW.md) | Code integration | 30 min |
| [QUICK_REFERENCE.md](_Docs/01_Guides/QUICK_REFERENCE.md) | FAQ & lookup | 5 min |
| [TECHNICAL_REFERENCE.md](_Docs/04_Technical/TECHNICAL_REFERENCE.md) | Architecture | 45 min |

## 📖 Core Components

The token system includes these pre-built components:

1. **Button** — Multiple variants & states
2. **Input** — Text fields with validation states
3. **Card** — Container component
4. **Checkbox** — Form control
5. **Radio** — Form control
6. **Toggle** — Switch component
7. **Select** — Dropdown component
8. **Modal** — Dialog component
9. **Notification** — Toast/alert component

## 🎨 Theme Support

### Light Mode
- Primary colors optimized for light backgrounds
- High contrast ratios for readability
- WCAG AA compliant

### Dark Mode
- Primary colors optimized for dark backgrounds
- Reduced eye strain
- WCAG AA compliant

## 📊 Token Statistics

- **Total Tokens**: 403+
- **Color Tokens**: ~80
- **Spacing Tokens**: ~40
- **Typography Tokens**: ~50
- **Component Tokens**: ~150+
- **Motion Tokens**: ~30
- **Other Tokens**: ~50+

## 🔗 Integration Options

### Web/Frontend
- Figma design tokens
- CSS variables
- Tailwind configuration

### Mobile (Android)
- Kotlin data classes (`_TransformedTokens/kotlin/`)
- XML resources (`_TransformedTokens/xml/`)

## ❓ FAQ

**Q: What changed from the previous version?**  
A: See [CLIENT_HANDOFF.md](_Docs/CLIENT_HANDOFF.md) for a complete summary.

**Q: How do I implement this in my project?**  
A: Choose your role and follow the workflow guides in `_Docs/02_Workflows/`.

**Q: Are there compatibility issues with existing tokens?**  
A: One breaking change: `AppliedBlue` → `BrandPrimary`. Migration takes < 5 minutes.

**Q: Can I customize the tokens?**  
A: Yes! The token files are in `Tokens/New/` and can be modified. Follow the 6-layer architecture.

## 📞 Support

For detailed information:
1. Check [QUICK_REFERENCE.md](_Docs/01_Guides/QUICK_REFERENCE.md) for common questions
2. Review [DOCUMENTATION_MAP.md](_Docs/01_Guides/DOCUMENTATION_MAP.md) for all docs
3. Read the technical guide: [TECHNICAL_REFERENCE.md](_Docs/04_Technical/TECHNICAL_REFERENCE.md)

## 📄 License

This design token system is part of the VehicleOS design framework.

---

**Ready to get started?** → [START_HERE](_Docs/00_START_HERE.md)

