#!/bin/bash
# Script to swap brand and theme tokens in VehicleComponentsDemo
# Updates gradle.properties and triggers automatic token sync via Gradle

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
TOKENS_DIR="$PROJECT_ROOT/_TransformedTokens/xml"
GRADLE_PROPERTIES="$SCRIPT_DIR/gradle.properties"

# Available options
echo -e "${YELLOW}Available Brand/Theme Combinations:${NC}"
echo "  1) default_day      - Default brand, Day theme"
echo "  2) default_night    - Default brand, Night theme"
echo "  3) performance_day - Performance brand, Day theme"
echo "  4) performance_night - Performance brand, Night theme"
echo "  5) luxury_day       - Luxury brand, Day theme"
echo "  6) luxury_night     - Luxury brand, Night theme"
echo ""

# Check if argument provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: ./swap-tokens.sh <brand_theme>${NC}"
    echo "Example: ./swap-tokens.sh luxury_day"
    exit 1
fi

BRAND_THEME=$1
SOURCE_DIR="$TOKENS_DIR/$BRAND_THEME"

# Validate selection
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Error: Token directory not found: $SOURCE_DIR${NC}"
    echo "Available options: default_day, default_night, performance_day, performance_night, luxury_day, luxury_night"
    exit 1
fi

# Check if gradle.properties exists
if [ ! -f "$GRADLE_PROPERTIES" ]; then
    echo -e "${RED}Error: gradle.properties not found: $GRADLE_PROPERTIES${NC}"
    exit 1
fi

echo -e "${YELLOW}Swapping tokens to: $BRAND_THEME${NC}"
echo ""

# Update gradle.properties
echo -e "${BLUE}Updating gradle.properties...${NC}"
if grep -q "^token.brandTheme=" "$GRADLE_PROPERTIES"; then
    # Update existing property
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^token.brandTheme=.*/token.brandTheme=$BRAND_THEME/" "$GRADLE_PROPERTIES"
    else
        # Linux
        sed -i "s/^token.brandTheme=.*/token.brandTheme=$BRAND_THEME/" "$GRADLE_PROPERTIES"
    fi
else
    # Add property if it doesn't exist
    echo "token.brandTheme=$BRAND_THEME" >> "$GRADLE_PROPERTIES"
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Error updating gradle.properties${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Updated gradle.properties${NC}"
echo ""

# Sync token files directly (Gradle will also do this automatically on next build)
APP_VALUES_DIR="$SCRIPT_DIR/app/src/main/res/values"
echo -e "${BLUE}Syncing token files...${NC}"

if [ ! -d "$APP_VALUES_DIR" ]; then
    echo -e "${RED}Error: App values directory not found: $APP_VALUES_DIR${NC}"
    exit 1
fi

# Copy token files
cp "$SOURCE_DIR"/*.xml "$APP_VALUES_DIR/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Token files synced${NC}"
    echo ""
    echo -e "${GREEN}✓ Successfully swapped and synced tokens to: $BRAND_THEME${NC}"
    echo ""
    echo "The tokens are now active. Next steps:"
    echo "  1. Sync Gradle in Android Studio (if using IDE)"
    echo "  2. Rebuild the project"
    echo "  3. Run the app to see the new brand/theme"
    echo ""
    echo "Note: Future builds will automatically sync tokens from _TransformedTokens/xml/$BRAND_THEME/"
else
    echo -e "${RED}✗ Error syncing token files${NC}"
    exit 1
fi

