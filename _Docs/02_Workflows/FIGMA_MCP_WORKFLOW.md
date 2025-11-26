# AI-Assisted Development with Figma MCP

**For:** Designers and developers using Cursor AI with Figma designs  
**TL;DR:** Use Figma MCP Server in Cursor to generate code that automatically adheres to your design tokens from Figma.

---

## What is Figma MCP?

The **Figma Model Context Protocol (MCP) Server** allows Cursor AI to directly access your Figma designs and extract design tokens, spacing, typography, and component specifications. This enables AI-assisted development that automatically adheres to your design system.

**How it works:**
1. **Designer creates components in Figma** using design tokens
2. **Developer prompts Cursor** with a Figma design link
3. **Cursor uses Figma MCP** to extract design context (colors, spacing, typography, layout)
4. **Cursor generates code** that uses the actual design tokens from your system
5. **Result:** Code matches design exactly, using token references instead of hardcoded values

---

## Example Workflow

### Step 1: Designer Creates Component in Figma

Designer creates a vehicle component card in Figma using tokens:
- Card background: `{color.surface.primary}` token
- Text color: `{color.text.primary}` token
- Spacing: `{spacing-24}` token
- Typography: `{Typography.heading-80}` composition token

### Step 2: Developer Prompts Cursor

Developer in Cursor:
```
@Figma https://figma.com/design/.../VehicleCard
Build this component using our design tokens. 
Use the spacing, typography, and color tokens from the design.
```

### Step 3: Cursor Generates Token-Based Code

Cursor response generates Android XML/Kotlin code that:
- Uses `@color/color_surface_primary` (from tokens)
- Uses `@dimen/spacing_24` (from tokens)
- Uses `@string/typography_heading_80_font_family` (from tokens)
- Matches the Figma design exactly

---

## Real Example: VehicleOSDemo App

The **VehicleOSDemo** Android app (`VehicleOSDemo/`) was built using this workflow:

1. **Design created in Figma** with design tokens applied
2. **Figma MCP used in Cursor** to extract design specifications
3. **Code generated** using actual token references from `_TransformedTokens/xml/`
4. **Result:** A fully functional demo app that:
   - Uses brand/theme tokens (swappable with `./swap-tokens.sh`)
   - Matches Figma design exactly
   - Supports all 6 brand/theme combinations
   - No hardcoded values

**See it in action:**
```bash
cd VehicleOSDemo
./swap-tokens.sh luxury_night
# App now uses Luxury brand + Night theme tokens
```

**Key files:**
- `VehicleOSDemo/app/src/main/res/layout/activity_main.xml` — Layout built from Figma design
- `VehicleOSDemo/app/src/main/res/values/` — Token files synced from `_TransformedTokens/xml/`

---

## Best Practices

### ✅ Do

- **Always reference Figma designs** when prompting Cursor
- **Explicitly ask Cursor** to "use design tokens from the Figma design"
- **Verify generated code** uses token references (not hardcoded values)
- **Test with different brand/theme combinations** after generation
- **Check token names** match your token system structure

### ❌ Don't

- **Don't accept hardcoded values** — Always use token references
- **Don't skip token verification** after code generation
- **Don't use MCP without ensuring** token system is set up
- **Don't ignore brand/theme differences** — Test all combinations

---

## Prompting Tips

### Good Prompts

```
@Figma [Figma URL]
Build this component using our design tokens. 
Use spacing, typography, and color tokens from the design.
Reference tokens from _TransformedTokens/xml/{brand}_{theme}/
```

```
@Figma [Figma URL]
Generate Android XML layout matching this design.
Use design tokens for all colors, spacing, and typography.
Ensure it works with our brand/theme swapping system.
```

### What to Verify After Generation

1. **Colors:** Should use `@color/color_*` references, not hex codes
2. **Spacing:** Should use `@dimen/spacing_*` references, not hardcoded dp values
3. **Typography:** Should use `@string/typography_*` and `@dimen/font_size_*` references
4. **Brand/Theme:** Should work with `./swap-tokens.sh` command

---

## Integration with Token System

### How MCP Works with Our Tokens

1. **Figma design** uses Token Studio tokens
2. **MCP extracts** design specifications from Figma
3. **Cursor generates code** using token references
4. **Token transformer** (`token_transformer_full_coverage.py`) generates platform files
5. **swap-tokens.sh** syncs tokens to app
6. **Result:** Design → Code → App, all using tokens

### Token File Structure

When prompting Cursor, reference the token structure:
- `_Base/Value.json` — Base primitives
- `01_Brand/{Brand}.json` — Brand overrides
- `03_Themes/{Theme}.json` — Theme mappings
- `_TransformedTokens/xml/{brand}_{theme}/` — Generated Android XML

---

## Troubleshooting

**Q: Cursor generated hardcoded values instead of tokens**  
A: Explicitly mention "use design tokens" in your prompt. Reference the token file structure.

**Q: Generated code doesn't match Figma design**  
A: Verify the Figma design uses tokens (not local styles). Check that MCP can access the design.

**Q: Tokens don't work after generation**  
A: Run `python3 _Scripts/token_transformer_full_coverage.py . --modes` to regenerate tokens, then `./swap-tokens.sh {brand}_{theme}` to sync.

**Q: How do I know which tokens to use?**  
A: Check `_TransformedTokens/xml/{brand}_{theme}/` for available token names. Or reference the Figma design's token usage.

---

## Resources

- **[Figma MCP Server Guide](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server)** — Official Figma MCP documentation
- **[Useful Links](../01_Guides/USEFUL_LINKS.md)** — More Figma MCP resources
- **[Design Workflow](../02_Workflows/DESIGN_WORKFLOW.md)** — Setting up tokens in Figma
- **[Developer Workflow](../02_Workflows/DEV_WORKFLOW.md)** — Building with tokens

---

**Status:** ✅ Production-proven workflow  
**Example:** VehicleOSDemo app  
**Last Updated:** November 2025

