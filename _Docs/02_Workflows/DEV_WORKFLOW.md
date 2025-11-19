# Developer Token Workflow — VehicleOS v4

**For:** Android, Web, Flutter engineers  
**Production Systems:** K&G, IPSY, Spabreaks, Trojan  
**TL;DR:** Tokens automate your design-to-code pipeline. You already use tokens. This makes it faster and scales to any brand.

---

## Why This Matters (The Pitch)

You already use tokens in your projects. **This system makes your life easier:**

✅ **Single source of truth** — Designers push a change once, all brands update automatically  
✅ **No manual mapping** — Figma variable IDs stay consistent; your build just pulls fresh values  
✅ **Brand templating** — New client? Run Style Dictionary, done. No code changes.  
✅ **CICD friendly** — Token updates integrate into your build pipeline automatically  
✅ **You look better** — No more "designer changed a color and forgot to tell dev"  

---

## The Pipeline: What You Get

```
Figma/Token Studio (Designer updates)
         ↓ (exports JSON via Figma Tokens plugin)
Token Files (global.json, brand overrides, themes)
         ↓ (your CI/CD triggers)
Style Dictionary Build
         ↓ (transforms to platform-specific)
CSS Variables / Android XML / Dart Constants
         ↓ (your code consumes)
App UI (automatically in sync)
```

**What changed (Nov 12):** Token names updated for white-label compliance, but the pipeline is identical.

---

## What's Different From Framework Defaults

### Android (Default Material Design)

**Without tokens (what you might have):**
```kotlin
// Hardcoded colors scattered across codebase
Button(
  backgroundColor = Color(0x335fff),  // Some blue
  contentColor = Color(0xFFFFFF)      // White text
)
```

**With our token system:**
```kotlin
// Single source, reusable, theme-aware
Button(
  backgroundColor = colorResource(R.color.surface_primary_enabled),
  contentColor = colorResource(R.color.on_surface_enabled)
)
```

**Advantage:** Change one token, all buttons update. Supports multiple brands without code changes.

---

### Web (CSS Variables)

**Without tokens:**
```css
.button-primary {
  background: #335fff;
  color: #ffffff;
}
.button-primary:hover {
  background: #1243f5;
}
/* Repeat for 20+ component variations */
```

**With tokens:**
```css
.button-primary {
  background: var(--surface-primary-enabled);
  color: var(--on-surface-enabled);
}
.button-primary:hover {
  background: var(--surface-primary-pressed);
}
```

**Advantage:** Theme switching is 1 line of code. Brand swapping is deploying a new CSS file.

---

### Flutter (Dart Constants)

**Without tokens:**
```dart
class AppColors {
  static const primary = Color(0xFF335FFF);
  static const onPrimary = Color(0xFFFFFFFF);
  // Repeat for each color...
}
```

**With tokens:**
```dart
class VosTokens {
  // Auto-generated from tokens
  static const surfacePrimaryEnabled = Color(0xFF335FFF);
  static const onSurfaceEnabled = Color(0xFFFFFFFF);
  // Plus theme-aware variants
}
```

**Advantage:** Regenerate with `style-dictionary build`. Scales to 50+ brands automatically.

---

## The Breaking Change: What You Need to Know

**What changed:** Token name `color-primitives.AppliedBlue` → `color-primitives.BrandPrimary`

**Why:** Remove company-specific branding for white-label system (supports any OEM/brand)

**Your impact:**

| Before | After | Impact |
|--------|-------|--------|
| `color-primitives.AppliedBlue.60` | `color-primitives.BrandPrimary.60` | Token name in JSON exports |
| Generated CSS: `--color-primitives-applied-blue-60` | Generated CSS: `--color-primitives-brand-primary-60` | CSS variable names |
| Generated Android: `color_primitives_applied_blue_60` | Generated Android: `color_primitives_brand_primary_60` | XML resource names |
| Generated Dart: `colorPrimitivesAppliedBlue60` | Generated Dart: `colorPrimitivesAppliedPrimary60` | Dart constant names |

**Migration:** Just re-run `style-dictionary build`. Old references won't work—update imports in your code.

---

## Your Build Process (Step-by-Step)

### Step 1: Designers Push Changes

Designers update tokens in Figma/Token Studio:
```
Figma Tokens Plugin → Export as JSON
```

Token files pushed to repo:
- `global.json` (primitives)
- `_Base/Value.json` (default brand)
- `01_Brand/[ClientName]/Value.json` (client overrides)
- `02_Semantics/Light.json` & `Dark.json` (theme mappings)
- `$metadata.json` (token set order)
- `$themes.json` (Figma variable mappings)

### Step 2: Your Build Pipeline Triggers

```bash
# Pull latest tokens
git pull origin main

# Run Style Dictionary (transforms tokens to platform-specific)
npx style-dictionary build

# Outputs generated in:
# - tokens/web/variables.css (CSS custom properties)
# - tokens/android/colors.xml (Android resources)
# - tokens/flutter/tokens.dart (Dart constants)
# - tokens/web/index.js (JavaScript object)
```

### Step 3: Your Code Consumes Tokens

**Android:**
```kotlin
val backgroundColor = ContextCompat.getColor(
  context, 
  R.color.surface_primary_enabled  // From tokens/android/colors.xml
)
```

**Web:**
```css
.button {
  background-color: var(--surface-primary-enabled);  /* From tokens/web/variables.css */
}
```

**Flutter:**
```dart
Container(
  color: VosTokens.surfacePrimaryEnabled,  // From tokens/flutter/tokens.dart
)
```

### Step 4: Deploy

Your normal deployment process. Tokens are now baked into your binaries/CSS.

---

## Multi-Brand Workflow (The Template Pattern)

This is where tokens save time:

### Current (Without Token Templating)

**New client request:**
1. Designer creates new Figma file
2. Designer manually recreates components for new brand
3. Designer sends specs to dev
4. Dev manually updates colors/fonts/spacing in code
5. QA tests
6. Deploy

**Time:** 2-3 weeks per brand

### With Token System (Production Proven)

**New client request:**
1. Designer creates `01_Brand/[ClientName]/Value.json` (5 min)
2. Designer overrides hero color, fonts, maybe spacing (10 min)
3. Dev runs: `npx style-dictionary build` (30 sec)
4. Deploy new assets
5. QA tests

**Time:** 1 day per brand

**Real example (IPSY):** Added 3 new brands in 1 sprint using this system. Old approach would've taken a full sprint per brand.

---

## Figma Variable Mapping (How It All Connects)

When you see `color-primitives.BrandPrimary.60` in the JSON, here's what happens:

**In Figma:**
```
Figma Tokens Plugin displays:
├─ Token: color-primitives.BrandPrimary.60
└─ Value: #335fff
└─ Figma Variable ID: ad78f5920ed3a0e883abd9b5ac1f34efc795b11f
```

**In $themes.json (token mapping):**
```json
{
  "$figmaVariableReferences": {
    "color-primitives.BrandPrimary.60": "ad78f5920ed3a0e883abd9b5ac1f34efc795b11f"
  }
}
```

**When Style Dictionary builds:**
```
Input: color-primitives.BrandPrimary.60 = #335fff
Output (Android): <color name="color_primitives_brand_primary_60">#335fff</color>
Output (CSS): --color-primitives-brand-primary-60: #335fff;
Output (Dart): static const colorPrimitivesImBrandPrimary60 = Color(0xFF335FFF);
```

**Your code uses:**
```kotlin
colorResource(R.color.color_primitives_brand_primary_60)
```

---

## Token Structure You'll See

### global.json (Primitives & Foundations)

```json
{
  "color-primitives": {
    "BrandPrimary": {
      "60": { "value": "#335fff", "type": "color" },
      "50": { "value": "#6383f8", "type": "color" }
    }
  },
  "spacing": {
    "spacing-8": { "value": 8, "type": "spacing" },
    "spacing-16": { "value": 16, "type": "spacing" }
  },
  "elevation": {
    "elevation-1": { 
      "value": { "x": 0, "y": 2, "blur": 4, "color": "#00000033" },
      "type": "shadow"
    }
  }
}
```

**What you consume:** All of it (these are your raw materials)

### _Base/Value.json (Default Brand Aliases)

```json
{
  "VOS": {
    "color": {
      "brand": {
        "primary": { "value": "{color-primitives.BrandPrimary.60}" }
      },
      "active": {
        "active-light-primary": { 
          "value": "{color-primitives.BrandPrimary.50}" 
        }
      }
    }
  }
}
```

**What this means:** One level of indirection. "primary" aliases to a specific primitive level. Clients override this if they want a different shade.

### 02_Semantics/Light.json (UI Roles)

```json
{
  "surface": {
    "surface-primary-enabled": {
      "value": "{VOS.color.active.active-light-primary}",
      "type": "color"
    }
  }
}
```

**What this means:** "When you see a primary surface in enabled state, use the active-light-primary color from the brand layer."

**Your code:** Uses `surface-primary-enabled` (top-level name), which auto-resolves through the layers.

---

## CICD Integration

### Option 1: Manual Rebuild (Simplest)

```bash
# In your CI/CD pipeline
script:
  - npm install -g style-dictionary
  - npx style-dictionary build
  - git add tokens/
  - git commit -m "Updated tokens from Figma"
```

**When:** Every time tokens JSON is pushed to repo

### Option 2: Automated (Recommended for Prod)

Use a GitHub Action or similar:

```yaml
# .github/workflows/token-build.yml
on:
  push:
    paths:
      - '**.json'  # When token files change
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build tokens
        run: |
          npm install -g style-dictionary
          npx style-dictionary build
      - name: Commit updated tokens
        run: |
          git config user.name "Token Bot"
          git add tokens/
          git commit -m "Auto-generated tokens"
          git push
```

---

## Common Questions

**Q: What if designers change a token mid-sprint?**  
A: Your next build picks up the change. If you're paranoid, pin token versions in your Figma file or use git tags.

**Q: How do I use tokens in my existing codebase?**  
A: Gradually replace hardcoded values. Start with colors, then spacing, then typography. No need to refactor everything at once.

**Q: What about dark mode?**  
A: Same token names, different values. `02_Semantics/Dark.json` provides dark variants. Your theme switcher toggles CSS class or app-level setting.

**Q: Can I override a token locally?**  
A: Not recommended. Defeats the purpose. If you need local overrides, talk to designers about adding a new token instead.

**Q: Figma Tokens plugin vs Token Studio Pro vs alternatives?**  
A: We use Figma Tokens + Token Studio (Pro) because clients use it too. Not perfect, but it works. Main thing: exports valid JSON. That's all you need.

---

## Production Examples (Real Systems)

### K&G (Multi-brand auto retail)

```
Brands: K&G, Vroom, others
Build time: 1 day per new brand
Token update cycle: ~2 weeks
Shared codebase: Yes (one React app, switched by brand)
```

**What works:** Same component codebase, different token sets per brand. Deploy once, serve all brands.

### IPSY (Beauty subscription)

```
Brands: IPSY, IPSY MAN, others
Platforms: Web + iOS
Build time: 1-2 days per brand
Shared tokens: Yes (some overlap, some brand-specific)
```

**What works:** Designers add new brand in 30 min, dev builds in 1 hour, test/deploy 1 day.

### Spabreaks (Travel/wellness)

```
Platforms: Android HMI, Web
Update frequency: Weekly token changes
Brands: Spabreaks, partner brands
```

**What works:** QA triggers rebuild when designers push, automatically deployed to staging for testing.

---

## Next Steps

1. **Read through** the token structure in `global.json` (it's self-documenting)
2. **Set up Style Dictionary** in your repo:
   ```bash
   npm install -g style-dictionary
   npx style-dictionary init
   ```
3. **Review** the generated outputs in `tokens/android/`, `tokens/web/`, `tokens/flutter/`
4. **Audit** your codebase: where are hardcoded values? Replace with token references.
5. **Integrate into CICD:** Add `npx style-dictionary build` to your build pipeline
6. **Sync with design team:** Establish update cadence (weekly? per-sprint?)

---

## Questions? Common Gotchas

**"I see `AppliedBlue` in old code/docs"**  
→ That's the old name. It's now `BrandPrimary`. Update your imports and re-run build.

**"My colors don't match after build"**  
→ Check if you're using the right token name. Color names changed Nov 12. See BREAKING_CHANGES_APPLIED.md.

**"Style Dictionary output looks different than expected"**  
→ Check your `.style-dictionary-config.js`. Make sure transforms match your platform. Default works for most cases.

**"Designer pushed tokens but my code doesn't see them"**  
→ You need to re-run `npx style-dictionary build` and redeploy. It's not automatic; it's part of your build step.

---

**Status:** Production-proven workflow  
**Last Updated:** November 12, 2025  
**Questions?** Reference the token files themselves — they're well-commented.

