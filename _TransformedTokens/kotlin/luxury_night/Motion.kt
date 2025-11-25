package com.example.hmithemedemo.ui.theme.luxury_night

object MotionTokens {
    // Durations (milliseconds)
    val durationshort = 100
    val durationmedium = 200
    val durationlong = 300
    val durationfast = 150
    val durationstandard = 300
    val durationslow = 500

    // Easing Functions
    val easingstandard = "cubic-bezier(0.4, 0.0, 0.2, 1)"
    val easingdecelerate = "cubic-bezier(0.0, 0.0, 0.2, 1)"
    val easingaccelerate = "cubic-bezier(0.4, 0.0, 1, 1)"
    val easingdefault = "cubic-bezier(0.25, 0.46, 0.45, 0.94)"
    val easingentrance = "cubic-bezier(0.34, 1.56, 0.64, 1)"
    val easingexit = "cubic-bezier(0.66, 0, 0.66, 0.07)"
    val easingsmooth = "cubic-bezier(0.4, 0, 0.2, 1)"
    val easingsharp = "cubic-bezier(0.4, 0, 0.6, 1)"

    // Transitions (combined duration + easing)
    val transitionfastSmooth = "{motion.duration.fast} {motion.easing.smooth}"
    val transitionstandardSmooth = "{motion.duration.standard} {motion.easing.default}"
    val transitionslowSmooth = "{motion.duration.slow} {motion.easing.default}"
    val transitionentranceEmphasis = "{motion.duration.standard} {motion.easing.entrance}"
    val transitionexitEmphasis = "{motion.duration.fast} {motion.easing.exit}"
}
