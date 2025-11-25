package com.example.vehiclecomponents

import android.os.Bundle
import android.view.View
import android.widget.FrameLayout
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Set progress bar to 65%
        val progressBarFill = findViewById<View>(R.id.progressBarFill)
        val progressBarContainer = findViewById<FrameLayout>(R.id.progressBarContainer)
        
        val progress = 0.65f // 65%
        
        // Use post to get width after layout is complete
        progressBarContainer.post {
            val containerWidth = progressBarContainer.width
            val padding = resources.getDimensionPixelSize(R.dimen.spacing_4) * 2 // left + right padding
            val availableWidth = containerWidth - padding
            val fillWidth = (availableWidth * progress).toInt()
            
            val layoutParams = progressBarFill.layoutParams
            layoutParams.width = fillWidth
            progressBarFill.layoutParams = layoutParams
        }
    }
}

