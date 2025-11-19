# Designer Token Workflow — VehicleOS v4

**For:** Product & system designers using Figma + Token Studio  
**Production Systems:** K&G, IPSY, Spabreaks, Trojan  
**TL;DR:** Token Studio is your design-to-code bridge. Update once in Figma, developers pull changes automatically.

---

## Why Tokens (The Pitch)

**You already use Figma tokens.** This system makes them work harder:

✅ **One source of truth** — Changes in Figma auto-flow to dev without manual specs  
✅ **Brand templating** — New brand? Copy-paste token file, override 5 colors, done  
✅ **Light/Dark themes** — Same components, flip a switch, both modes work  
✅ **Cross-platform** — One Figma file powers Android, Web, Flutter  
✅ **No "version hell"** — Designers + devs always in sync  

### The Problem We Solve

**Before tokens:** Colors scattered across code, design specs in docs, designers sending screenshots, devs guessing values
- Takes 2-3 weeks per brand
- "Did you update this color?" becomes a constant question
- Hard to maintain light/dark parity

**With our system:** One JSON file, changes cascade to all platforms, no manual work
- 1 day per new brand (proven on IPSY, K&G)
- Designers + devs always in sync
- Light/Dark consistency automatic  

---

## The Pipeline: What Happens When You Save

```
You update color in Figma
         ↓
Token Studio plugin captures change
         ↓
You export JSON
         ↓
Dev team pulls updated token files
         ↓
Their build system regenerates code
         ↓
All platforms (Android, Web, Flutter) update
```

**No hand-off meetings needed.** No "did you update the design spec?" No manual color specs.

---

## Understanding Figma Terminology (Quick Reference)

**Common confusion in Figma:**

| Term | What It Is | How We Use It |
|------|-----------|---------------|
| **Styles** | Figma containers for visual attributes (fills, strokes, text) | Legacy. Still useful, but we don't rely on them |
| **Variables** | Figma's native variables (newer feature). Store single values like colors or spacing | Token Studio syncs to these. This is the bridge to your components. |
| **Design Tokens** (ours) | JSON files we manage in Token Studio with semantic meaning | This is the source of truth. These feed into Figma Variables. |
| **Themes** | Groups of tokens organized by context (Light, Dark, brand, etc.) | You toggle themes in Token Studio, components auto-update |

**In practice:**
1. You edit values in **Token Studio** (the plugin)
2. Token Studio syncs to **Figma Variables** (Figma's native feature)
3. Your components reference **Figma Variables** (they see the updates)
4. Developers consume **Design Tokens** (the JSON files)

**Key insight:** Token Studio is the control center. Don't edit Figma Variables directly—always go through Token Studio.

---

## Token Studio Setup (Step-by-Step)

### Step 1: Install Plugin

1. **Open Figma** → Plugins menu → Search "Tokens"
2. **Install** "Figma Tokens" by Lukas Oppermann
3. **Open** the plugin in your file

### Step 2: Import v4 Tokens

**Option A: From GitHub (Recommended for teams)**

1. **In Token Studio plugin panel:**
   - Click Settings ⚙️
   - Choose **Sync** → **Add New** → **GitHub**
   - Enter your GitHub personal access token and repo path (ask your dev team for this)
   - Token Studio will sync with the shared token repository

2. **Expected token sets appear automatically:**
   - `global` (primitives)
   - `_Base/Value` (default brand)
   - `01_Brand/Value` (your brand overrides)
   - `02_Semantics/Light` (light theme)
   - `02_Semantics/Dark` (dark theme)
   - `03_Responsive/Mode 1` (optional)

**Option B: Manual Upload (For one-off projects)**

1. Download the v4 token JSON files
2. In Token Studio → Click Settings ⚙️
3. Drag/upload the JSON files into the panel
4. Token sets will appear

### Step 3: Editing Token Values

1. **Find the token** you want to update in Token Studio
2. **Click the value field** (e.g., color hex code)
3. **Edit the value** to your new color/size/font
4. **Changes appear instantly** in your Figma components (if they use that token)

**Important:** Token Studio won't let you delete tokens even if unused. This is intentional — it keeps the system stable. Leave unused tokens in place.

### Step 4: Create Themes

1. **Click Themes** in Token Studio
2. **New theme:** "Light Mode"
   - Enable: `global`, `_Base/Value`, `01_Brand/Value`, `02_Semantics/Light`
3. **New theme:** "Dark Mode"
   - Enable: `global`, `_Base/Value`, `01_Brand/Value`, `02_Semantics/Dark`

Now you can toggle Light ↔ Dark in Token Studio and see components update in Figma.

### Step 5: Syncing to GitHub (Team Workflow)

After you've updated tokens:

1. **In Token Studio → Click Push** (bottom of panel)
2. **Add a commit message** describing your changes:
   ```
   Updated primary brand colors for Q1 refresh
   ```
3. **Select your branch** and click **Push**
4. **If pushing to a branch** (not main), create a Pull Request for dev review
5. **Dev team pulls the changes** → Their build auto-updates → All platforms reflect your changes

**Pull updates from dev:**
- If dev made changes to tokens, click **Pull** in Token Studio to get the latest

---

## What Changed (Nov 12 — Breaking Change)

**Token name:** `AppliedBlue` → `BrandPrimary`

**Why:** Remove company-specific branding for white-label system

**What you see in Token Studio:**

| Before | After | Impact |
|--------|-------|--------|
| Token: `AppliedBlue.60` | Token: `BrandPrimary.60` | Name in Token Studio UI |
| Color: #335fff | Color: #335fff (unchanged) | Visual: No change |
| Used in: Brand components | Used in: Brand components | Same components work |

**In practice:** If you have components using the old `AppliedBlue` token, re-assign them to `BrandPrimary`. Same color, new name. Takes 5 minutes.

**For clients:** When they customize brand colors, they override `BrandPrimary` to their color. No "Applied" branding shows to their end users.

---

## How to Use Tokens in Figma

### Applying Tokens to Components

**Color fill:**
1. Select element (text, shape, etc.)
2. In Design panel → Fill section
3. Click color swatch
4. Click **Token icon** (looks like `{}`)
5. Choose token from list: `surface-primary-enabled`

**Text styling:**
1. Select text element
2. Typography section → Click token icon
3. Choose: `Body/Medium` or `Display/Large`

**Component Button Example:**

```
Button component states:
├─ Default (enabled)
│  ├─ Fill: {surface-primary-enabled}
│  ├─ Text: {on-surface-primary-enabled}
│  └─ Spacing: {spacing-16}
├─ Pressed
│  ├─ Fill: {surface-primary-pressed}
│  └─ Text: {on-surface-primary-pressed}
└─ Disabled
   ├─ Fill: {surface-primary-disabled}
   └─ Text: {on-surface-primary-disabled}
```

When developers consume this component, they don't hardcode colors. They use token references.

---

## Creating a New Brand

### Scenario: Client "BrandName" Needs Custom Tokens

**Step 1: Create brand override file**

In your token files, create:
```
01_Brand/BrandName/Value.json
```

**Step 2: Override what's different**

```json
{
  "VOS": {
    "color": {
      "brand": {
        "primary": { "value": "#FF6B35" },  // Client's brand color
        "secondary": { "value": "#004E89" } // Client's accent
      },
      "type": {
        "fontFamily": {
          "primary": { "value": "Client Sans" }  // Client's font
        }
      }
    }
  }
}
```

**Step 3: Leave everything else as-is**

Don't recreate all tokens. Only override what's different. Everything else inherits from `_Base/Value`.

**Step 4: In Token Studio**

- Add new theme: "BrandName Light"
- Enable: `global`, `_Base/Value`, `01_Brand/BrandName`, `02_Semantics/Light`
- Your components auto-update to client colors

**Step 5: Export**

- Click Tokens panel → Export
- Share JSON with dev team
- They run build; client's branding is live

---

## Light/Dark Theme Pattern

### Same Tokens, Different Values

**Light Mode (02_Semantics/Light.json):**
```json
{
  "surface-primary-enabled": { "value": "{VOS.color.active.active-light-primary}" },
  "on-surface-enabled": { "value": "{VOS.color.blacks.black-90}" }
}
```

**Dark Mode (02_Semantics/Dark.json):**
```json
{
  "surface-primary-enabled": { "value": "{VOS.color.active.active-dark-primary}" },
  "on-surface-enabled": { "value": "{VOS.color.whites.white-90}" }
}
```

**Same token name.** Different values. Developers toggle theme once, everything updates.

### In Figma

1. Create component with light-mode colors
2. In Token Studio → Switch to "Dark Mode" theme
3. Component colors auto-swap (if you used tokens)
4. Add dark variant to component

Now one component supports both themes.

---

## Token Structure You'll Use

### global.json — The Foundation

```
Primitives (raw values)
├─ color-primitives (White, Black, BrandPrimary, Red, Green, Blue, etc.)
├─ spacing (4pt grid: spacing-4, spacing-8, spacing-16...)
├─ elevation (shadow levels: elevation-0 through elevation-4)
├─ radius (corner options: radius-small, medium, large, xlarge)
├─ fontSize (scale: 0-10, from 12px to 180px)
└─ lineHeight (reading comfort: multiple options)
```

**You use:** All of it. These are your design tokens.

### _Base/Value.json — Brand Defaults

```
Brand aliases
├─ VOS.color.brand (primary, secondary)
├─ VOS.color.active (light/dark variants for active states)
├─ VOS.color.background (light/dark backgrounds)
├─ VOS.color.status (success, warning, error, caution, info)
├─ VOS.type (font families, weights)
└─ VOS.radius (component rounding)
```

**You use:** When building components. These are semantic (meaning-based) tokens.

### 02_Semantics/Light.json & Dark.json — UI Roles

```
Component states
├─ surface-primary-enabled (main button state)
├─ surface-primary-pressed (tapped/hovered)
├─ surface-primary-disabled (inactive)
├─ on-surface-enabled (text on surface)
├─ divider (line colors)
├─ background-page (page backgrounds)
└─ etc.
```

**You use:** Most frequently. These are "ready to use" tokens.

---

## Common Patterns

### Pattern 1: Primary Action Button

```
Button component
├─ Background: {surface-primary-enabled}
├─ Text: {on-surface-primary-enabled}
├─ Padding: {spacing-16}
├─ Radius: {radius-component}
└─ States:
   ├─ :pressed → {surface-primary-pressed}
   ├─ :disabled → {surface-primary-disabled}
   └─ :focus → {surface-primary-enabled} + focus-ring
```

### Pattern 2: Secondary Button

```
Button component
├─ Background: {surface-secondary-enabled}
├─ Text: {on-surface-secondary-enabled}
├─ Padding: {spacing-12}
└─ States similar to above
```

### Pattern 3: Card/Container

```
Container component
├─ Background: {background-ui-primary}
├─ Border: {divider}
├─ Radius: {radius-container}
├─ Spacing (padding): {spacing-24}
└─ Shadow: {elevation-1}
```

Copy-paste this pattern for consistency.

---

## Exporting & Handoff to Devs

### When You're Done Designing

1. **In Token Studio → Export Tokens**
2. **Copy the JSON**
3. **Create PR** to your token repo with updated files:
   - `global.json`
   - `_Base/Value.json`
   - `01_Brand/[YourBrand]/Value.json` (if needed)
   - `02_Semantics/Light.json`
   - `02_Semantics/Dark.json`
   - `$themes.json` (auto-generated, includes Figma variable mappings)

4. **Write commit message:**
   ```
   feat(tokens): update BrandName theme for Q1 refresh
   
   - Updated primary color to #FF6B35
   - Updated font family to Client Sans
   - Added new functional colors for alerts
   ```

5. **Dev team gets notification** → They build → Everyone's synced

### No Manual Specs Needed

Devs don't need you to write color specs or send Figma file links. They consume the JSON directly.

---

## Tips & Best Practices

### ✅ Do

- **Use semantic token names** in components (not primitives)
  - ✅ Good: `surface-primary-enabled`
  - ❌ Avoid: `color-primitives.BrandPrimary.60`

- **Sync Variables to Figma** after editing
  - In Token Studio → Click sync icon
  - Updates Figma's native Variables with new values
  - This is the bridge between tokens and components

- **Test in both themes** (Light + Dark) before handing off
  - Toggle theme in Token Studio
  - Verify readability & contrast in both

- **Document new tokens** with inline comments if adding custom ones
  - Why was this token created?
  - What's it used for?

- **Keep token names consistent** with the established pattern
  - `category-modifier-state`
  - Examples: `surface-primary-enabled`, `text-disabled`, `divider`

- **Use spacing tokens** for consistency
  - Don't use custom spacing values
  - Pick from the 4pt grid: 4, 8, 12, 16, 24, 32, 48, 64

- **Use existing tokens where possible**
  - Try to reference Semantic tokens (already connected to themes)
  - Brand tokens are your second choice
  - Primitives are for rare edge cases only

### ❌ Don't

- **Don't skip the Sync Variables step** after editing
  - Without syncing, Figma won't see updated values
  - This is why components don't refresh

- **Don't mix themes** (Light tokens + Dark components)
  - Use one theme per page/frame

- **Don't hardcode colors** in components
  - Always use token references
  - Makes theme switching impossible

- **Don't create new tokens casually**
  - Talk to devs first: "Do we need a new token or can we use existing ones?"

- **Don't rename token folder names or folder structure**
  - Token names can change within Token Studio UI
  - But folder hierarchy must stay the same
  - Changing folder structure breaks the sync with Figma Variables

- **Don't rename existing tokens** without coordinating with dev
  - Breaks their imports
  - Use BREAKING_CHANGES_APPLIED.md as reference

- **Don't assume devs saw your changes**
  - Send a message: "Updated tokens for XYZ, ready to build"

- **Don't touch tokens.json directly in code**
  - Leave it for Token Studio to manage
  - Only revert if something broke (and ask for help)

---

## Real Workflow Example (IPSY)

**Monday:** Designer updates seasonal brand colors in Token Studio
- Primary: Purple → Teal
- Secondary: Gold → Coral

**Tuesday AM:** Designer exports tokens, creates PR
```
01_Brand/IPSY-Spring/Value.json updated
```

**Tuesday PM:** Dev reviews, merges PR, runs:
```bash
npx style-dictionary build
```

**Wednesday:** QA tests staging environment (all colors updated automatically)

**Thursday:** Deploy to production

**Without tokens:** This would take 1-2 weeks of back-and-forth specs and manual updates.

---

## Token Studio Pro vs. Free

**We use Token Studio Pro** because clients do. But for your workflow:

| Feature | Free | Pro |
|---------|------|-----|
| Basic token editing | ✅ | ✅ |
| GitHub sync | ✅ | ✅ |
| Figma variable support | ✅ | ✅ |
| Advanced UI | ❌ | ✅ |
| Team collaboration | Basic | ✅ |

For a solo team, Free is fine. For multi-brand at scale, Pro saves time.

---

## Troubleshooting

**Q: I updated a token but it doesn't show in my components**  
A: In Token Studio, click **Sync Variables to Figma** (this updates Figma's native variables). Then refresh components or reset them.

**Q: My components aren't picking up the new token values**  
A: Make sure Token Studio is in sync with Figma Variables. Click the sync icon. If still stuck, detach the component from main and re-apply tokens.

**Q: GitHub sync isn't working**  
A: Ask your dev team for your GitHub personal access token and the correct repo path. Make sure your token has `repo` permissions. Test the connection in Token Studio Settings.

**Q: I can't push my tokens to GitHub**  
A: You might not have write permission to the repo, or the GitHub token expired. Contact your dev team lead or request GitHub access.

**Q: Dark mode tokens aren't working**  
A: Make sure you switched to Dark theme in Token Studio, and Dark.json is enabled in the theme config. Also verify that components use semantic tokens (not primitives directly).

**Q: Developer said token name changed (AppliedBlue → BrandPrimary)**  
A: Re-assign your components to new token name. Same color, new name. Takes 5 min.

**Q: Can I use custom token names?**  
A: Yes, but keep the naming pattern: `category-modifier-state`. Devs will thank you.

**Q: What if I want to use a color not in tokens?**  
A: Add it to `global.json` as a new primitive, then create a semantic token for it. Don't use raw hex values.

**Q: Can I delete tokens I'm not using?**  
A: No — Token Studio prevents token deletion to keep the system stable. Unused tokens won't break anything. Just leave them.

---

## Next Steps

1. **Install Figma Tokens** plugin (if you haven't)
2. **Import v4 tokens** from the GitHub branch or JSON files
3. **Create Light/Dark themes** in Token Studio
4. **Pick 5 components** and re-assign them to use tokens
5. **Test theme switching** (Light ↔ Dark)
6. **Export and hand off** to dev team

---

**Status:** Production-proven workflow  
**Systems using this:** K&G, IPSY, Spabreaks, Trojan  
**Last Updated:** November 12, 2025  
**Questions?** Reference BREAKING_CHANGES_APPLIED.md for the Nov 12 token rename.

