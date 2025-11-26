package com.example.vehicleosdemo

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide

data class ComponentData(
    val title: String,
    val label: String,
    val value: String,
    val progress: Float,
    val replacementText: String
)

class ComponentCardAdapter(
    private val components: List<ComponentData>
) : RecyclerView.Adapter<ComponentCardAdapter.ComponentViewHolder>() {

    class ComponentViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val titleText = itemView.findViewById<TextView>(R.id.tiresHeading)
        private val labelText = itemView.findViewById<TextView>(R.id.labelText)
        private val valueText = itemView.findViewById<TextView>(R.id.valueText)
        private val replacementText = itemView.findViewById<TextView>(R.id.replacementText)
        private val progressBarFill = itemView.findViewById<View>(R.id.progressBarFill)
        private val progressBarContainer = itemView.findViewById<FrameLayout>(R.id.progressBarContainer)
        private val productImage = itemView.findViewById<ImageView>(R.id.productImage)
        
        fun bind(component: ComponentData) {
            // Set text values
            titleText.text = component.title
            labelText.text = component.label
            valueText.text = component.value
            replacementText.text = component.replacementText
            
            // Load product image from asset token
            val productImageUrl = itemView.context.getString(R.string.asset_product_image)
            Glide.with(itemView.context)
                .load(productImageUrl)
                .centerCrop()
                .into(productImage)
            
            // Set progress bar
            val progress = component.progress
            
            // Use post to get width after layout is complete
            progressBarContainer.post {
                val containerWidth = progressBarContainer.width
                val padding = itemView.resources.getDimensionPixelSize(R.dimen.spacing_xs) * 2 // left + right padding
                val availableWidth = containerWidth - padding
                val fillWidth = (availableWidth * progress).toInt()
                
                val layoutParams = progressBarFill.layoutParams
                layoutParams.width = fillWidth
                progressBarFill.layoutParams = layoutParams
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ComponentViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_component_card, parent, false)
        return ComponentViewHolder(view)
    }

    override fun onBindViewHolder(holder: ComponentViewHolder, position: Int) {
        holder.bind(components[position])
    }

    override fun getItemCount(): Int = components.size
}

