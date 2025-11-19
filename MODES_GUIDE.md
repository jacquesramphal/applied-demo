# 🎨 Figma Modes Guide - VehicleOS Design System

## Overview

The design token system now supports **Figma Modes** for easy management of brands, themes, and spacing variants. Instead of selecting from 12 separate themes, designers can toggle 3 independent mode groups.

## Available Modes

### 1. Brand Mode
Select which brand to use:
- **Default** — Apply Default Brand colors & typography
- **Brand2** — Apply Brand2 colors & typography

### 2. Theme Mode
Select light or dark color theme:
- **Light** — Light mode colors
- **Dark** — Dark mode colors

### 3. Spacing Mode
Select density/spacing:
- **Default** — Base spacing (spacing-8 = 8px)
- **Compact** — Dense spacing (spacing-8 = 7px)
- **Spacious** — Generous spacing (spacing-8 = 9px)

## How It Works

### In Figma (Plugin Interface)

1. Open **Figma Tokens** plugin
2. Select **00_master_modes** theme from dropdown
3. You'll see 3 mode groups at the top:
   - **Brand:** [Default] [Brand2]
   - **Theme:** [Light] [Dark]
   - **Spacing:** [Default] [Compact] [Spacious]
4. Click to toggle each mode
5. All tokens update automatically for selected combination

### Mode Combinations (12 Total)

```
Brand          × Theme        × Spacing      = Total
(2 options)    (2 options)    (3 options)   = 12 combinations
```

**Examples:**
- Default Brand + Light + Default Spacing
- Default Brand + Dark + Compact Spacing
- Brand2 + Dark + Spacious Spacing
- Brand2 + Light + Compact Spacing
- etc. (12 total)

## Token Resolution

When you select modes, tokens resolve as follows:

```
spacing-8 token:
1. Base: 8px (from 02_Layout.json)
2. Mode: [Brand selected] → color/typography
3. Mode: [Theme selected] → color overrides
4. Mode: [Spacing selected] → spacing overrides
   - Default: Keep 8px
   - Compact: Override to 7px
   - Spacious: Override to 9px
```

**Result:** spacing-8 resolves to either 7px, 8px, or 9px based on Spacing mode.

## Usage Examples

### Example 1: Compact Dark Mode for Brand2
```
Brand:   Brand2 ✓
Theme:   Dark ✓
Spacing: Compact ✓

Resolution:
→ Button uses Brand2 colors
→ Dark theme applied
→ Spacing-8 = 7px (dense layout)
```

### Example 2: Default Light Mode
```
Brand:   Default ✓
Theme:   Light ✓
Spacing: Default ✓

Resolution:
→ Button uses Default Brand colors
→ Light theme applied
→ Spacing-8 = 8px (standard layout)
```

### Example 3: Spacious Light Mode for Brand2
```
Brand:   Brand2 ✓
Theme:   Light ✓
Spacing: Spacious ✓

Resolution:
→ Button uses Brand2 colors
→ Light theme applied
→ Spacing-8 = 9px (generous layout)
```

## Scaling: Adding a New Brand

Want to add Brand3?

### Steps:
1. Create `01_Brand/Brand3.json` with brand colors/typography
2. Update `$modes.json`:
   - Add "Brand3" to Brand mode values
   - Add 6 new modeMapping entries for Brand3 combinations
3. Add 6 new theme entries to `$themes.json` (Compact/Spacious for Light/Dark)
4. Sync to Figma

That's it! All 18 combinations now work automatically.

## Reference: Mode Mapping

| Brand | Theme | Spacing | Color | Spacing Value |
|-------|-------|---------|-------|---------------|
| Default | Light | Default | Default colors | 8px |
| Default | Light | Compact | Default colors | 7px |
| Default | Light | Spacious | Default colors | 9px |
| Default | Dark | Default | Dark colors | 8px |
| Default | Dark | Compact | Dark colors | 7px |
| Default | Dark | Spacious | Dark colors | 9px |
| Brand2 | Light | Default | Brand2 colors | 8px |
| Brand2 | Light | Compact | Brand2 colors | 7px |
| Brand2 | Light | Spacious | Brand2 colors | 9px |
| Brand2 | Dark | Default | Brand2 Dark colors | 8px |
| Brand2 | Dark | Compact | Brand2 Dark colors | 7px |
| Brand2 | Dark | Spacious | Brand2 Dark colors | 9px |

## Technical Details

### JSON Structure

**$modes.json** defines the mode structure and mapping:
```json
{
  "modes": {
    "Brand": { "values": ["Default", "Brand2"] },
    "Theme": { "values": ["Light", "Dark"] },
    "Spacing": { "values": ["Default", "Compact", "Spacious"] }
  },
  "modeMapping": {
    "Default/Light/Default": { "brand": "01_Brand/Default", ... }
  }
}
```

**$themes.json** contains the master modes theme:
```json
{
  "id": "00_master-modes",
  "modes": {
    "Brand": ["Default", "Brand2"],
    "Theme": ["Light", "Dark"],
    "Spacing": ["Default", "Compact", "Spacious"]
  },
  "modeValues": { /* 12 combinations */ }
}
```

### File Organization

Token files remain organized by purpose:
- `01_Brand/` — Brand-specific colors, typography
- `02_Layout.json` — Base spacing/radius
- `03_Themes/` — Color theme overrides
- `04_Responsive/` — Spacing overrides (Compact/Spacious)
- `05_Interactions/` — Interactive states
- `07_Components/` — Component compositions

## FAQ

**Q: Can I still use the 12 individual themes?**  
A: Yes! They're still available. The master modes theme is optional.

**Q: What happens if I add a new spacing mode?**  
A: You'd need to create new Spacing values and update all 12 (or more) mode combinations. Master modes handle this automatically.

**Q: Can I have more than 3 mode groups?**  
A: Yes! Add more groups to `$modes.json` (e.g., Density, Contrast, etc.).

**Q: How do I export tokens in a specific mode combination?**  
A: Use Figma Tokens plugin's export feature after selecting your modes.

## Support

For questions about modes:
1. Check this guide
2. Review `$modes.json` for current mapping
3. See `$themes.json` for theme definitions
4. Check `TECHNICAL_REFERENCE.md` for architecture details

