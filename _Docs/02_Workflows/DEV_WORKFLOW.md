# Developer Token Workflow — VehicleOS v4

**For:** Android, Web, Flutter engineers  
**Production Systems:** K&G, IPSY, Spabreaks, Trojan  
**TL;DR:** Tokens automate your design-to-code pipeline. You already use tokens. This makes it faster and scales to any brand.

---

## Why This Matters (The Pitch)

You already use tokens in your projects. **This system makes your life easier:**

✅ **Single source of truth** — Designers push a change once, all brands update automatically  
✅ **No manual mapping** — Figma variable IDs stay consistent; your build just pulls fresh values  
✅ **Brand templating** — New client? Run token transformer, done. No code changes.  
✅ **CICD friendly** — Token updates integrate into your build pipeline automatically  
✅ **One-command swapping** — Switch between 6 brand/theme combinations with `./swap-tokens.sh`  
✅ **You look better** — No more "designer changed a color and forgot to tell dev"  

---

## The Pipeline: What You Get

```
Figma/Token Studio (Designer updates)
         ↓ (exports JSON via Figma Tokens plugin)
Token Files (_Base/Value.json, 01_Brand/*.json, 03_Themes/*.json)
         ↓ (your CI/CD triggers or manual run)
token_transformer_full_coverage.py
         ↓ (transforms to platform-specific for all 6 brand/theme combos)
_TransformedTokens/
  ├─ xml/{brand}_{theme}/     (Android XML resources)
  ├─ kotlin/{brand}_{theme}/   (Kotlin constants)
  └─ css/{brand}_{theme}/      (CSS variables)
         ↓ (swap-tokens.sh syncs to app or your code consumes)
App UI (automatically in sync)
```

**Current setup:** 3 brands (Default, Performance, Luxury) × 2 themes (Day, Night) = 6 combinations, all generated automatically.

---

## 🤖 AI-Assisted Development with Figma MCP

**Want to use Cursor AI to generate code from your Figma designs?** Use the Figma MCP Server to automatically extract design tokens and generate code that adheres to your design system.

👉 **[See the complete Figma MCP Workflow Guide →](FIGMA_MCP_WORKFLOW.md)**

The **VehicleOSDemo** app was built using this workflow — see it as a real example of AI-assisted development with design tokens.

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

**Advantage:** Regenerate with `token_transformer_full_coverage.py`. Scales to any number of brands automatically.

---

## The Breaking Change: What You Need to Know

**Current token structure:** The system uses a 6-layer architecture with brand and theme separation.

**Token file structure:**
- `_Base/Value.json` — Base primitives and defaults
- `01_Brand/Default.json`, `Performance.json`, `Luxury.json` — Brand-specific overrides
- `03_Themes/Day.json`, `Night.json` — Theme-specific mappings
- `04_Motion/Animations.json` — Motion tokens
- `05_Interactions/States.json` — Interaction state tokens
- `07_Components/Compositions.json` — Component composition tokens

**Generated outputs:** All 6 brand/theme combinations are generated automatically:
- `default_day`, `default_night`
- `performance_day`, `performance_night`
- `luxury_day`, `luxury_night`

**Migration:** If you're migrating from an old system, run the transformer and update your imports to use the new resource names.

---

## Your Build Process (Step-by-Step)

### Step 1: Designers Push Changes

Designers update tokens in Figma/Token Studio and push to GitHub:
```
Figma Tokens Plugin → Push to GitHub
```

Token files pushed to repo:
- `_Base/Value.json` (base primitives and defaults)
- `01_Brand/Default.json`, `Performance.json`, `Luxury.json` (brand overrides)
- `03_Themes/Day.json`, `Night.json` (theme mappings)
- `04_Motion/Animations.json` (motion tokens)
- `05_Interactions/States.json` (interaction states)
- `07_Components/Compositions.json` (component tokens)
- `$themes.json` (auto-generated, includes Figma variable mappings)

### Step 2: Generate Platform-Specific Tokens

```bash
# Pull latest tokens
git pull origin main

# Run token transformer (generates all 6 brand/theme combinations)
python3 _Scripts/token_transformer_full_coverage.py . --modes

# Outputs generated in:
# - _TransformedTokens/xml/{brand}_{theme}/ (Android XML resources)
#   ├─ colors.xml, dimens.xml, strings.xml, typography.xml, etc.
# - _TransformedTokens/kotlin/{brand}_{theme}/ (Kotlin constants)
#   └─ Tokens.kt
# - _TransformedTokens/css/{brand}_{theme}/ (CSS variables)
#   └─ variables.css
```

**Note:** The `--modes` flag generates all 6 brand/theme combinations automatically. Each combination gets its own directory.

### Step 3: Swap Tokens in Demo App (or Integrate into Your App)

**For the VehicleOSDemo app:**
```bash
cd VehicleOSDemo
./swap-tokens.sh luxury_night
```

This single command:
1. Regenerates all tokens (if needed)
2. Updates `gradle.properties` with the selected brand/theme
3. Syncs XML files from `_TransformedTokens/xml/luxury_night/` to `app/src/main/res/values/`
4. Ready to build and run!

**For your own app:**
- Copy XML files from `_TransformedTokens/xml/{brand}_{theme}/` to your Android app's `res/values/`
- Import Kotlin files from `_TransformedTokens/kotlin/{brand}_{theme}/` into your Kotlin project
- Include CSS files from `_TransformedTokens/css/{brand}_{theme}/` in your web project

**Android:**
```kotlin
val backgroundColor = ContextCompat.getColor(
  context, 
  R.color.color_brand_primary_primary  // From _TransformedTokens/xml/{brand}_{theme}/colors.xml
)
```

**Web:**
```css
.button {
  background-color: var(--color-brand-primary-primary);  /* From _TransformedTokens/css/{brand}_{theme}/variables.css */
}
```

**Kotlin (Compose):**
```kotlin
import com.example.tokens.Tokens  // From _TransformedTokens/kotlin/{brand}_{theme}/Tokens.kt

Button(
  colors = ButtonDefaults.buttonColors(
    backgroundColor = Tokens.colorBrandPrimaryPrimary
  )
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
1. Designer creates `01_Brand/[ClientName].json` (5 min)
2. Designer overrides hero color, fonts, maybe spacing (10 min)
3. Designer pushes to GitHub
4. Dev runs: `python3 _Scripts/token_transformer_full_coverage.py . --modes` (30 sec)
5. This automatically generates `{clientname}_day` and `{clientname}_night` outputs
6. Dev tests with: `cd VehicleOSDemo && ./swap-tokens.sh {clientname}_day`
7. Deploy new assets
8. QA tests

**Time:** 1 day per brand

**Real example:** The system currently supports 3 brands (Default, Performance, Luxury) × 2 themes = 6 combinations, all generated automatically from the same token files.

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

**When token_transformer_full_coverage.py runs:**
```
Input: color.brandPrimary.primary = #335fff (from 01_Brand/Default.json)
       + Theme mappings from 03_Themes/Day.json
Output (Android XML): <color name="color_brand_primary_primary">#335fff</color>
Output (CSS): --color-brand-primary-primary: #335fff;
Output (Kotlin): val colorBrandPrimaryPrimary = Color(0xFF335FFF)
```

**Your code uses:**
```kotlin
colorResource(R.color.color_brand_primary_primary)
```

**Note:** The transformer resolves all token references through the 6-layer architecture, ensuring brand and theme values are correctly applied.

---

## Token Structure You'll See

### _Base/Value.json (Primitives & Foundations)

```json
{
  "color": {
    "active": {
      "active-light-primary": { "value": "#6383f8", "type": "color" },
      "active-dark-primary": { "value": "#4d3a5e", "type": "color" }
    },
    "whites": { /* white color scale */ },
    "blacks": { /* black color scale */ }
  },
  "Spacing": {
    "spacing-4": { "value": 4, "type": "spacing" },
    "spacing-8": { "value": 8, "type": "spacing" },
    "spacing-16": { "value": 16, "type": "spacing" }
  },
  "Typography": {
    "fontSize": { /* font size scale */ },
    "lineHeight": { /* line height scale */ },
    "fontWeight": { /* font weights */ }
  }
}
```

**What you consume:** Base primitives that all brands inherit from.

### 01_Brand/Default.json, Performance.json, Luxury.json (Brand Overrides)

```json
{
  "color": {
    "brandPrimary": {
      "primary": { "value": "#335fff", "type": "color" },
      "secondary": { "value": "#6383f8", "type": "color" }
    }
  },
  "Typography": {
    "fontFamily": {
      "primary": { "value": "sans-serif", "type": "fontFamily" }
    }
  },
  "Spacing": {
    // Only override spacing values that differ from base
  }
}
```

**What this means:** Each brand file only contains what's different. Default uses blue, Performance uses orange, Luxury uses purple and serif fonts.

### 03_Themes/Day.json & Night.json (Theme Mappings)

```json
{
  "color": {
    "surface": {
      "primary": { "value": "{color.active.active-light-primary}", "type": "color" },
      "secondary": { "value": "{color.whites.white-100-primary}", "type": "color" }
    },
    "text": {
      "primary": { "value": "{color.blacks.black-90-default}", "type": "color" }
    }
  }
}
```

**What this means:** Day themes map to light-optimized colors, Night themes map to dark-optimized colors. The theme files ensure proper day/night color usage.

**Your code:** Uses tokens like `color_brand_primary_primary` and `color_surface_primary`, which resolve through brand → theme layers automatically.

---

## CICD Integration

### Option 1: Manual Rebuild (Simplest)

```bash
# In your CI/CD pipeline or local development
script:
  - python3 _Scripts/token_transformer_full_coverage.py . --modes
  - git add _TransformedTokens/
  - git commit -m "Updated tokens from Figma"
```

**When:** Every time token JSON files are pushed to repo

**Note:** The `--modes` flag generates all 6 brand/theme combinations automatically.

### Option 2: Automated (Recommended for Prod)

Use a GitHub Action or similar:

```yaml
# .github/workflows/token-build.yml
on:
  push:
    paths:
      - 'Tokens/**/*.json'  # When token files change
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Build tokens
        run: |
          python3 _Scripts/token_transformer_full_coverage.py . --modes
      - name: Commit updated tokens
        run: |
          git config user.name "Token Bot"
          git config user.email "token-bot@example.com"
          git add _TransformedTokens/
          git commit -m "Auto-generated tokens for all brand/theme combinations" || exit 0
          git push || exit 0
```

**Note:** The transformer generates outputs for all 6 combinations, so your CI/CD can build/test all variants automatically.

---

## Common Questions

**Q: What if designers change a token mid-sprint?**  
A: Your next build picks up the change. Run `python3 _Scripts/token_transformer_full_coverage.py . --modes` to regenerate all outputs. If you're paranoid, pin token versions in your Figma file or use git tags.

**Q: How do I use tokens in my existing codebase?**  
A: Gradually replace hardcoded values. Start with colors, then spacing, then typography. No need to refactor everything at once. Use `swap-tokens.sh` in the demo app to test different combinations.

**Q: What about day/night themes?**  
A: Same token names, different values. `03_Themes/Day.json` and `Night.json` provide theme-specific mappings. The transformer generates separate outputs for each theme. Use `./swap-tokens.sh {brand}_day` or `./swap-tokens.sh {brand}_night` to test.

**Q: Can I override a token locally?**  
A: Not recommended. Defeats the purpose. If you need local overrides, talk to designers about adding a new token instead. The system is designed so brand files only override what's different.

**Q: How do I test different brand/theme combinations?**  
A: Use `./swap-tokens.sh {brand}_{theme}` in the VehicleOSDemo app. Available combinations: `default_day`, `default_night`, `performance_day`, `performance_night`, `luxury_day`, `luxury_night`.

**Q: What's the difference between the token files and the generated outputs?**  
A: Token files (in `Tokens/`) are the source of truth. Generated outputs (in `_TransformedTokens/`) are platform-specific files (XML, Kotlin, CSS) that your code consumes. Always regenerate after token changes.

---

## Next Steps

1. **Read through** the token structure in `Tokens/_Base/Value.json` and brand files (they're self-documenting)
2. **Set up the token transformer** in your repo:
   ```bash
   pip install -r requirements.txt
   python3 _Scripts/token_transformer_full_coverage.py . --modes
   ```
3. **Review** the generated outputs in `_TransformedTokens/xml/`, `_TransformedTokens/kotlin/`, `_TransformedTokens/css/`
4. **Test token swapping** in the demo app:
   ```bash
   cd VehicleOSDemo
   ./swap-tokens.sh luxury_night
   ```
5. **Audit** your codebase: where are hardcoded values? Replace with token references.
6. **Integrate into CICD:** Add `python3 _Scripts/token_transformer_full_coverage.py . --modes` to your build pipeline
7. **Sync with design team:** Establish update cadence (weekly? per-sprint?)

---

## Questions? Common Gotchas

**"My colors don't match after build"**  
→ Make sure you're using the correct brand/theme combination. Run `./swap-tokens.sh {brand}_{theme}` to ensure the right tokens are synced. Also verify that day themes use day colors and night themes use night colors.

**"Token transformer output looks different than expected"**  
→ Check that all token files are present and valid JSON. The transformer resolves references through the 6-layer architecture. Make sure brand and theme files are correctly structured.

**"Designer pushed tokens but my code doesn't see them"**  
→ You need to re-run `python3 _Scripts/token_transformer_full_coverage.py . --modes` and then sync to your app (or run `./swap-tokens.sh` in the demo). It's not automatic; it's part of your build step.

**"How do I switch between brands in my app?"**  
→ Use `./swap-tokens.sh {brand}_{theme}` in the demo app. For your own app, copy the XML/Kotlin/CSS files from `_TransformedTokens/{platform}/{brand}_{theme}/` to your project.

**"I see errors about missing resources"**  
→ Make sure you've run the token transformer and synced the correct brand/theme combination. Some tokens are brand-specific (e.g., `color_brand_primary_primary`), so ensure you're using the right combination.

---

**Status:** Production-proven workflow  
**Last Updated:** November 12, 2025  
**Questions?** Reference the token files themselves — they're well-commented.

