#!/usr/bin/env python3
"""
FULL COVERAGE Token Transformer
Generates both Kotlin (.kt) and XML (.xml) outputs for ALL token types with mode/theme support.

Features:
- Loads all token files with support for Brand and Theme modes
- Brand modes: Default, Performance, Luxury
- Theme modes: Day (light), Night (dark)
- Extracts ALL token types (colors, spacing, typography, motion, components, accessibility, etc.)
- Generates Kotlin outputs: Color.kt, Spacing.kt, Typography.kt, Motion.kt, etc.
- Generates XML outputs: colors.xml, dimens.xml, typography.xml, animations.xml, etc.
- Generates CSS outputs: tokens.css (CSS custom properties)
- Full coverage: 750+ tokens
- Mode-aware exports: Can export all brand/theme combinations separately
- Separate output folders: _TransformedTokens/kotlin/, _TransformedTokens/xml/, and _TransformedTokens/css/

Usage:
    # Export default combination (Default brand, Day theme)
    python3 token_transformer_full_coverage.py /path/to/workspace
    
    # Export all brand/theme combinations (6 combinations total)
    python3 token_transformer_full_coverage.py /path/to/workspace --modes

Output Structure (with --modes):
    _TransformedTokens/
    ├── kotlin/
    │   ├── default_day/     # Default brand, Day theme
    │   ├── default_night/   # Default brand, Night theme
    │   ├── performance_day/  # Performance brand, Day theme
    │   ├── performance_night/
    │   ├── luxury_day/
    │   └── luxury_night/
    ├── xml/
    │   └── (same structure)
    └── css/
        └── (same structure)
"""

import json
import re
import sys
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class TransformerConfig:
    """Configuration for transformer."""
    base_path: str
    xml_output_path: Optional[str] = None
    verbose: bool = True


class FullCoverageTransformer:
    """Transform 750+ tokens to both Kotlin and XML formats."""

    def __init__(self, config: TransformerConfig):
        self.config = config
        self.base_path = Path(config.base_path)
        self.token_data = {}
        self.resolved_cache = {}
        self.unresolved_refs = set()
        
        # Initialize output paths
        self.xml_output_path = Path(config.xml_output_path or self.base_path / "_TransformedTokens" / "xml")
        
        # Create output directories
        self.xml_output_path.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "info"):
        """Log with emoji indicators."""
        if not self.config.verbose:
            return
        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌", "debug": "🐛"}
        icon = icons.get(level, "•")
        print(f"{icon}  {message}")

    def load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading {file_path}: {e}", "error")
            return {}

    def load_all_tokens(self, brand: str = "Default", theme: str = "Day"):
        """
        Load all token files with support for brand and theme modes.
        
        Args:
            brand: Brand mode - "Default", "Performance", or "Luxury"
            theme: Theme mode - "Day" or "Night"
        """
        # Always load base tokens
        base_files = [
            "Tokens/_Base/Value.json",
        ]
        
        # Load brand-specific tokens
        brand_files = [
            f"Tokens/01_Brand/{brand}.json",
        ]
        
        # Load theme-specific tokens
        theme_files = [
            f"Tokens/03_Themes/{theme}.json",
        ]
        
        # Load shared tokens (motion, interactions, components)
        shared_files = [
            "Tokens/04_Motion/Animations.json",
            "Tokens/05_Interactions/States.json",
            "Tokens/07_Components/Compositions.json",
        ]
        
        all_files = base_files + brand_files + theme_files + shared_files
        
        self.log(f"Loading tokens for Brand={brand}, Theme={theme}...", "info")
        self.log(f"  Total files: {len(all_files)}", "info")
        
        for file_path in all_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                self.log(f"  ✓ {file_path}")
                data = self.load_json(full_path)
                # Deep merge to avoid overwriting nested objects
                self._deep_merge(self.token_data, data)
            else:
                self.log(f"  ⚠ {file_path} not found", "warning")
        
        self.log(f"Loaded all tokens. Total keys: {len(self.token_data)}", "success")
    
    def _deep_merge(self, target: dict, source: dict):
        """Deep merge source dict into target dict."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                self._deep_merge(target[key], value)
            else:
                # Otherwise, update/add the value
                target[key] = value

    def resolve_reference(self, ref_string: str) -> str:
        """Resolve token references, handling recursive/nested references."""
        if ref_string in self.resolved_cache:
            return self.resolved_cache[ref_string]

        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, ref_string)

        if not matches:
            return ref_string

        resolved = ref_string
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while '{' in resolved and iteration < max_iterations:
            iteration += 1
            matches = re.findall(pattern, resolved)
            if not matches:
                break
                
        for token_path in matches:
            value = self._get_token_value(token_path)
            if value:
                # Convert value to string and recursively resolve if it contains references
                value_str = str(value)
                if '{' in value_str:
                    # Recursively resolve nested references
                    value_str = self.resolve_reference(value_str)
                resolved = resolved.replace(f"{{{token_path}}}", value_str)
            else:
                self.unresolved_refs.add(token_path)
                # If we can't resolve, keep the original reference
                break

        self.resolved_cache[ref_string] = resolved
        return resolved

    def _get_token_value(self, path: str):
        """Get token value by path."""
        parts = path.split('.')
        current = self.token_data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        if isinstance(current, dict):
            if 'value' in current:
                value = current['value']
                if isinstance(value, str) and '{' in value:
                    return self.resolve_reference(value)
                return value
        elif isinstance(current, (str, int, float, bool)):
            return current

        return None

    def _parse_dict_like_string(self, value_str: str) -> Optional[Dict[str, Any]]:
        """Try to parse a dict-like string (e.g., "{'key': 'value'}") into a dict."""
        if not isinstance(value_str, str):
            return None
        
        # Check if it looks like a dict string
        value_str = value_str.strip()
        if not (value_str.startswith("{") and value_str.endswith("}")):
            return None
        
        try:
            # Try to parse as Python dict using ast.literal_eval (safe)
            parsed = ast.literal_eval(value_str)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, SyntaxError):
            # If literal_eval fails, try a simpler regex-based approach
            # This handles cases like "{'fill': '{color.red.red-30}'}"
            pass
        
        return None

    # ===== EXTRACTION METHODS =====

    def extract_assets(self) -> Dict[str, str]:
        """Extract all asset tokens from brand files."""
        assets = {}
        
        # Extract brand assets (asset.brandLogo, etc.)
        if "asset" in self.token_data:
            asset_data = self.token_data["asset"]
            if isinstance(asset_data, dict):
                for name, token_def in asset_data.items():
                    if isinstance(token_def, dict) and "value" in token_def:
                        key = f"asset_{name}"
                        value = self.resolve_reference(str(token_def["value"]))
                        assets[key] = value
        
        self.log(f"Extracted {len(assets)} asset tokens", "info")
        return assets

    def extract_colors(self) -> Dict[str, str]:
        """Extract all color tokens from primitives, brand, and theme."""
        colors = {}
        
        # Extract color-primitives
        if "color-primitives" in self.token_data:
            for color_group, values in self.token_data["color-primitives"].items():
                if isinstance(values, dict):
                    for level, token_def in values.items():
                        if isinstance(token_def, dict) and "value" in token_def:
                            key = f"color_primitives_{color_group}_{level}"
                            value = self.resolve_reference(str(token_def["value"]))
                            colors[key] = value
        
        # Extract brand colors (color.brandPrimary, color.functional, etc.)
        if "color" in self.token_data:
            color_data = self.token_data["color"]
            if isinstance(color_data, dict):
                for category, category_data in color_data.items():
                    if isinstance(category_data, dict):
                        for name, token_def in category_data.items():
                            if isinstance(token_def, dict) and "value" in token_def:
                                key = f"color_{category}_{name}"
                                value = self.resolve_reference(str(token_def["value"]))
                                colors[key] = value
                            elif isinstance(token_def, dict):
                                # Handle nested structures (e.g., color.brandPrimary.primary)
                                for sub_name, sub_def in token_def.items():
                                    if isinstance(sub_def, dict) and "value" in sub_def:
                                        key = f"color_{category}_{name}_{sub_name}"
                                        value = self.resolve_reference(str(sub_def["value"]))
                                        colors[key] = value
        
        self.log(f"Extracted {len(colors)} color tokens", "info")
        return colors

    def extract_spacing(self) -> Dict[str, int]:
        """Extract spacing tokens."""
        spacing = {}
        if "spacing" in self.token_data:
            for name, token_def in self.token_data["spacing"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    spacing[name] = token_def["value"]
        self.log(f"Extracted {len(spacing)} spacing tokens", "info")
        return spacing

    def extract_typography(self) -> Dict[str, Dict]:
        """Extract typography tokens (font sizes, line heights, weights, compositions)."""
        typography = {
            "fontSize": {},
            "lineHeight": {},
            "fontWeight": {},
            "compositions": {}  # Typography composition tokens (heading-80, body-100, etc.)
        }
        
        # Extract fontSize
        if "fontSize" in self.token_data:
            fs_data = self.token_data["fontSize"]
            self.log(f"  Found fontSize with {len(fs_data)} tokens", "debug")
            for name, token_def in fs_data.items():
                if not name.startswith("_"):  # Skip comments
                    if isinstance(token_def, dict) and "value" in token_def:
                        typography["fontSize"][name] = token_def["value"]
                        self.log(f"    fontSize.{name} = {token_def['value']}", "debug")
        
        # Extract lineHeight
        if "lineHeight" in self.token_data:
            lh_data = self.token_data["lineHeight"]
            self.log(f"  Found lineHeight with {len(lh_data)} tokens", "debug")
            for name, token_def in lh_data.items():
                if not name.startswith("_"):  # Skip comments
                    if isinstance(token_def, dict) and "value" in token_def:
                        typography["lineHeight"][name] = token_def["value"]
                        self.log(f"    lineHeight.{name} = {token_def['value']}", "debug")
        
        # Extract font weights from Typography-Advanced
        if "Typography-Advanced" in self.token_data:
            typo_adv = self.token_data["Typography-Advanced"]
            if isinstance(typo_adv, dict):
                for name, token_def in typo_adv.items():
                    if not name.startswith("_") and isinstance(token_def, dict) and "value" in token_def:
                        if "font-weight" in name.lower():
                            weight_name = name.replace("font-weight-", "").replace("-", "_")
                            typography["fontWeight"][weight_name] = token_def["value"]
        
        # Extract Typography composition tokens (heading-80, body-100, etc.)
        if "Typography" in self.token_data:
            typo_compositions = self.token_data["Typography"]
            if isinstance(typo_compositions, dict):
                for name, token_def in typo_compositions.items():
                    if not name.startswith("_") and isinstance(token_def, dict) and "value" in token_def:
                        value = token_def["value"]
                        if isinstance(value, dict):
                            # Resolve fontFamily references and extract all typography properties
                            resolved_value = {}
                            for key, val in value.items():
                                if key == "fontFamily" and isinstance(val, str) and val.startswith("{") and val.endswith("}"):
                                    # Resolve fontFamily reference (e.g., {fontFamily.hmi})
                                    font_family_path = val.strip("{}")
                                    resolved_font = self._get_token_value(font_family_path)
                                    if resolved_font:
                                        # Extract font name from resolved value (e.g., "tt commons pro", "Arial, sans-serif", "Georgia, serif")
                                        font_name = resolved_font if isinstance(resolved_font, str) else str(resolved_font)
                                        font_name_lower = font_name.lower()
                                        # Map to Android system fonts:
                                        # - "Arial, sans-serif" or "tt commons pro" → sans-serif (TT Commons Pro is a sans-serif font)
                                        # - "Georgia, serif" → serif
                                        if "georgia" in font_name_lower or ("serif" in font_name_lower and "sans-serif" not in font_name_lower):
                                            resolved_value[key] = "serif"
                                        else:
                                            # Default to sans-serif for Arial, TT Commons Pro, and any other sans-serif fonts
                                            resolved_value[key] = "sans-serif"
                                    else:
                                        resolved_value[key] = "sans-serif"  # Default fallback
                                elif key == "letterSpacing" and isinstance(val, (str, int, float)):
                                    # Resolve letterSpacing if it's a reference, otherwise keep the value
                                    if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
                                        letter_spacing_path = val.strip("{}")
                                        resolved_letter_spacing = self._get_token_value(letter_spacing_path)
                                        if resolved_letter_spacing is not None:
                                            resolved_value[key] = resolved_letter_spacing
                                        else:
                                            # If resolution fails, try to extract numeric value from the path
                                            # e.g., {letterSpacing.normal} -> check if there's a numeric value
                                            resolved_value[key] = val  # Keep original if can't resolve
                                    else:
                                        # Direct value (number or string number)
                                        resolved_value[key] = float(val) if isinstance(val, (str, int, float)) and str(val).replace('.', '').isdigit() else val
                                else:
                                    # Keep other values as-is (fontSize, lineHeight, etc.)
                                    resolved_value[key] = val
                            typography["compositions"][name] = resolved_value
        
        # Fallback: create standard weights if not found
        if not typography["fontWeight"]:
            self.log("  No font weights found, using defaults", "debug")
            typography["fontWeight"] = {
                "light": 300,
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700
            }
        
        total = sum(len(v) for v in typography.values())
        self.log(f"Extracted {total} typography tokens (sizes: {len(typography['fontSize'])}, heights: {len(typography['lineHeight'])}, weights: {len(typography['fontWeight'])}, compositions: {len(typography['compositions'])})", "info")
        return typography

    def extract_elevation(self) -> Dict[str, Dict]:
        """Extract elevation/shadow tokens."""
        elevation = {}
        if "elevation" in self.token_data:
            for name, token_def in self.token_data["elevation"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    elevation[name] = token_def["value"]
        self.log(f"Extracted {len(elevation)} elevation tokens", "info")
        return elevation

    def extract_radius(self) -> Dict[str, int]:
        """Extract border radius tokens."""
        radius = {}
        if "borderRadius" in self.token_data:
            for name, token_def in self.token_data["borderRadius"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    radius[name] = token_def["value"]
        self.log(f"Extracted {len(radius)} border radius tokens", "info")
        return radius

    def extract_border_width(self) -> Dict[str, str]:
        """Extract border width tokens."""
        border_width = {}
        if "borderWidth" in self.token_data:
            for name, token_def in self.token_data["borderWidth"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    border_width[name] = token_def["value"]
        self.log(f"Extracted {len(border_width)} border width tokens", "info")
        return border_width

    def extract_text_case(self) -> Dict[str, str]:
        """Extract text case tokens."""
        text_case = {}
        if "textCase" in self.token_data:
            for name, token_def in self.token_data["textCase"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    text_case[name] = token_def["value"]
        self.log(f"Extracted {len(text_case)} text case tokens", "info")
        return text_case

    def extract_letter_spacing(self) -> Dict[str, Dict]:
        """Extract letter spacing tokens."""
        letter_spacing = {}
        if "letterSpacing" in self.token_data:
            letter_spacing = self.token_data["letterSpacing"]
        self.log(f"Extracted {len(letter_spacing)} letter spacing token groups", "info")
        return letter_spacing

    def extract_layout(self) -> Dict[str, Dict]:
        """Extract layout tokens (breakpoints, spacing modes, touch targets)."""
        layout = {}
        if "layout" in self.token_data:
            layout = self.token_data["layout"]
        self.log(f"Extracted {len(layout)} layout token groups", "info")
        return layout

    def extract_platforms(self) -> Dict[str, Dict]:
        """Extract platform-specific tokens (Android, QNX)."""
        platforms = {}
        if "platforms" in self.token_data:
            platforms = self.token_data["platforms"]
        self.log(f"Extracted {len(platforms)} platform-specific token groups", "info")
        return platforms

    def extract_motion(self) -> Dict[str, Dict]:
        """Extract motion/animation tokens (durations, easing, transitions)."""
        motion = {}
        if "motion" in self.token_data:
            motion = self.token_data["motion"]
        self.log(f"Extracted {len(motion)} motion token groups (duration, easing, transitions)", "info")
        return motion

    def extract_accessibility(self) -> Dict[str, str]:
        """Extract accessibility tokens."""
        accessibility = {}
        
        # From color-primitives.Accessibility
        if "color-primitives" in self.token_data:
            if "Accessibility" in self.token_data["color-primitives"]:
                for name, token_def in self.token_data["color-primitives"]["Accessibility"].items():
                    if isinstance(token_def, dict) and "value" in token_def:
                        accessibility[name] = str(token_def["value"])
        
        # From root level Accessibility
        if "Accessibility" in self.token_data:
            for name, token_def in self.token_data["Accessibility"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    accessibility[name] = str(token_def["value"])
        
        # Fallback: create standard accessibility tokens
        if not accessibility:
            accessibility = {
                "wcag_aa_text_on_primary": "#ffffff",
                "wcag_aa_text_on_error": "#ffffff",
                "wcag_aa_text_on_success": "#ffffff",
                "wcag_aa_text_on_warning": "#000000",
                "high_contrast_primary": "#0033cc",
                "high_contrast_text": "#000000",
                "focus_indicator": "#ffff00",
                "focus_indicator_dark": "#ffff00"
            }
        
        self.log(f"Extracted {len(accessibility)} accessibility tokens", "info")
        return accessibility

    def extract_interactions(self) -> Dict[str, Dict]:
        """Extract interaction state tokens (hover, active, focus, disabled, etc.)."""
        interactions = {}
        if "interaction" in self.token_data:
            interactions = self.token_data["interaction"]
        self.log(f"Extracted {len(interactions)} interaction state groups (hover, active, focus, disabled, etc.)", "info")
        return interactions

    def extract_components(self) -> Dict[str, Dict]:
        """Extract component-specific tokens (button, card, notification, input, checkbox, radio, toggle, select, modal)."""
        components = {}
        # Extract all known component types (from Compositions.json)
        for key in ["button", "input", "card", "notification", "form", "checkbox", "radio", "toggle", "select", "modal"]:
            if key in self.token_data:
                components[key] = self.token_data[key]
        self.log(f"Extracted {len(components)} component groups (buttons, cards, notifications, forms, inputs, checkboxes, radios, toggles, selects, modals)", "info")
        return components

    def extract_all_tokens(self) -> Dict[str, Any]:
        """Extract all token types."""
        return {
            "colors": self.extract_colors(),
            "spacing": self.extract_spacing(),
            "typography": self.extract_typography(),
            "elevation": self.extract_elevation(),
            "radius": self.extract_radius(),
            "border_width": self.extract_border_width(),
            "text_case": self.extract_text_case(),
            "letter_spacing": self.extract_letter_spacing(),
            "layout": self.extract_layout(),
            "platforms": self.extract_platforms(),
            "motion": self.extract_motion(),
            "accessibility": self.extract_accessibility(),
            "interactions": self.extract_interactions(),
            "components": self.extract_components(),
            "assets": self.extract_assets(),
        }

    # ===== XML OUTPUT GENERATION =====

    # ===== XML OUTPUT GENERATION =====

    def generate_xml_assets(self, assets: Dict[str, str]) -> str:
        """Generate assets.xml for asset tokens (URLs to images, icons, etc.)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- ASSET TOKENS - URLs to brand assets (logos, images, icons) -->\n\n'
        
        for name, value in sorted(assets.items()):
            if isinstance(value, str):
                # Asset tokens are stored as string resources (URLs)
                xml += f'    <string name="{self._to_snake_case(name)}">{value}</string>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_colors(self, colors: Dict[str, str]) -> str:
        """Generate colors.xml."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- COLOR TOKENS - Generated from design tokens -->\n\n'
        
        for name, value in sorted(colors.items()):
            # Android color resources cannot contain gradients - extract hex color or skip
            if isinstance(value, str) and "linear-gradient" in value.lower():
                # Extract first hex color from gradient (e.g., "linear-gradient(... #1A1A1A95 ...)" -> "#1A1A1A95")
                hex_match = re.search(r'#([0-9A-Fa-f]{6,8})', value)
                if hex_match:
                    # Use the first hex color found in the gradient
                    extracted_color = "#" + hex_match.group(1)
                    xml += f'    <color name="{self._to_snake_case(name)}">{extracted_color}</color>\n'
                else:
                    # Skip gradient colors that can't be parsed
                    continue
            elif isinstance(value, str) and value.startswith("#"):
                # Valid hex color
                xml += f'    <color name="{self._to_snake_case(name)}">{value}</color>\n'
            else:
                # Skip invalid color values
                continue
        
        xml += '</resources>\n'
        return xml

    def generate_xml_radius(self, radius: Dict[str, int]) -> str:
        """Generate radius.xml for border radius tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- BORDER RADIUS TOKENS - Corner rounding values -->\n\n'
        for name in sorted(radius.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            value = radius[name]
            # For numeric names, use them directly without the spacing_ prefix
            resource_name = name if name.isdigit() else self._to_snake_case(name)
            xml += f'    <dimen name="border_radius_{resource_name}">{value}dp</dimen>\n'
        xml += '</resources>\n'
        return xml

    def generate_xml_elevation(self, elevation: Dict[str, Any]) -> str:
        """Generate elevation.xml for elevation/shadow tokens - uses y (vertical offset) for Android elevation."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- ELEVATION TOKENS - Material Design elevation levels (y offset from boxShadow) -->\n\n'
        
        if elevation:
            for name in sorted(elevation.keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = elevation[name]
                resource_name = name if name.isdigit() else self._to_snake_case(name)
                
                # The value is the shadow dict (extracted by extract_elevation)
                if isinstance(value, dict):
                    # Extract y (vertical offset) for Android elevation
                    # Android elevation represents the shadow's vertical offset
                    y_offset = value.get("y", 0)
                    # Extract numeric value if it's a string like "2px" or number
                    if isinstance(y_offset, str):
                        y_offset = int(y_offset.replace('px', '').strip()) if y_offset.replace('px', '').strip().isdigit() else 0
                    elif isinstance(y_offset, (int, float)):
                        y_offset = int(y_offset)
                    else:
                        y_offset = 0
                    xml += f'    <dimen name="elevation_{resource_name}">{y_offset}dp</dimen>\n'
                elif isinstance(value, (int, float)):
                    xml += f'    <dimen name="elevation_{resource_name}">{int(value)}dp</dimen>\n'
                else:
                    xml += f'    <dimen name="elevation_{resource_name}">0dp</dimen>\n'
        else:
            # Fallback elevation values
            xml += '    <dimen name="elevation_0">0dp</dimen>      <!-- Flat -->\n'
            xml += '    <dimen name="elevation_1">2dp</dimen>      <!-- Subtle elevation -->\n'
            xml += '    <dimen name="elevation_2">4dp</dimen>      <!-- Medium elevation -->\n'
            xml += '    <dimen name="elevation_3">8dp</dimen>      <!-- High elevation -->\n'
            xml += '    <dimen name="elevation_4">16dp</dimen>     <!-- Maximum elevation -->\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_dimens(self, spacing: Dict[str, int], border_width: Dict[str, str] = None) -> str:
        """Generate dimens.xml (Android convention for spacing and border widths)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- SPACING TOKENS - 4pt grid system - Organized by token name suffix -->\n\n'
        
        # Extract numeric suffix from token name for grouping
        def get_sort_key(item):
            name, value = item
            # Extract numeric part from name (e.g., "spacing-2" -> 2, "compact-16" -> 16)
            parts = name.split('-')
            if parts[-1].isdigit():
                suffix_num = int(parts[-1])
            else:
                suffix_num = 999
            return (suffix_num, name)
        
        sorted_spacing = sorted(spacing.items(), key=get_sort_key)
        
        last_suffix = None
        for name, value in sorted_spacing:
            suffix = name.split('-')[-1]
            suffix_num = int(suffix) if suffix.isdigit() else 999
            
            # Add comment header for each new token suffix group
            if suffix_num != last_suffix:
                if last_suffix is not None:
                    xml += '\n'
                xml += f'    <!-- {suffix} (variants: spacing, compact, spacious) -->\n'
                last_suffix = suffix_num
            
            # Always prefix spacing tokens with "spacing_" for consistency
            token_name = self._to_snake_case(name)
            if not token_name.startswith("spacing_"):
                token_name = f"spacing_{token_name}"
            xml += f'    <dimen name="{token_name}">{value}dp</dimen>\n'
        
        # Add border width tokens
        if border_width:
            xml += '\n    <!-- BORDER WIDTH TOKENS -->\n\n'
            for name, value in sorted(border_width.items()):
                # Ensure all border width values have "dp" unit
                # Convert "px" to "dp" and add "dp" if no unit present
                if isinstance(value, str):
                    if value.endswith("px"):
                        # Convert px to dp (1px = 1dp for border widths in Android)
                        value_dp = value.replace("px", "dp")
                    elif value.endswith("dp"):
                        value_dp = value
                    elif value == "0" or value.isdigit():
                        # Add "dp" unit if missing
                        value_dp = f"{value}dp"
                    else:
                        value_dp = value
                else:
                    # Numeric value - add "dp" unit
                    value_dp = f"{value}dp"
                xml += f'    <dimen name="border_{self._to_snake_case(name)}">{value_dp}</dimen>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_styles(self, typography: Dict[str, Dict]) -> str:
        """Generate styles.xml (typography)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- TYPOGRAPHY TOKENS - Font sizes, line heights, font weights -->\n\n'
        
        # Font Sizes
        if typography["fontSize"]:
            xml += '    <!-- Font Sizes (sp) -->\n'
            for name in sorted(typography["fontSize"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["fontSize"][name]
                xml += f'    <dimen name="font_size_{self._to_snake_case(name)}">{value}sp</dimen>\n'
            xml += '\n'
        else:
            xml += '    <!-- Font Sizes (sp) -->\n'
            # Fallback
            for i in range(11):
                xml += f'    <dimen name="font_size_{i}">12sp</dimen>  <!-- Placeholder -->\n'
            xml += '\n'
        
        # Line Heights
        if typography["lineHeight"]:
            xml += '    <!-- Line Heights (sp) -->\n'
            for name in sorted(typography["lineHeight"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["lineHeight"][name]
                xml += f'    <dimen name="line_height_{self._to_snake_case(name)}">{value}sp</dimen>\n'
            xml += '\n'
        else:
            xml += '    <!-- Line Heights (sp) -->\n'
            # Fallback
            for i in range(5):
                xml += f'    <dimen name="line_height_{i}">20sp</dimen>  <!-- Placeholder -->\n'
            xml += '\n'
        
        # Font Weights
        xml += '    <!-- Font Weights -->\n'
        weights = typography["fontWeight"] if typography["fontWeight"] else {
            "light": 300,
            "regular": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700
        }
        for name, weight in sorted(weights.items()):
            xml += f'    <integer name="font_weight_{self._to_snake_case(name)}">{weight}</integer>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_typography_unified(self, typography: Dict[str, Dict], letter_spacing: Dict[str, Dict] = None, text_case: Dict[str, str] = None) -> str:
        """Generate unified typography.xml combining font sizes, line heights, weights, letter spacing, text case, and font families."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- COMPREHENSIVE TYPOGRAPHY TOKENS -->\n'
        xml += '    <!-- Combines font sizes, line heights, font weights, letter spacing, text case, and font families -->\n\n'
        
        # Font Families and Letter Spacing from Typography compositions
        xml += '    <!-- ========== TYPOGRAPHY COMPOSITIONS (font families, letter spacing) ========== -->\n'
        if typography.get("compositions"):
            for comp_name, comp_value in sorted(typography["compositions"].items()):
                if isinstance(comp_value, dict):
                    resource_name = self._to_snake_case(comp_name)
                    
                    # Generate font family string
                    if "fontFamily" in comp_value:
                        font_family = comp_value["fontFamily"]
                        xml += f'    <string name="typography_{resource_name}_font_family">{font_family}</string>\n'
                    
                    # Generate letter spacing string (for reference - Android letterSpacing doesn't support resources in XML)
                    # These will be used in TextAppearance styles
                    if "letterSpacing" in comp_value:
                        letter_spacing = comp_value["letterSpacing"]
                        # Store as string for reference (will be used in styles.xml)
                        xml += f'    <string name="typography_{resource_name}_letter_spacing">{letter_spacing}</string>\n'
        xml += '\n'
        
        # Font Sizes
        xml += '    <!-- ========== FONT SIZES ========== -->\n'
        if typography.get("fontSize"):
            for name in sorted(typography["fontSize"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["fontSize"][name]
                # For numeric names, use them directly without the spacing_ prefix
                resource_name = name if name.isdigit() else self._to_snake_case(name)
                xml += f'    <dimen name="font_size_{resource_name}">{value}sp</dimen>\n'
        xml += '\n'
        
        # Line Heights
        xml += '    <!-- ========== LINE HEIGHTS ========== -->\n'
        if typography.get("lineHeight"):
            for name in sorted(typography["lineHeight"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["lineHeight"][name]
                # For numeric names, use them directly without the spacing_ prefix
                resource_name = name if name.isdigit() else self._to_snake_case(name)
                xml += f'    <dimen name="line_height_{resource_name}">{value}sp</dimen>\n'
        xml += '\n'
        
        # Font Weights
        xml += '    <!-- ========== FONT WEIGHTS ========== -->\n'
        weights = typography.get("fontWeight") if typography.get("fontWeight") else {
            "light": 300,
            "regular": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700
        }
        for name, weight in sorted(weights.items()):
            xml += f'    <integer name="font_weight_{self._to_snake_case(name)}">{weight}</integer>\n'
        xml += '\n'
        
        # Letter Spacing (from Typography compositions - already handled above)
        # Note: Android letterSpacing attribute doesn't support resource references in XML,
        # so these are generated as strings for reference/documentation
        # They should be used programmatically or via TextAppearance styles
        
        # Text Case
        if text_case:
            xml += '    <!-- ========== TEXT CASE ========== -->\n'
            for name, value in sorted(text_case.items()):
                xml += f'    <string name="text_case_{self._to_snake_case(name)}">{value}</string>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_attrs(self, accessibility: Dict[str, str]) -> str:
        """Generate attrs.xml (accessibility color tokens)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- ACCESSIBILITY TOKENS - WCAG AA compliant colors, focus indicators, high contrast -->\n\n'
        
        # WCAG Text Pairs (white/black text on colored backgrounds)
        wcag_pairs = {k: v for k, v in accessibility.items() if 'wcag' in k.lower()}
        if wcag_pairs:
            xml += '    <!-- WCAG AA Compliant Text Pairs -->\n'
            for name, value in sorted(wcag_pairs.items()):
                clean_name = name.replace('-', '_').replace('wcag_aa_text_on_', 'text_on_').lower()
                xml += f'    <color name="accessibility_{clean_name}">{value}</color>\n'
            xml += '\n'
        
        # Focus Indicators
        focus_items = {k: v for k, v in accessibility.items() if 'focus' in k.lower()}
        if focus_items:
            xml += '    <!-- Focus Indicators (for keyboard navigation) -->\n'
            for name, value in sorted(focus_items.items()):
                clean_name = name.replace('-', '_').lower()
                xml += f'    <color name="accessibility_{clean_name}">{value}</color>\n'
            xml += '\n'
        
        # High Contrast Mode
        contrast_items = {k: v for k, v in accessibility.items() if 'high' in k.lower() or 'contrast' in k.lower()}
        if contrast_items:
            xml += '    <!-- High Contrast Mode (for accessibility) -->\n'
            for name, value in sorted(contrast_items.items()):
                clean_name = name.replace('-', '_').lower()
                xml += f'    <color name="accessibility_{clean_name}">{value}</color>\n'
        
        # Catch any remaining tokens
        used_keys = set(wcag_pairs.keys()) | set(focus_items.keys()) | set(contrast_items.keys())
        remaining = {k: v for k, v in accessibility.items() if k not in used_keys}
        if remaining:
            xml += '\n    <!-- Other Accessibility Tokens -->\n'
            for name, value in sorted(remaining.items()):
                clean_name = name.replace('-', '_').lower()
                xml += f'    <color name="accessibility_{clean_name}">{value}</color>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_animations(self, motion: Dict[str, Any]) -> str:
        """Generate animations.xml (motion tokens)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- MOTION TOKENS - Durations, easing functions, and transitions -->\n\n'
        
        # Durations
        xml += '    <!-- Durations (milliseconds) -->\n'
        if "duration" in motion:
            for name, token_def in motion["duration"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    xml += f'    <integer name="motion_duration_{self._to_snake_case(name)}">{token_def["value"]}</integer>\n'
        else:
            # Fallback
            xml += '    <integer name="motion_duration_short">100</integer>  <!-- Placeholder -->\n'
            xml += '    <integer name="motion_duration_standard">300</integer>  <!-- Placeholder -->\n'
            xml += '    <integer name="motion_duration_slow">500</integer>  <!-- Placeholder -->\n'
        
        # Easing
        xml += '\n    <!-- Easing Functions -->\n'
        if "easing" in motion:
            for name, token_def in motion["easing"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    easing_value = token_def["value"]
                    xml += f'    <string name="motion_easing_{self._to_snake_case(name)}">{easing_value}</string>\n'
        else:
            xml += '    <string name="motion_easing_default">cubic-bezier(0.25, 0.46, 0.45, 0.94)</string>  <!-- Placeholder -->\n'
            xml += '    <string name="motion_easing_entrance">cubic-bezier(0.34, 1.56, 0.64, 1)</string>  <!-- Placeholder -->\n'
        
        # Transitions
        xml += '\n    <!-- Transitions (combined duration + easing) -->\n'
        if "transition" in motion:
            for name, token_def in motion["transition"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    transition_value = token_def["value"]
                    # Resolve template syntax in transitions
                    if isinstance(transition_value, str):
                        transition_value = self.resolve_reference(transition_value)
                        # If still contains template syntax, use resolved values
                        if '{' in transition_value:
                            # Try to extract and resolve individual parts
                            # For now, use a simple fallback
                            transition_value = transition_value.replace('{motion.duration.fast}', '150ms')
                            transition_value = transition_value.replace('{motion.duration.standard}', '300ms')
                            transition_value = transition_value.replace('{motion.duration.slow}', '500ms')
                            transition_value = transition_value.replace('{motion.easing.smooth}', 'cubic-bezier(0.4, 0, 0.2, 1)')
                            transition_value = transition_value.replace('{motion.easing.default}', 'cubic-bezier(0.25, 0.46, 0.45, 0.94)')
                            transition_value = transition_value.replace('{motion.easing.entrance}', 'cubic-bezier(0.34, 1.56, 0.64, 1)')
                            transition_value = transition_value.replace('{motion.easing.exit}', 'cubic-bezier(0.66, 0, 0.66, 0.07)')
                    xml += f'    <string name="motion_transition_{self._to_snake_case(name)}">{transition_value}</string>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_text_case(self, text_case: Dict[str, str]) -> str:
        """Generate text-case.xml for text transformation tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- TEXT CASE TOKENS - Text transformation values -->\n\n'
        for name, value in sorted(text_case.items()):
            xml += f'    <string name="text_case_{self._to_snake_case(name)}">{value}</string>\n'
        xml += '</resources>\n'
        return xml

    def generate_xml_letter_spacing(self, letter_spacing: Dict[str, Dict]) -> str:
        """Generate letter-spacing.xml for letter spacing tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- LETTER SPACING TOKENS - Fine-grained typography control -->\n\n'
        
        for category, tokens in sorted(letter_spacing.items()):
            xml += f'    <!-- {category.capitalize()} -->\n'
            if isinstance(tokens, dict):
                for name, token_def in sorted(tokens.items()):
                    if isinstance(token_def, dict) and "value" in token_def:
                        xml += f'    <dimen name="letter_spacing_{self._to_snake_case(category)}_{self._to_snake_case(name)}">{token_def["value"]}em</dimen>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_layout(self, layout: Dict[str, Dict]) -> str:
        """Generate layout.xml for layout tokens (breakpoints, spacing modes)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- LAYOUT TOKENS - Breakpoints, spacing modes, touch targets -->\n\n'
        
        for category, tokens in sorted(layout.items()):
            xml += f'    <!-- {category.capitalize()} -->\n'
            if isinstance(tokens, dict):
                for name, token_def in sorted(tokens.items()):
                    if isinstance(token_def, dict) and "value" in token_def:
                        value = token_def["value"]
                        xml += f'    <dimen name="layout_{self._to_snake_case(category)}_{self._to_snake_case(name)}">{value}dp</dimen>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_platforms(self, platforms: Dict[str, Dict]) -> str:
        """Generate platforms.xml for platform-specific tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- PLATFORM-SPECIFIC TOKENS - Android, QNX, Web configurations -->\n\n'
        
        for platform, tokens in sorted(platforms.items()):
            xml += f'    <!-- {platform.upper()} Platform -->\n'
            if isinstance(tokens, dict):
                for name, token_def in sorted(tokens.items()):
                    if isinstance(token_def, dict):
                        # Only extract the "value" key, ignore "type" and other metadata
                        if "value" in token_def:
                            value = token_def["value"]
                            xml += f'    <string name="platform_{self._to_snake_case(platform)}_{self._to_snake_case(name)}">{value}</string>\n'
                    elif isinstance(token_def, (str, int, float)):
                        # Direct value (not wrapped in dict)
                        xml += f'    <string name="platform_{self._to_snake_case(platform)}_{self._to_snake_case(name)}">{token_def}</string>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_interactions(self, interactions: Dict[str, Dict], colors: Dict[str, str] = None) -> str:
        """Generate interactions.xml for state tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- INTERACTION STATE TOKENS - Hover, active, focus, disabled, etc. -->\n\n'
        
        # Helper to resolve color references
        def resolve_color_value(value_str):
            """Resolve color reference to hex value."""
            if isinstance(value_str, str):
                # Check if it's already a hex color
                if value_str.startswith("#"):
                    return value_str
                # Try to resolve as reference
                resolved = self.resolve_reference(value_str)
                # If still contains template syntax, try to find in colors dict
                if colors and '{' in resolved:
                    # Extract color path from template syntax
                    import re
                    matches = re.findall(r'\{([^}]+)\}', resolved)
                    for match in matches:
                        # Try to find matching color key
                        color_key = match.replace('.', '_').replace('-', '_')
                        # Search for matching color
                        for color_name, color_value in colors.items():
                            if color_key.lower() in color_name.lower() or color_name.lower().endswith(color_key.lower()):
                                return color_value
                # If resolved is a hex color, return it
                if resolved.startswith("#"):
                    return resolved
                # Otherwise return original if no match found
                return value_str
            return value_str
        
        for state_name, state_def in sorted(interactions.items()):
            xml += f'    <!-- {state_name.capitalize()} State -->\n'
            if isinstance(state_def, dict):
                for property_name, property_def in sorted(state_def.items()):
                    if isinstance(property_def, dict) and "value" in property_def:
                        value = property_def["value"]
                        full_name = f"interaction_{self._to_snake_case(state_name)}_{self._to_snake_case(property_name)}"
                        
                        # Resolve value if it's a string with references
                        if isinstance(value, str):
                            value = self.resolve_reference(value)
                        
                        # Skip cursor strings - not applicable to Android (CSS/web-specific)
                        if property_name.lower().endswith("_cursor") or property_name.lower() == "cursor":
                            continue
                        
                        # Determine resource type
                        if isinstance(value, str) and value.startswith("#"):
                            xml += f'    <color name="{full_name}">{value}</color>\n'
                        elif isinstance(value, str) and ("color" in property_name.lower() or "background" in property_name.lower() or "border" in property_name.lower() or "text" in property_name.lower()):
                            # Try to resolve as color
                            resolved_color = resolve_color_value(value)
                            if resolved_color and resolved_color.startswith("#"):
                                xml += f'    <color name="{full_name}">{resolved_color}</color>\n'
                        elif isinstance(value, str) and '{' in value:
                            # Still has template syntax - try to resolve color references
                            import re
                            color_refs = re.findall(r'\{([^}]+)\}', value)
                            resolved_value = value
                            
                            # Try to resolve each color reference
                            for color_ref in color_refs:
                                # Convert color path to resource name format
                                color_key = color_ref.replace('.', '_').replace('-', '_')
                                
                                # Search for matching color in colors dict
                                found_color = None
                                for color_name, color_value in colors.items() if colors else {}:
                                    # Match patterns like "color_active_active_dark_primary" or "color_active_dark_primary"
                                    if (color_key.lower() in color_name.lower() or 
                                        color_name.lower().endswith(color_key.lower()) or
                                        f"color_{color_key}" in color_name.lower()):
                                        found_color = color_value
                                        break
                                
                                if found_color:
                                    # Replace template syntax with resolved color
                                    resolved_value = resolved_value.replace(f"{{{color_ref}}}", found_color)
                                else:
                                    # Try to resolve via token system
                                    token_value = self._get_token_value(color_ref)
                                    if token_value and isinstance(token_value, str) and token_value.startswith("#"):
                                        resolved_value = resolved_value.replace(f"{{{color_ref}}}", token_value)
                            
                            # Check if we successfully resolved to a color
                            if resolved_value.startswith("#"):
                                xml += f'    <color name="{full_name}">{resolved_value}</color>\n'
                            elif '{' not in resolved_value and ("color" in property_name.lower() or "ring" in property_name.lower()):
                                # If it's a color property and we resolved it, output as color
                                # Extract hex color from resolved string if it contains one
                                hex_match = re.search(r'#([0-9A-Fa-f]{6,8})', resolved_value)
                                if hex_match:
                                    xml += f'    <color name="{full_name}">#{hex_match.group(1)}</color>\n'
                                else:
                                    # Output as string but try to use Android resource reference if possible
                                    xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                            else:
                                # Still has unresolved template syntax or not a color
                                # For outline strings, output as-is (may contain CSS-like syntax)
                                if "outline" in property_name.lower():
                                    xml += f'    <!-- Note: Outline uses CSS-like syntax, may need manual conversion -->\n'
                                xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                        elif isinstance(value, (int, float)):
                            # Use dimen for numeric values (opacity, delta, etc.)
                            xml += f'    <dimen name="{full_name}">{value}dp</dimen>\n'
                        else:
                            xml += f'    <string name="{full_name}">{value}</string>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_components(self, components: Dict[str, Dict]) -> str:
        """Generate components.xml for component-specific tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- COMPONENT TOKENS - Buttons, Cards, Notifications, Forms -->\n\n'
        
        for component_name, component_def in sorted(components.items()):
            xml += f'    <!-- {component_name.capitalize()} Component -->\n'
            
            if isinstance(component_def, dict):
                for variant_name, variant_def in sorted(component_def.items()):
                    if isinstance(variant_def, dict):
                        # Check if this is a nested variant structure (e.g., button.danger.active)
                        # If variant_def has "value" and "type" keys, it's a composition token at this level
                        # Otherwise, it might be a nested variant (e.g., danger -> active, hover, default)
                        if "value" in variant_def and "type" in variant_def:
                            # This is a composition token at this level (e.g., card.default)
                            # Process it directly by treating variant_def as if it has a "value" property
                            property_name = "value"
                            property_def = variant_def["value"]  # Get the actual value dict
                            # Now process it as a composition token
                            if isinstance(property_def, dict):
                                safe_component_name = self._to_snake_case(component_name)
                                safe_variant_name = self._to_snake_case(variant_name)
                                # Extract each property from the composition
                                # CRITICAL: Process ALL properties to ensure padding (horizontal, vertical, top, left, right, bottom) and all other properties are transformed
                                for prop_key, prop_value in sorted(property_def.items()):
                                    safe_prop_key = self._to_snake_case(prop_key)
                                    
                                    # Handle nested dicts (e.g., indicator: {size: "...", fill: "..."})
                                    if isinstance(prop_value, dict):
                                        # Extract nested properties
                                        for nested_key, nested_value in sorted(prop_value.items()):
                                            safe_nested_key = self._to_snake_case(nested_key)
                                            full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_prop_key}_{safe_nested_key}"
                                            
                                            # Resolve the nested value if it's a reference
                                            if isinstance(nested_value, str):
                                                resolved_value = self.resolve_reference(nested_value)
                                            else:
                                                resolved_value = nested_value
                                            
                                            # Determine resource type
                                            nested_key_lower = nested_key.lower()
                                            is_nested_color = any(x in nested_key_lower for x in ["color", "fill", "background"])
                                            is_nested_dimen = any(x in nested_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap", "horizontal", "vertical"])
                                            
                                            # Try to convert to number
                                            nested_numeric = None
                                            if isinstance(resolved_value, str):
                                                try:
                                                    # Remove units for numeric conversion
                                                    numeric_str = resolved_value.replace("px", "").replace("dp", "").strip()
                                                    if '.' in numeric_str:
                                                        nested_numeric = float(numeric_str)
                                                    else:
                                                        nested_numeric = int(numeric_str)
                                                except ValueError:
                                                    pass
                                            
                                            # Generate XML resource
                                            if isinstance(resolved_value, str):
                                                if resolved_value.startswith("#"):
                                                    xml += f'    <color name="{full_name}">{resolved_value}</color>\n'
                                                elif nested_numeric is not None and is_nested_dimen:
                                                    xml += f'    <dimen name="{full_name}">{nested_numeric}dp</dimen>\n'
                                                elif resolved_value.startswith("@"):
                                                    xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                                else:
                                                    xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                            elif isinstance(resolved_value, (int, float)):
                                                if is_nested_dimen:
                                                    xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                                else:
                                                    xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                            else:
                                                xml += f'    <string name="{full_name}">{str(resolved_value)}</string>\n'
                                        continue  # Skip processing this prop_key as a simple value
                                    
                                    # Handle simple (non-dict) properties
                                    full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_prop_key}"
                                    
                                    # Resolve the property value if it's a reference
                                    if isinstance(prop_value, str):
                                        resolved_value = self.resolve_reference(prop_value)
                                    else:
                                        resolved_value = prop_value
                                    
                                    # Determine resource type based on property name and value
                                    prop_key_lower = prop_key.lower()
                                    is_color_prop = any(x in prop_key_lower for x in ["color", "fill", "background"])
                                    is_dimen_prop = any(x in prop_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap", "shadow", "elevation", "horizontal", "vertical"])
                                    
                                    # SIMPLIFIED: Check if this is ANY padding property (padding, horizontalPadding, verticalPadding, paddingTop, etc.)
                                    is_padding_prop = "padding" in prop_key_lower
                                    
                                    # SIMPLIFIED: For padding properties, ALWAYS try to convert to number and write as dimen
                                    if is_padding_prop:
                                        padding_numeric = None
                                        if isinstance(resolved_value, (int, float)):
                                            padding_numeric = resolved_value
                                        elif isinstance(resolved_value, str):
                                            # If it's still a reference, try to resolve it one more time
                                            if resolved_value.startswith("{") and resolved_value.endswith("}"):
                                                further_resolved = self.resolve_reference(resolved_value)
                                                if further_resolved != resolved_value:
                                                    resolved_value = further_resolved
                                            
                                            # Remove units and try to convert
                                            numeric_str = resolved_value.replace("px", "").replace("dp", "").replace("%", "").strip()
                                            if numeric_str:
                                                try:
                                                    padding_numeric = float(numeric_str) if '.' in numeric_str else int(numeric_str)
                                                except (ValueError, TypeError):
                                                    pass
                                        
                                        if padding_numeric is not None:
                                            xml += f'    <dimen name="{full_name}">{padding_numeric}dp</dimen>\n'
                                        else:
                                            xml += f'    <string name="{full_name}">{str(resolved_value)}</string>\n'
                                    else:
                                        # Try to convert string to number if it looks numeric
                                        numeric_value = None
                                        if isinstance(resolved_value, str):
                                            try:
                                                numeric_str = resolved_value.replace("px", "").replace("dp", "").replace("%", "").strip()
                                                if numeric_str:
                                                    numeric_value = float(numeric_str) if '.' in numeric_str else int(numeric_str)
                                            except ValueError:
                                                pass
                                        
                                        # Check if resolved_value is a dict-like string that needs parsing, or an actual dict object
                                        parsed_dict = None
                                        if isinstance(resolved_value, str):
                                            parsed_dict = self._parse_dict_like_string(resolved_value)
                                        elif isinstance(resolved_value, dict):
                                            parsed_dict = resolved_value
                                        if parsed_dict:
                                            # Extract properties from the parsed dict
                                            for dict_key, dict_value in sorted(parsed_dict.items()):
                                                safe_dict_key = self._to_snake_case(dict_key)
                                                dict_full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_prop_key}_{safe_dict_key}"
                                                
                                                # Resolve the dict value if it's a reference
                                                if isinstance(dict_value, str):
                                                    dict_resolved = self.resolve_reference(dict_value)
                                                else:
                                                    dict_resolved = dict_value
                                                
                                                # Determine resource type
                                                dict_key_lower = dict_key.lower()
                                                is_dict_color = any(x in dict_key_lower for x in ["color", "fill", "background"])
                                                is_dict_dimen = any(x in dict_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap", "horizontal", "vertical", "x", "y", "blur", "spread"])
                                                
                                                # Try to convert to number
                                                dict_numeric = None
                                                if isinstance(dict_resolved, str):
                                                    try:
                                                        dict_numeric = float(dict_resolved) if '.' in dict_resolved else int(dict_resolved)
                                                    except ValueError:
                                                        pass
                                                
                                                # Generate XML resource
                                                if isinstance(dict_resolved, str):
                                                    if dict_resolved.startswith("#"):
                                                        xml += f'    <color name="{dict_full_name}">{dict_resolved}</color>\n'
                                                    elif dict_numeric is not None and is_dict_dimen:
                                                        xml += f'    <dimen name="{dict_full_name}">{dict_numeric}dp</dimen>\n'
                                                    elif dict_resolved.startswith("@"):
                                                        xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                                    else:
                                                        xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                                elif isinstance(dict_resolved, (int, float)):
                                                    if is_dict_dimen:
                                                        xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                                    else:
                                                        xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                                else:
                                                    xml += f'    <string name="{dict_full_name}">{str(dict_resolved)}</string>\n'
                                        # Generate appropriate XML resource based on value type and property name
                                        # Skip writing the full dict if we already extracted its properties
                                        if parsed_dict:
                                            # Already extracted dict properties, skip writing the full dict
                                            pass
                                        elif isinstance(resolved_value, str):
                                            if resolved_value.startswith("#"):
                                                xml += f'    <color name="{full_name}">{resolved_value}</color>\n'
                                            elif numeric_value is not None and is_dimen_prop:
                                                xml += f'    <dimen name="{full_name}">{numeric_value}dp</dimen>\n'
                                            elif is_color_prop and not resolved_value.startswith("@") and not resolved_value.startswith("#"):
                                                if resolved_value.startswith("{") or "color" in resolved_value.lower():
                                                    further_resolved = self.resolve_reference(resolved_value)
                                                    if further_resolved.startswith("#"):
                                                        xml += f'    <color name="{full_name}">{further_resolved}</color>\n'
                                                    else:
                                                        xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                                else:
                                                    xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                            elif resolved_value.startswith("@"):
                                                xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                            else:
                                                xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                        elif isinstance(resolved_value, (int, float)):
                                            if is_dimen_prop:
                                                xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                            elif is_color_prop:
                                                xml += f'    <color name="{full_name}">#{int(resolved_value):06x}</color>\n'
                                            else:
                                                xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                        elif isinstance(resolved_value, dict):
                                            # Dict objects should have been handled above by extracting properties
                                            # Only write as string if it wasn't parsed (shouldn't happen, but safety check)
                                            if not parsed_dict:
                                                # This shouldn't happen, but if it does, skip writing invalid dict syntax
                                                pass
                                        else:
                                            xml += f'    <string name="{full_name}">{str(resolved_value)}</string>\n'
                            continue  # Skip the nested variant processing for direct composition tokens
                        else:
                            # This is a nested variant structure, recurse into it
                            for sub_variant_name, sub_variant_def in sorted(variant_def.items()):
                                if isinstance(sub_variant_def, dict):
                                    # Process sub-variant
                                    for property_name, property_def in sorted(sub_variant_def.items()):
                                        safe_component_name = self._to_snake_case(component_name)
                                        safe_variant_name = self._to_snake_case(variant_name)
                                        safe_sub_variant_name = self._to_snake_case(sub_variant_name)
                                        safe_property_name = self._to_snake_case(property_name)
                                        
                                        # Skip type properties
                                        if property_name.endswith("_type") or property_name == "type":
                                            continue
                                        
                                        # Handle composition tokens: when property_name is "value" and property_def is a dict of properties
                                        if property_name == "value" and isinstance(property_def, dict):
                                            # Extract each property from the composition
                                            for prop_key, prop_value in sorted(property_def.items()):
                                                safe_prop_key = self._to_snake_case(prop_key)
                                                
                                                # Handle nested dicts (e.g., indicator: {size: "...", fill: "..."})
                                                if isinstance(prop_value, dict):
                                                    # Extract nested properties
                                                    for nested_key, nested_value in sorted(prop_value.items()):
                                                        safe_nested_key = self._to_snake_case(nested_key)
                                                        full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_sub_variant_name}_{safe_prop_key}_{safe_nested_key}"
                                                        
                                                        # Resolve the nested value if it's a reference
                                                        if isinstance(nested_value, str):
                                                            resolved_value = self.resolve_reference(nested_value)
                                                        else:
                                                            resolved_value = nested_value
                                                        
                                                        # Determine resource type
                                                        nested_key_lower = nested_key.lower()
                                                        is_nested_color = any(x in nested_key_lower for x in ["color", "fill", "background"])
                                                        is_nested_dimen = any(x in nested_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap", "horizontal", "vertical"])
                                                        
                                                        # Try to convert to number (handle units like "px", "dp")
                                                        nested_numeric = None
                                                        if isinstance(resolved_value, str):
                                                            try:
                                                                # Remove units for numeric conversion
                                                                numeric_str = resolved_value.replace("px", "").replace("dp", "").replace("%", "").strip()
                                                                if numeric_str and '.' in numeric_str:
                                                                    nested_numeric = float(numeric_str)
                                                                elif numeric_str:
                                                                    nested_numeric = int(numeric_str)
                                                            except ValueError:
                                                                pass
                                                        
                                                        # Generate XML resource
                                                        if isinstance(resolved_value, str):
                                                            if resolved_value.startswith("#"):
                                                                xml += f'    <color name="{full_name}">{resolved_value}</color>\n'
                                                            elif nested_numeric is not None and is_nested_dimen:
                                                                xml += f'    <dimen name="{full_name}">{nested_numeric}dp</dimen>\n'
                                                            elif resolved_value.startswith("@"):
                                                                xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                                            else:
                                                                xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                                        elif isinstance(resolved_value, (int, float)):
                                                            if is_nested_dimen:
                                                                xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                                            else:
                                                                xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                                        else:
                                                            xml += f'    <string name="{full_name}">{str(resolved_value)}</string>\n'
                                                    continue  # Skip processing this prop_key as a simple value
                                                
                                                # Handle simple (non-dict) properties
                                                full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_sub_variant_name}_{safe_prop_key}"
                                                
                                                # Resolve the property value if it's a reference
                                                if isinstance(prop_value, str):
                                                    resolved_value = self.resolve_reference(prop_value)
                                                else:
                                                    resolved_value = prop_value
                                                
                                                # Determine resource type based on property name and value
                                                prop_key_lower = prop_key.lower()
                                                is_color_prop = any(x in prop_key_lower for x in ["color", "fill", "background"])
                                                is_dimen_prop = any(x in prop_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap", "shadow", "elevation", "horizontal", "vertical"])
                                                
                                                # SIMPLIFIED: Check if this is ANY padding property (padding, horizontalPadding, verticalPadding, paddingTop, etc.)
                                                is_padding_prop = "padding" in prop_key_lower
                                                
                                                # Build full name for nested variant
                                                full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_sub_variant_name}_{safe_prop_key}"
                                                
                                                # SIMPLIFIED: For padding properties, ALWAYS try to convert to number and write as dimen
                                                if is_padding_prop:
                                                    padding_numeric = None
                                                    if isinstance(resolved_value, (int, float)):
                                                        padding_numeric = resolved_value
                                                    elif isinstance(resolved_value, str):
                                                        # If it's still a reference, try to resolve it one more time
                                                        if resolved_value.startswith("{") and resolved_value.endswith("}"):
                                                            further_resolved = self.resolve_reference(resolved_value)
                                                            if further_resolved != resolved_value:
                                                                resolved_value = further_resolved
                                                        
                                                        # Remove units and try to convert
                                                        numeric_str = resolved_value.replace("px", "").replace("dp", "").replace("%", "").strip()
                                                        if numeric_str:
                                                            try:
                                                                padding_numeric = float(numeric_str) if '.' in numeric_str else int(numeric_str)
                                                            except (ValueError, TypeError):
                                                                pass
                                                    
                                                    if padding_numeric is not None:
                                                        xml += f'    <dimen name="{full_name}">{padding_numeric}dp</dimen>\n'
                                                    else:
                                                        xml += f'    <string name="{full_name}">{str(resolved_value)}</string>\n'
                                                    continue  # Skip the rest of the logic for padding properties
                                                
                                                # Try to convert string to number if it looks numeric
                                                numeric_value = None
                                                if isinstance(resolved_value, str):
                                                    try:
                                                        # Remove units for numeric conversion
                                                        numeric_str = resolved_value.replace("px", "").replace("dp", "").replace("%", "").strip()
                                                        if numeric_str:
                                                            numeric_value = float(numeric_str) if '.' in numeric_str else int(numeric_str)
                                                    except ValueError:
                                                        pass
                                                
                                                # Check if resolved_value is a dict-like string that needs parsing
                                                parsed_dict = self._parse_dict_like_string(resolved_value) if isinstance(resolved_value, str) else None
                                                if parsed_dict:
                                                    # Extract properties from the parsed dict
                                                    for dict_key, dict_value in sorted(parsed_dict.items()):
                                                        safe_dict_key = self._to_snake_case(dict_key)
                                                        dict_full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_sub_variant_name}_{safe_prop_key}_{safe_dict_key}"
                                                        
                                                        # Resolve the dict value if it's a reference
                                                        if isinstance(dict_value, str):
                                                            dict_resolved = self.resolve_reference(dict_value)
                                                        else:
                                                            dict_resolved = dict_value
                                                        
                                                        # Determine resource type
                                                        dict_key_lower = dict_key.lower()
                                                        is_dict_color = any(x in dict_key_lower for x in ["color", "fill", "background"])
                                                        is_dict_dimen = any(x in dict_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap", "horizontal", "vertical", "x", "y", "blur", "spread"])
                                                        
                                                        # Try to convert to number (handle units like "px", "dp")
                                                        dict_numeric = None
                                                        if isinstance(dict_resolved, str):
                                                            try:
                                                                numeric_str = dict_resolved.replace("px", "").replace("dp", "").replace("%", "").strip()
                                                                if numeric_str:
                                                                    dict_numeric = float(numeric_str) if '.' in numeric_str else int(numeric_str)
                                                            except ValueError:
                                                                pass
                                                        
                                                        # Generate XML resource
                                                        if isinstance(dict_resolved, str):
                                                            if dict_resolved.startswith("#"):
                                                                xml += f'    <color name="{dict_full_name}">{dict_resolved}</color>\n'
                                                            elif dict_numeric is not None and is_dict_dimen:
                                                                xml += f'    <dimen name="{dict_full_name}">{dict_numeric}dp</dimen>\n'
                                                            elif dict_resolved.startswith("@"):
                                                                xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                                            else:
                                                                xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                                        elif isinstance(dict_resolved, (int, float)):
                                                            if is_dict_dimen:
                                                                xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                                            else:
                                                                xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                                        else:
                                                            xml += f'    <string name="{dict_full_name}">{str(dict_resolved)}</string>\n'
                                                # Generate appropriate XML resource based on value type and property name
                                                # Skip writing the full dict if we already extracted its properties
                                                if parsed_dict:
                                                    # Already extracted dict properties, skip writing the full dict
                                                    pass
                                                elif isinstance(resolved_value, str):
                                                    if resolved_value.startswith("#"):
                                                        xml += f'    <color name="{full_name}">{resolved_value}</color>\n'
                                                    elif numeric_value is not None and is_dimen_prop:
                                                        xml += f'    <dimen name="{full_name}">{numeric_value}dp</dimen>\n'
                                                    elif resolved_value.startswith("@"):
                                                        xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                                    else:
                                                        xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                                elif isinstance(resolved_value, (int, float)):
                                                    if is_dimen_prop:
                                                        xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                                    elif is_color_prop:
                                                        xml += f'    <color name="{full_name}">#{int(resolved_value):06x}</color>\n'
                                                    else:
                                                        xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                                elif isinstance(resolved_value, dict):
                                                    # Dict objects should have been handled above by extracting properties
                                                    # Only write as string if it wasn't parsed (shouldn't happen, but safety check)
                                                    if not parsed_dict:
                                                        # This shouldn't happen, but if it does, skip writing invalid dict syntax
                                                        pass
                                                else:
                                                    xml += f'    <string name="{full_name}">{str(resolved_value)}</string>\n'
                            continue  # Skip the main loop for nested variants
                        
                        # Main loop for single-level variants
                        for property_name, property_def in sorted(variant_def.items()):
                            # Sanitize names: replace hyphens with underscores for valid Android resource names
                            safe_component_name = self._to_snake_case(component_name)
                            safe_variant_name = self._to_snake_case(variant_name)
                            safe_property_name = self._to_snake_case(property_name)
                            
                                # Skip type properties (they're just metadata, not needed in Android XML)
                            if property_name.endswith("_type") or property_name == "type":
                                continue
                            
                            # Skip component identifier strings (redundant - resource name already identifies it)
                            # These are generated when JSON-like structures are converted to simple identifiers
                            if isinstance(property_def, str) and not isinstance(property_def, dict):
                                # Check if it's just a duplicate identifier (e.g., "button_primary_default")
                                if property_def == f"{safe_component_name}_{safe_variant_name}" or property_def == f"{safe_component_name}_{safe_variant_name}_{safe_property_name}":
                                    continue
                            
                            # Handle composition tokens: 
                            # 1. When property_name is "value" and property_def is a dict of properties
                            # 2. When property_def is a dict with "value" and "type" keys (nested variant like button.danger.active)
                            if isinstance(property_def, dict) and "value" in property_def and isinstance(property_def["value"], dict):
                                # Extract the actual value dict
                                value_dict = property_def["value"]
                                # Extract each property from the composition
                                # e.g., card.default.value = {fill: "...", padding: "...", borderRadius: "..."}
                                # or button.danger.active.value = {fill: "..."}
                                for prop_key, prop_value in sorted(value_dict.items()):
                                    safe_prop_key = self._to_snake_case(prop_key)
                                    # For nested variants (like button.danger.active), include the variant name in the resource name
                                    if property_name != "value":
                                        # This is a nested variant (e.g., "active" in button.danger.active)
                                        full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_property_name}_{safe_prop_key}"
                                    else:
                                        # This is a direct value property
                                        full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_prop_key}"
                                    
                                    # Resolve the property value if it's a reference
                                    if isinstance(prop_value, str):
                                        resolved_value = self.resolve_reference(prop_value)
                                    else:
                                        resolved_value = prop_value
                                    
                                    # Determine resource type based on property name and value
                                    prop_key_lower = prop_key.lower()
                                    is_color_prop = any(x in prop_key_lower for x in ["color", "fill", "background"])
                                    is_dimen_prop = any(x in prop_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap", "shadow", "elevation", "horizontal", "vertical"])
                                    
                                    # SIMPLIFIED: Check if this is ANY padding property (padding, horizontalPadding, verticalPadding, paddingTop, etc.)
                                    is_padding_prop = "padding" in prop_key_lower
                                    
                                    # SIMPLIFIED: For padding properties, ALWAYS try to convert to number and write as dimen
                                    if is_padding_prop:
                                        padding_numeric = None
                                        if isinstance(resolved_value, (int, float)):
                                            padding_numeric = resolved_value
                                        elif isinstance(resolved_value, str):
                                            # If it's still a reference, try to resolve it one more time
                                            if resolved_value.startswith("{") and resolved_value.endswith("}"):
                                                further_resolved = self.resolve_reference(resolved_value)
                                                if further_resolved != resolved_value:
                                                    resolved_value = further_resolved
                                            
                                            # Remove units and try to convert
                                            numeric_str = resolved_value.replace("px", "").replace("dp", "").replace("%", "").strip()
                                            if numeric_str:
                                                try:
                                                    padding_numeric = float(numeric_str) if '.' in numeric_str else int(numeric_str)
                                                except (ValueError, TypeError):
                                                    pass
                                        
                                        if padding_numeric is not None:
                                            xml += f'    <dimen name="{full_name}">{padding_numeric}dp</dimen>\n'
                                        else:
                                            xml += f'    <string name="{full_name}">{str(resolved_value)}</string>\n'
                                    else:
                                        # Try to convert string to number if it looks numeric
                                        numeric_value = None
                                        if isinstance(resolved_value, str):
                                            try:
                                                numeric_str = resolved_value.replace("px", "").replace("dp", "").replace("%", "").strip()
                                                if numeric_str:
                                                    numeric_value = float(numeric_str) if '.' in numeric_str else int(numeric_str)
                                            except ValueError:
                                                pass
                                        
                                        # Check if resolved_value is a dict-like string that needs parsing, or an actual dict object
                                        parsed_dict = None
                                        if isinstance(resolved_value, str):
                                            parsed_dict = self._parse_dict_like_string(resolved_value)
                                        elif isinstance(resolved_value, dict):
                                            parsed_dict = resolved_value
                                        if parsed_dict:
                                            # Extract properties from the parsed dict
                                            for dict_key, dict_value in sorted(parsed_dict.items()):
                                                safe_dict_key = self._to_snake_case(dict_key)
                                                dict_full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_prop_key}_{safe_dict_key}"
                                                
                                                # Resolve the dict value if it's a reference
                                                if isinstance(dict_value, str):
                                                    dict_resolved = self.resolve_reference(dict_value)
                                                else:
                                                    dict_resolved = dict_value
                                                
                                                # Determine resource type
                                                dict_key_lower = dict_key.lower()
                                                is_dict_color = any(x in dict_key_lower for x in ["color", "fill", "background"])
                                                is_dict_dimen = any(x in dict_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap", "horizontal", "vertical", "x", "y", "blur", "spread"])
                                                
                                                # Try to convert to number
                                                dict_numeric = None
                                                if isinstance(dict_resolved, str):
                                                    try:
                                                        dict_numeric = float(dict_resolved) if '.' in dict_resolved else int(dict_resolved)
                                                    except ValueError:
                                                        pass
                                                
                                                # Generate XML resource
                                                if isinstance(dict_resolved, str):
                                                    if dict_resolved.startswith("#"):
                                                        xml += f'    <color name="{dict_full_name}">{dict_resolved}</color>\n'
                                                    elif dict_numeric is not None and is_dict_dimen:
                                                        xml += f'    <dimen name="{dict_full_name}">{dict_numeric}dp</dimen>\n'
                                                    elif dict_resolved.startswith("@"):
                                                        xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                                    else:
                                                        xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                                elif isinstance(dict_resolved, (int, float)):
                                                    if is_dict_dimen:
                                                        xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                                    else:
                                                        xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                                else:
                                                    xml += f'    <string name="{dict_full_name}">{str(dict_resolved)}</string>\n'
                                        # Generate appropriate XML resource based on value type and property name
                                        # Skip writing the full dict if we already extracted its properties
                                        if parsed_dict:
                                            # Already extracted dict properties, skip writing the full dict
                                            pass
                                        elif isinstance(resolved_value, str):
                                            if resolved_value.startswith("#"):
                                                xml += f'    <color name="{full_name}">{resolved_value}</color>\n'
                                            elif numeric_value is not None and is_dimen_prop:
                                                xml += f'    <dimen name="{full_name}">{numeric_value}dp</dimen>\n'
                                            elif resolved_value.startswith("@"):
                                                xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                            else:
                                                xml += f'    <string name="{full_name}">{resolved_value}</string>\n'
                                        elif isinstance(resolved_value, (int, float)):
                                            if is_dimen_prop:
                                                xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                            elif is_color_prop:
                                                xml += f'    <color name="{full_name}">#{int(resolved_value):06x}</color>\n'
                                            else:
                                                xml += f'    <dimen name="{full_name}">{resolved_value}dp</dimen>\n'
                                        elif isinstance(resolved_value, dict):
                                            # Dict objects should have been handled above by extracting properties
                                            # Only write as string if it wasn't parsed (shouldn't happen, but safety check)
                                            if not parsed_dict:
                                                # This shouldn't happen, but if it does, skip writing invalid dict syntax
                                                pass
                                        else:
                                            xml += f'    <string name="{full_name}">{str(resolved_value)}</string>\n'
                            elif isinstance(property_def, dict) and "value" in property_def:
                                # Handle nested structure where property_def has a "value" key
                                value = property_def["value"]
                                full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_property_name}"
                                
                                # Resolve value if it's a string with references
                                if isinstance(value, str):
                                    value = self.resolve_reference(value)
                                
                                # Check if value is a dict-like string that needs parsing
                                parsed_dict = self._parse_dict_like_string(value) if isinstance(value, str) else None
                                if parsed_dict:
                                    # Extract properties from the parsed dict
                                    for dict_key, dict_value in sorted(parsed_dict.items()):
                                        safe_dict_key = self._to_snake_case(dict_key)
                                        dict_full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_property_name}_{safe_dict_key}"
                                        
                                        # Resolve the dict value if it's a reference
                                        if isinstance(dict_value, str):
                                            dict_resolved = self.resolve_reference(dict_value)
                                        else:
                                            dict_resolved = dict_value
                                        
                                        # Determine resource type
                                        dict_key_lower = dict_key.lower()
                                        is_dict_color = any(x in dict_key_lower for x in ["color", "fill", "background"])
                                        is_dict_dimen = any(x in dict_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap"])
                                        
                                        # Try to convert to number
                                        dict_numeric = None
                                        if isinstance(dict_resolved, str):
                                            try:
                                                if '.' in dict_resolved:
                                                    dict_numeric = float(dict_resolved)
                                                else:
                                                    dict_numeric = int(dict_resolved)
                                            except ValueError:
                                                pass
                                        
                                        # Generate XML resource
                                        if isinstance(dict_resolved, str):
                                            if dict_resolved.startswith("#"):
                                                xml += f'    <color name="{dict_full_name}">{dict_resolved}</color>\n'
                                            elif dict_numeric is not None and is_dict_dimen:
                                                xml += f'    <dimen name="{dict_full_name}">{dict_numeric}dp</dimen>\n'
                                            elif dict_resolved.startswith("@"):
                                                xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                            else:
                                                xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                        elif isinstance(dict_resolved, (int, float)):
                                            if is_dict_dimen:
                                                xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                            else:
                                                xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                        else:
                                            xml += f'    <string name="{dict_full_name}">{str(dict_resolved)}</string>\n'
                                # Generate appropriate XML resource
                                elif isinstance(value, str):
                                    if value.startswith("#"):
                                        xml += f'    <color name="{full_name}">{value}</color>\n'
                                    else:
                                        xml += f'    <string name="{full_name}">{value}</string>\n'
                                elif isinstance(value, (int, float)):
                                    xml += f'    <dimen name="{full_name}">{value}dp</dimen>\n'
                                else:
                                    xml += f'    <string name="{full_name}">{str(value)}</string>\n'
                            elif isinstance(property_def, str):
                                # Direct string value without "value" key
                                # Sanitize names: replace hyphens with underscores for valid Android resource names
                                safe_component_name = self._to_snake_case(component_name)
                                safe_variant_name = self._to_snake_case(variant_name)
                                safe_property_name = self._to_snake_case(property_name)
                                full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_property_name}"
                                # Check if property_def is a dict-like string that needs parsing
                                parsed_dict = self._parse_dict_like_string(property_def)
                                if parsed_dict:
                                    # Extract properties from the parsed dict
                                    for dict_key, dict_value in sorted(parsed_dict.items()):
                                        safe_dict_key = self._to_snake_case(dict_key)
                                        dict_full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_property_name}_{safe_dict_key}"
                                        
                                        # Resolve the dict value if it's a reference
                                        if isinstance(dict_value, str):
                                            dict_resolved = self.resolve_reference(dict_value)
                                        else:
                                            dict_resolved = dict_value
                                        
                                        # Determine resource type
                                        dict_key_lower = dict_key.lower()
                                        is_dict_color = any(x in dict_key_lower for x in ["color", "fill", "background"])
                                        is_dict_dimen = any(x in dict_key_lower for x in ["padding", "margin", "radius", "width", "height", "size", "spacing", "gap"])
                                        
                                        # Try to convert to number
                                        dict_numeric = None
                                        if isinstance(dict_resolved, str):
                                            try:
                                                if '.' in dict_resolved:
                                                    dict_numeric = float(dict_resolved)
                                                else:
                                                    dict_numeric = int(dict_resolved)
                                            except ValueError:
                                                pass
                                        
                                        # Generate XML resource
                                        if isinstance(dict_resolved, str):
                                            if dict_resolved.startswith("#"):
                                                xml += f'    <color name="{dict_full_name}">{dict_resolved}</color>\n'
                                            elif dict_numeric is not None and is_dict_dimen:
                                                xml += f'    <dimen name="{dict_full_name}">{dict_numeric}dp</dimen>\n'
                                            elif dict_resolved.startswith("@"):
                                                xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                            else:
                                                xml += f'    <string name="{dict_full_name}">{dict_resolved}</string>\n'
                                        elif isinstance(dict_resolved, (int, float)):
                                            if is_dict_dimen:
                                                xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                            else:
                                                xml += f'    <dimen name="{dict_full_name}">{dict_resolved}dp</dimen>\n'
                                        else:
                                            xml += f'    <string name="{dict_full_name}">{str(dict_resolved)}</string>\n'
                                    continue
                                # Only output if it's a meaningful string value (not just an identifier)
                                # Skip if it's just repeating the component/variant name
                                if property_def != f"{safe_component_name}_{safe_variant_name}" and property_def != f"{safe_component_name}_{safe_variant_name}_{safe_property_name}":
                                    xml += f'    <string name="{full_name}">{property_def}</string>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    # ===== UTILITY METHODS =====

    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase/mixed to snake_case, replacing hyphens with underscores for valid Android resource names."""
        # First replace hyphens with underscores (Android resource names cannot contain hyphens)
        name = name.replace('-', '_')
        # Then convert camelCase to snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        # Android resource names must start with a letter, not a number
        if result and result[0].isdigit():
            result = f"spacing_{result}"
        return result

    # ===== MAIN EXECUTION =====

    def _cleanup_root_files(self):
        """Clean up old root-level token files when using --modes."""
        # XML root files to remove
        xml_root_files = [
            "colors.xml", "dimens.xml", "radius.xml", "typography.xml",
            "attrs.xml", "animations.xml", "interactions.xml", "components.xml",
            "elevation.xml", "assets.xml", "layout.xml", "platforms.xml"
        ]
        
        # Remove XML root files
        for filename in xml_root_files:
            filepath = self.xml_output_path / filename
            if filepath.exists():
                filepath.unlink()
                self.log(f"  Removed old root file: {filename}", "info")

    def generate_all_outputs(self, export_modes: bool = True):
        """
        Generate all XML output files.
        
        Args:
            export_modes: If True, export separate files for each brand/theme combination.
                          If False, export only the default combination.
        """
        if export_modes:
            # Clean up old root-level files when using --modes
            self._cleanup_root_files()
            
            # Export all brand/theme combinations
            brands = ["Default", "Performance", "Luxury"]
            themes = ["Day", "Night"]
            
            self.log("="*60, "info")
            self.log("EXPORTING ALL MODE COMBINATIONS", "info")
            self.log("="*60, "info")
            
            for brand in brands:
                for theme in themes:
                    self.log(f"\n📦 Exporting: Brand={brand}, Theme={theme}", "info")
                    self.token_data = {}  # Reset for each combination
                    self.resolved_cache = {}
                    self.unresolved_refs = set()
                    
                    # Load tokens for this combination
                    self.load_all_tokens(brand=brand, theme=theme)
                    all_tokens = self.extract_all_tokens()
                    
                    # Generate outputs with mode suffix
                    mode_suffix = f"{brand.lower()}_{theme.lower()}"
                    self._generate_xml_outputs(all_tokens, mode_suffix=mode_suffix)
            
            self.log("\n✅ All mode combinations exported successfully!", "success")
        else:
            # Export only default combination
            self.load_all_tokens(brand="Default", theme="Day")
            all_tokens = self.extract_all_tokens()
            
            self.log("Generating XML outputs...", "info")
            self._generate_xml_outputs(all_tokens)
            
            self.log("✅ All outputs generated successfully!", "success")
            self._print_summary(all_tokens)

    def _generate_xml_outputs(self, tokens: Dict[str, Any], mode_suffix: str = None):
        """Generate all XML files."""
        outputs = {
            "colors.xml": self.generate_xml_colors(tokens["colors"]),
            "dimens.xml": self.generate_xml_dimens(tokens["spacing"], tokens.get("border_width")),
            "radius.xml": self.generate_xml_radius(tokens["radius"]),
            "typography.xml": self.generate_xml_typography_unified(tokens["typography"], tokens.get("letter_spacing"), tokens.get("text_case")),
            "attrs.xml": self.generate_xml_attrs(tokens["accessibility"]),
            "animations.xml": self.generate_xml_animations(tokens["motion"]),
            "interactions.xml": self.generate_xml_interactions(tokens["interactions"], colors=tokens["colors"]),
            "components.xml": self.generate_xml_components(tokens["components"]),
            "elevation.xml": self.generate_xml_elevation(tokens["elevation"]),
        }
        
        # Add optional token files if they have content
        if tokens.get("assets"):
            outputs["assets.xml"] = self.generate_xml_assets(tokens["assets"])
        if tokens.get("layout"):
            outputs["layout.xml"] = self.generate_xml_layout(tokens["layout"])
        if tokens.get("platforms"):
            outputs["platforms.xml"] = self.generate_xml_platforms(tokens["platforms"])
        
        # Create mode-specific subdirectory if exporting modes
        output_path = self.xml_output_path
        if mode_suffix:
            output_path = self.xml_output_path / mode_suffix
            output_path.mkdir(parents=True, exist_ok=True)
        
        for filename, content in outputs.items():
            filepath = output_path / filename
            with open(filepath, 'w') as f:
                f.write(content)
            self.log(f"  Generated {filepath.relative_to(self.xml_output_path.parent)}", "success")

    def _print_summary(self, tokens: Dict[str, Any], mode_suffix: str = None):
        """Print generation summary."""
        mode_info = f" (Mode: {mode_suffix})" if mode_suffix else ""
        print("\n" + "="*60)
        print(f"FULL COVERAGE TOKEN TRANSFORMATION COMPLETE{mode_info}")
        print("="*60)
        print(f"\n📁 XML outputs: {self.xml_output_path}")
        print(f"   ├─ colors.xml ({len(tokens['colors'])} colors)")
        print(f"   ├─ dimens.xml ({len(tokens['spacing'])} spacing values)")
        print(f"   ├─ typography.xml ({sum(len(v) for v in tokens['typography'].values())} typography values)")
        print(f"   ├─ radius.xml ({len(tokens['radius'])} radius values)")
        print(f"   ├─ attrs.xml ({len(tokens['accessibility'])} accessibility values)")
        print(f"   ├─ animations.xml ({len(tokens.get('motion', {}))} motion groups)")
        print(f"   ├─ interactions.xml ({len(tokens.get('interactions', {}))} state groups)")
        print(f"   └─ components.xml ({len(tokens.get('components', {}))} component groups)")
        
        total_tokens = (
            len(tokens['colors']) +
            len(tokens['spacing']) +
            sum(len(v) for v in tokens['typography'].values()) +
            len(tokens.get('elevation', {})) +
            len(tokens.get('motion', {})) +
            len(tokens['accessibility'])
        )
        
        print(f"\n✅ TOTAL TOKENS TRANSFORMED: {total_tokens}+")
        print(f"   ✓ Base tokens loaded")
        print(f"   ✓ Brand and theme tokens loaded")
        print(f"   ✓ All token types extracted")
        print(f"   ✓ XML outputs generated")
        print("="*60 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 token_transformer_full_coverage.py /path/to/workspace [--modes]")
        print("  --modes: Export separate files for each brand/theme combination")
        sys.exit(1)
    
    base_path = sys.argv[1]
    export_modes = "--modes" in sys.argv
    
    config = TransformerConfig(base_path=base_path, verbose=True)
    transformer = FullCoverageTransformer(config)
    transformer.generate_all_outputs(export_modes=export_modes)


if __name__ == "__main__":
    main()

