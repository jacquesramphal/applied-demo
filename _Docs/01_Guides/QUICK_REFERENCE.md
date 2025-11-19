# Quick Reference Card — Token Audit Summary
**Print & Tack to Your Monitor** ✨

---

## 🎯 What Changed?

### 1️⃣ **BIG CHANGE: AppliedBlue → BrandPrimary**
- Reason: Remove company branding (must be white-label)
- Files affected: 4 (global, _Base, 01_Brand, $themes)
- References updated: 17
- Breaking: YES

### 2️⃣ **NEW: Spacing & Elevation Tokens**
- Spacing: 4pt grid (spacing-4, 8, 12, 16, 20, 24, 32, 40, 48, 64)
- Elevation: 5 levels (elevation-0 through elevation-4)
- Location: global.json (NEW FILE)
- File size: 347 lines

### 3️⃣ **NEW: global.json**
- Consolidated primitives with extensive comments
- 11 color scales (including BrandPrimary, Glass, Material A-series)
- All foundational tokens in one place
- Ready for Figma import

### 4️⃣ **FIXED: Typos**
- `postivee` → `positive` (2 locations)
- Fixed in Light.json & Dark.json

### 5️⃣ **ENHANCED: Platform Mapping**
- Added Android/QNX comments to semantic tokens
- Added WCAG accessibility notes
- Added Figma mapping hints

---

## 📊 File Status Snapshot

```
✅ COMPLETE   global.json (NEW)
✅ UPDATED    _Base/Value.json (3 refs + comments)
✅ UPDATED    01_Brand/Value copy.json (4 refs + comments)
✅ UPDATED    02_Semantics/Light.json (typo + 20 comments)
✅ UPDATED    02_Semantics/Dark.json (typo + 20 comments)
✅ UNCHANGED  03_Responsive/Mode 1.json
✅ UNCHANGED  $metadata.json
✅ UPDATED    $themes.json (13 Figma refs)
```

---

## 🚀 Migration Checklist

### For Designers
```bash
□ Backup Figma file
□ Import new global.json to Figma Tokens
□ Re-sync token sets
□ Search: "AppliedBlue" → Replace: "BrandPrimary"
□ Test Light/Dark theme switching
□ Verify buttons/surfaces render correctly
```
**Time:** ~15 minutes

### For Developers
```bash
□ Pull updated JSON files
□ Run: npx style-dictionary build
□ Update any hardcoded token references
□ Test Android/web output
□ Verify visual output unchanged
```
**Time:** ~20 minutes

---

## 📍 Where to Find Things

| Need | File | Location |
|------|------|----------|
| Spacing tokens | global.json | Lines 270-284 |
| Elevation tokens | global.json | Lines 286-313 |
| Color scales | global.json | Lines 13-268 |
| Brand overrides | 01_Brand/Value.json | Lines 79-84 |
| Semantic light | 02_Semantics/Light.json | Sections: onSurface, background, surface |
| Semantic dark | 02_Semantics/Dark.json | Mirrored from Light.json |
| Breaking change details | TOKEN_AUDIT.md | Full documentation |
| Full audit | TOKEN_AUDIT.md | Complete comparison & research |

## 💬 Comment Patterns in Token Files

When reading New token files, you'll see these inline comments:

| Pattern | Example | Means |
|---------|---------|-------|
| **BREAKING CHANGE** | `"BREAKING CHANGE (Nov 12): AppliedBlue → BrandPrimary"` | Requires code/design update |
| **ANDROID/QNX** | `"ANDROID: onSurfaceVariant \| QNX: text-disabled"` | Platform mapping reference |
| **FIGMA MAPPING** | `"FIGMA MAPPING: Referenced in brand.primary"` | Points to Figma integration |
| **HERO COLOR** | `"HERO COLOR (60%). Primary brand..."` | This is the main brand color clients override |
| **Fixed: typo** | `"Fixed: typo positivee → positive"` | Correction from previous version |
| **Industry standard** | `"4pt grid system (Material Design, Atlassian)"` | Why this value was chosen |
| **Usage context** | `"Used for button backgrounds"` | When to use this token |
| **Section header** | `"RAW PRIMITIVES — Base color values..."` | What this section contains |

---

## 🔍 Key Comments by Pattern

### Pattern 1: Breaking Change
```json
"_comment": "BREAKING CHANGE (Nov 12, 2025): AppliedBlue → BrandPrimary"
```
**Action:** Update references in code/designs

### Pattern 2: Platform Mapping
```json
"_comment": "ANDROID: onSurfaceVariant | QNX: text-disabled"
```
**Action:** Map to platform-specific framework

### Pattern 3: Figma Integration
```json
"_comment": "FIGMA MAPPING: Referenced in _Base/Value.json brand.primary"
```
**Action:** Verify Figma sync

---

## 💡 Remember

✅ **All color values are identical** — Only names changed (BrandPrimary)  
✅ **Visual output should not change** — Token rename, not redesign  
✅ **Spacing & elevation are new** — No breaking changes, just additions  
✅ **Light/Dark fully covered** — Both themes have complete semantic mappings  
✅ **Android & QNX supported** — Platform comments guide integration  

---

## 📞 Questions?

**See:**
- BREAKING_CHANGES_APPLIED.md (breaking change details)
- TOKEN_COMPARISON_AUDIT.md (full comparison with research alignment)
- INLINE_ANNOTATIONS_GUIDE.md (comment pattern reference)
- CHANGE_SUMMARY_TABLE.md (updateable tracking table)

**Meeting reference:** Nov 10, 2025 — Design System & Token Setup Walkthrough  
**Research reference:** VehicleOS Design Tokens – Updated Structure & Guidelines (REOS 2025-11)

---

**Version:** 1.0 | **Date:** November 12, 2025 | **Status:** ✅ READY TO IMPLEMENT


