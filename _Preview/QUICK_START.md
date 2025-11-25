# Quick Start Guide

## 🚀 Start the Preview Site

### Option 1: Simple File Open
```bash
# Just open the HTML file in your browser
open _Preview/index.html
```

### Option 2: Local Server (Recommended)
```bash
# IMPORTANT: Run from PROJECT ROOT, not from _Preview directory
cd /path/to/applied-token-audit  # Go to project root
python3 -m http.server 8080
# Then visit http://localhost:8080/_Preview/ in your browser

# Or use the provided script:
./_Preview/start-server.sh

# If port 8080 is also in use, try:
python3 -m http.server 3000
# Or any other available port
```

## 🎨 Using the Preview

1. **Switch Brands**: Use the "Brand" dropdown to select:
   - Default
   - Performance  
   - Luxury

2. **Switch Themes**: Use the "Theme" dropdown to select:
   - Day (Light mode)
   - Night (Dark mode)

3. **View Tokens**: Click "Show Tokens" to see all design tokens in a side panel

## 📦 What You'll See

- **Buttons**: All button variants and states
- **Cards**: Standard and elevated card components
- **Form Inputs**: Text fields, checkboxes, radio buttons
- **Typography**: Complete typography scale
- **Color Palette**: Visual color swatches with values
- **Spacing Scale**: Visual spacing tokens

## 🔄 How It Works

The preview dynamically loads CSS token files based on your selection:
- `_TransformedTokens/css/{brand}_{theme}/tokens.css`

All components automatically update when you switch brands or themes!

## 🐛 Troubleshooting

**Components not updating?**
- Make sure token files exist in `_TransformedTokens/css/`
- Run the transformer script: `python3 _Scripts/token_transformer_full_coverage.py . --modes`

**Colors look wrong?**
- Check browser console for CSS loading errors
- Verify the token CSS file path is correct

**Token viewer not working?**
- Make sure you're using a local server (not file://)
- Check browser console for JavaScript errors

