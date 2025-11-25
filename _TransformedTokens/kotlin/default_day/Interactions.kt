package com.example.hmithemedemo.ui.theme.default_day

import androidx.compose.ui.graphics.Color

object InteractionTokens {

    // Active State
    object Active {
        val colordelta = -4
        val opacity = 0.76
    }

    // Disabled State
    object Disabled {
        val colordelta = 1
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
        val backgroundcolor = "{color.red.red-10}"
        val bordercolor = "{color.red.red-100}"
        val color = "{color.functional.warning}"
        val textcolor = "{color.red.red-100}"
    }

    // Focus State
    object Focus {
        val outline = "{borderWidth.2} solid {interaction.focus.ringColor}"
        val ringcolor = "{color.active-dark-primary}"
        val ringoffset = 2
        val ringwidth = 2
    }

    // Hover State
    object Hover {
        val colordelta = -2
        val opacity = 0.88
    }

    // Loading State
    object Loading {
        val cursor = "wait"
        val opacity = 0.6
    }

    // Readonly State
    object Readonly {
        val backgroundcolor = "{color.blacks.black-10}"
        val cursor = "default"
        val opacity = 0.6
        val textcolor = "{color.blacks.black-60-inactive}"
    }

    // Selected State
    object Selected {
        val backgroundcolor = "{color.active.active-light-secondary}"
        val bordercolor = "{color.active.active-light-primary}"
        val textcolor = "{color.active.active-dark-primary}"
    }

    // Success State
    object Success {
        val backgroundcolor = "{color.green.green-10}"
        val bordercolor = "{color.green.green-80}"
        val color = "{color.functional.positive}"
        val textcolor = "{color.green.green-80}"
    }

    // Warning State
    object Warning {
        val backgroundcolor = "{color.amber.amber-10}"
        val bordercolor = "{color.amber.amber-80}"
        val color = "{color.functional.caution}"
        val textcolor = "{color.amber.amber-80}"
    }
}
