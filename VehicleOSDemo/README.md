# Vehicle Components Demo

A simple Android Studio project that uses XML design tokens to match the Figma design for vehicle component cards.

## Project Structure

```
VehicleOSDemo/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/example/vehicleosdemo/
│   │   │   │   └── MainActivity.kt
│   │   │   ├── res/
│   │   │   │   ├── layout/
│   │   │   │   │   └── activity_main.xml
│   │   │   │   ├── values/
│   │   │   │   │   ├── colors.xml (from tokens)
│   │   │   │   │   ├── dimens.xml (from tokens)
│   │   │   │   │   ├── typography.xml (from tokens)
│   │   │   │   │   └── strings.xml
│   │   │   │   └── drawable/
│   │   │   │       ├── ic_revert.xml
│   │   │   │       ├── progress_bar_background.xml
│   │   │   │       └── progress_bar_fill.xml
│   │   │   └── AndroidManifest.xml
│   │   └── build.gradle.kts
├── build.gradle.kts
└── settings.gradle.kts
```

## Design Tokens Used

This project uses XML design tokens from `_TransformedTokens/xml/default_night/`:

- **Colors**: `color_functional_caution` (yellow/orange for progress), `color_text_primary`, `color_surface_primary`, `color_background_background-dark-primary`
- **Spacing**: `@dimen/4`, `@dimen/16`, `@dimen/24`
- **Typography**: `@dimen/font_size_36`, `@dimen/font_size_24`, `@dimen/font_size_20`, `@dimen/line_height_48`, `@dimen/line_height_32`
- **Border Radius**: `@dimen/16` for card corners, `@dimen/4` for progress bar

## Features

- Vehicle component card matching Figma design
- Progress bar showing 65% tire pressure
- Uses XML tokens for all styling (colors, spacing, typography)
- Dark theme with proper contrast

## Setup

1. Open the project in Android Studio
2. Sync Gradle files
3. Run on an emulator or device (minSdk 24)

## Swapping Brand and Theme

**One command to swap and sync tokens!**

Use the `swap-tokens.sh` script to swap brand/theme combinations. It will:
- ✅ Update `gradle.properties` with your selection
- ✅ Sync token files immediately
- ✅ Configure automatic syncing for future builds

### Quick Swap

```bash
./swap-tokens.sh <brand_theme>
```

**Available options:**
- `default_day` - Default brand, Day theme
- `default_night` - Default brand, Night theme (default)
- `performance_day` - Performance brand, Day theme
- `performance_night` - Performance brand, Night theme
- `luxury_day` - Luxury brand, Day theme
- `luxury_night` - Luxury brand, Night theme

**Example:**
```bash
./swap-tokens.sh luxury_day
```

After running the script:
1. Sync Gradle in Android Studio (if using IDE)
2. Rebuild the project
3. Run the app to see the new brand/theme

### Automatic Token Sync

The token files are also automatically synced from `_TransformedTokens/xml/` during every Gradle build. The `swap-tokens.sh` script updates `gradle.properties` with the `token.brandTheme` property, which tells the build system which tokens to use.

This means:
- ✅ **No manual copying needed** - Just rebuild after regenerating tokens
- ✅ **Always in sync** - Token files update automatically when you regenerate them
- ✅ **One command** - `./swap-tokens.sh` handles everything

### Manual Configuration (Advanced)

You can also manually edit `gradle.properties`:

```properties
token.brandTheme=default_night
```

Then rebuild the project - tokens will sync automatically.

See `BRAND_THEME_SWAP.md` for more details.

## Design Reference

Based on Figma design: https://www.figma.com/design/5rEM7fmSLwZeWNkLRwqPLE/Jake-s-Branch?node-id=5046-622167&m=dev

