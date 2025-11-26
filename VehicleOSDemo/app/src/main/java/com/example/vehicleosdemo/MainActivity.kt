package com.example.vehicleosdemo

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.componentsRecyclerView)
        
        // Create sample component data
        val components = listOf(
            ComponentData(
                title = "Tires",
                label = "Low Tire Pressure",
                value = "65%",
                progress = 0.65f,
                replacementText = "Replacement Due: 5,000 mi"
            ),
            ComponentData(
                title = "Brakes",
                label = "Brake Pad Wear",
                value = "45%",
                progress = 0.45f,
                replacementText = "Replacement Due: 8,000 mi"
            ),
            ComponentData(
                title = "Oil",
                label = "Oil Life",
                value = "30%",
                progress = 0.30f,
                replacementText = "Replacement Due: 2,000 mi"
            ),
            ComponentData(
                title = "Battery",
                label = "Battery Health",
                value = "85%",
                progress = 0.85f,
                replacementText = "Replacement Due: 15,000 mi"
            ),
            ComponentData(
                title = "Engine",
                label = "Engine Status",
                value = "92%",
                progress = 0.92f,
                replacementText = "Replacement Due: 20,000 mi"
            ),
            ComponentData(
                title = "Transmission",
                label = "Transmission Fluid",
                value = "70%",
                progress = 0.70f,
                replacementText = "Replacement Due: 10,000 mi"
            )
        )
        
        // Create adapter
        val adapter = ComponentCardAdapter(components)
        recyclerView.adapter = adapter
        
        // Set up GridLayoutManager with 2 columns and spacing token
        val gridLayoutManager = GridLayoutManager(this, 2)
        recyclerView.layoutManager = gridLayoutManager
        
        // Add spacing between grid items using brand spacing token
        val spacing = resources.getDimensionPixelSize(R.dimen.spacing_md)
        recyclerView.addItemDecoration(
            GridSpacingItemDecoration(
                spanCount = 2,
                spacing = spacing,
                includeEdge = true
            )
        )
    }
}

