# How to Swap Brand and Theme in VehicleOSDemo

## 🚀 One-Command Solution

The easiest way to swap brands and themes is using the `swap-tokens.sh` script. This single command handles everything automatically.

### Quick Start

```bash
cd VehicleOSDemo
./swap-tokens.sh <brand_theme>
```

### Available Brand/Theme Combinations

You have **6 brand/theme combinations** available:
- `default_day` - Default brand, Day theme
- `default_night` - Default brand, Night theme
- `performance_day` - Performance brand, Day theme
- `performance_night` - Performance brand, Night theme
- `luxury_day` - Luxury brand, Day theme
- `luxury_night` - Luxury brand, Night theme

### Examples

**Switch to Luxury Night:**
```bash
./swap-tokens.sh luxury_night
```

**Switch to Performance Day:**
```bash
./swap-tokens.sh performance_day
```

**Switch to Default Day:**
```bash
./swap-tokens.sh default_day
```

## What the Script Does

The `swap-tokens.sh` script automatically:

1. ✅ **Generates/regenerates all tokens** for all 6 brand/theme combinations
   - Runs `python3 _Scripts/token_transformer_full_coverage.py . --modes`
   - Ensures you always have the latest tokens

2. ✅ **Updates `gradle.properties`** with your selected brand/theme
   - Sets `token.brandTheme={brand}_{theme}`
   - Used by Gradle build system for automatic syncing

3. ✅ **Syncs token files** from `_TransformedTokens/xml/{brand}_{theme}/` to `app/src/main/res/values/`
   - Copies all XML token files (colors.xml, dimens.xml, typography.xml, etc.)
   - Overwrites existing files with new brand/theme tokens

4. ✅ **Ready to build** - No manual steps needed!

## After Running the Script

1. **Sync Gradle** in Android Studio (if using IDE)
   - Click "Sync Project with Gradle Files" or use `./gradlew build`

2. **Rebuild the project**
   - The app will now use the selected brand/theme tokens

3. **Run the app** to see the new brand/theme applied

## Current Brand/Theme

The current brand/theme is stored in `gradle.properties`:
```properties
token.brandTheme={brand}_{theme}
```

You can check the current setting by viewing `gradle.properties` or running:
```bash
grep token.brandTheme gradle.properties
```

## Automatic Token Syncing

The app's `build.gradle.kts` includes a `syncTokens` task that automatically runs before each build. This ensures:
- Tokens are always synced from `_TransformedTokens/xml/{brand}_{theme}/`
- The correct brand/theme is used based on `gradle.properties`
- No manual file copying is needed

## Manual Method (Advanced)

If you need to manually copy files (not recommended):

```bash
# From project root
cp _TransformedTokens/xml/{brand}_{theme}/*.xml VehicleOSDemo/app/src/main/res/values/
```

**Note:** This method doesn't update `gradle.properties` and won't work with the automatic sync task. Use `swap-tokens.sh` instead.

## Troubleshooting

**Q: Script says "Token directory not found"**  
A: The token generation step may have failed. Check that `_TransformedTokens/xml/{brand}_{theme}/` exists. Try running the transformer manually: `python3 _Scripts/token_transformer_full_coverage.py . --modes`

**Q: Tokens don't update after running script**  
A: Make sure to sync Gradle and rebuild. The script copies files, but Android Studio needs to sync to see changes.

**Q: Wrong brand/theme showing in app**  
A: Check `gradle.properties` to verify `token.brandTheme` is set correctly. Also ensure you've synced Gradle after running the script.

**Q: Can I use this in my own app?**  
A: Yes! Copy the `swap-tokens.sh` script and the `syncTokens` Gradle task from `build.gradle.kts` to your project. See `VehicleOSDemo/README.md` for integration details.

## Related Documentation

- **[Main README](../../README.md)** - Project overview and quick start
- **[Developer Workflow](../../_Docs/02_Workflows/DEV_WORKFLOW.md)** - Complete developer guide
- **[Figma MCP Workflow](../../_Docs/02_Workflows/FIGMA_MCP_WORKFLOW.md)** - AI-assisted development guide

