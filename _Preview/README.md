# Design Tokens Preview Site

An interactive preview site for viewing design tokens and components with brand/theme switching.

## Features

- **Brand Switching**: Switch between Default, Performance, and Luxury brands
- **Theme Switching**: Toggle between Day (light) and Night (dark) themes
- **Component Showcase**: View buttons, cards, inputs, typography, and more
- **Token Viewer**: Browse all design tokens organized by category
- **Color Palette**: Visual display of color tokens with values
- **Spacing Scale**: Visual representation of spacing tokens
- **Real-time Updates**: All components update instantly when switching brands/themes

## Usage

### Opening the Preview

Simply open `index.html` in a web browser:

```bash
# From the project root
open _Preview/index.html

# Or use a local server (recommended)
# IMPORTANT: Run server from PROJECT ROOT, not from _Preview directory
cd /path/to/applied-token-audit  # Go to project root
python3 -m http.server 8080
# Then visit http://localhost:8080/_Preview/

# Or use the provided script:
./_Preview/start-server.sh

# If port is in use, try a different port:
python3 -m http.server 3000
```

### Controls

- **Brand Selector**: Choose between Default, Performance, or Luxury
- **Theme Selector**: Switch between Day (light) and Night (dark)
- **Show Tokens Button**: Opens a side panel with all design tokens

### Components Shown

1. **Buttons**: Primary, Secondary, Tertiary, and Disabled states
2. **Cards**: Standard and elevated card components
3. **Form Inputs**: Text inputs, checkboxes, and radio buttons
4. **Typography**: Display, headings, body text, and labels
5. **Color Palette**: Key brand and functional colors
6. **Spacing Scale**: Visual spacing tokens

## File Structure

```
_Preview/
├── index.html      # Main HTML file
├── styles.css      # Component styles (uses token CSS)
├── app.js          # Brand/theme switching logic
└── README.md       # This file
```

## How It Works

1. The site loads CSS token files from `_TransformedTokens/css/{brand}_{theme}/tokens.css`
2. When you switch brands or themes, the CSS file is dynamically replaced
3. All components use CSS custom properties (variables) from the token files
4. The token viewer parses the CSS file to display all available tokens

## Token Categories

- **Colors**: Brand colors, functional colors, primitives, surfaces, text
- **Spacing**: 4pt grid spacing scale
- **Typography**: Font sizes, line heights, font weights
- **Border Radius**: Corner rounding values
- **Motion**: Durations, easing functions, transitions
- **Accessibility**: WCAG-compliant colors and focus indicators
- **Interactions**: Hover, active, focus, disabled states

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Custom Properties support required
- JavaScript enabled

## Development

To modify the preview site:

1. Edit `index.html` to add/remove components
2. Edit `styles.css` to style components (use token variables)
3. Edit `app.js` to modify switching logic or add features

## Notes

- The preview site uses relative paths to load token CSS files
- Make sure token files are generated before using the preview
- Run the transformer script with `--modes` flag to generate all combinations

