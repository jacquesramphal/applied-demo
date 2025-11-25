# How to Swap Brand and Theme in VehicleComponentsDemo

## Current Setup

The app currently uses tokens from `default_night` (Default brand, Night theme).

## Available Options

You have **6 brand/theme combinations** available in `_TransformedTokens/xml/`:
- `default_day` - Default brand, Day theme
- `default_night` - Default brand, Night theme (currently used)
- `performance_day` - Performance brand, Day theme
- `performance_night` - Performance brand, Night theme
- `luxury_day` - Luxury brand, Day theme
- `luxury_night` - Luxury brand, Night theme

## Method 1: Quick Swap (Copy Files)

**To change brand/theme:**

1. Copy the desired token files from `_TransformedTokens/xml/{brand}_{theme}/` to `app/src/main/res/values/`

   Example to switch to `luxury_day`:
   ```bash
   cp _TransformedTokens/xml/luxury_day/*.xml VehicleComponentsDemo/app/src/main/res/values/
   ```

2. Sync Gradle and rebuild

## Method 2: Using Android Resource Qualifiers (Recommended)

This allows automatic theme switching based on system dark mode.

### Setup Steps:

1. **Create theme-specific resource folders:**
   - `app/src/main/res/values/` - for Day theme (default)
   - `app/src/main/res/values-night/` - for Night theme

2. **Copy token files:**
   - Day theme: Copy from `_TransformedTokens/xml/{brand}_day/` to `values/`
   - Night theme: Copy from `_TransformedTokens/xml/{brand}_night/` to `values-night/`

3. **The app will automatically switch** between Day/Night based on system settings!

### To Change Brand:

Copy the appropriate brand files to both `values/` and `values-night/` folders.

## Method 3: Runtime Theme Switching (Advanced)

For runtime brand/theme switching, you would need to:
1. Create a ThemeManager class
2. Load resources dynamically
3. Apply theme programmatically

This is more complex but allows users to switch themes in-app.

## Quick Reference

**Current Brand/Theme:** Default + Night (in `app/src/main/res/values/`)

**To switch to:**
- **Luxury + Night:** `cp _TransformedTokens/xml/luxury_night/*.xml app/src/main/res/values/`
- **Performance + Day:** `cp _TransformedTokens/xml/performance_day/*.xml app/src/main/res/values/`
- **Default + Day:** `cp _TransformedTokens/xml/default_day/*.xml app/src/main/res/values/`

