package com.example.hmithemedemo.ui.theme

import androidx.compose.ui.graphics.Color

object InteractionTokens {

    // Active State
    object Active {
        val border-style = "solid"
        val color-modifier = "darken-20%"
        val opacity = 1.0
        val transition = "{motion.transition.fast-smooth}"
    }

    // Disabled State
    object Disabled {
        val color-modifier = "desaturate-50%"
        val cursor = "not-allowed"
        val opacity = 0.5
    }

    // Dragging State
    object Dragging {
        val boxshadow = "0 8px 16px rgba(0, 0, 0, 0.2)"
        val cursor = "grabbing"
        val opacity = 0.75
    }

    // Error State
    object Error {
        val backgroundcolor = "{color.red-10}"
        val bordercolor = "{color.red-100}"
        val color = "{color.functional-warning}"
        val textcolor = "{color.red-100}"
    }

    // Focus State
    object Focus {
        val outline = "2px solid {accessibility.focus-indicator}"
        val outline-offset = "2px"
        val outline-width = "2px"
    }

    // Hover State
    object Hover {
        val color-modifier = "darken-10%"
        val cursor = "pointer"
        val opacity = 0.88
        val transition = "{motion.transition.fast-smooth}"
    }

    // Loading State
    object Loading {
        val cursor = "wait"
        val opacity = 0.6
    }

    // Readonly State
    object Readonly {
        val backgroundcolor = "{color.black-10}"
        val cursor = "default"
        val opacity = 0.6
        val textcolor = "{color.black-60-inactive}"
    }

    // Selected State
    object Selected {
        val backgroundcolor = "{color.active-light-secondary}"
        val bordercolor = "{color.active-light-primary}"
        val textcolor = "{color.active-dark-primary}"
    }

    // Success State
    object Success {
        val backgroundcolor = "{color.green-10}"
        val bordercolor = "{color.green-80}"
        val color = "{color.functional-positive}"
        val textcolor = "{color.green-80}"
    }

    // Warning State
    object Warning {
        val backgroundcolor = "{color.amber-10}"
        val bordercolor = "{color.amber-80}"
        val color = "{color.functional-caution}"
        val textcolor = "{color.amber-80}"
    }
}
