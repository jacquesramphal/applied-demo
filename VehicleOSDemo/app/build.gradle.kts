plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// Token sync configuration
val tokenBrandTheme: String = project.findProperty("token.brandTheme") as String? ?: "default_night"
val tokensSourceDir = rootProject.file("../_TransformedTokens/xml/$tokenBrandTheme")
val tokensDestDir = file("src/main/res/values")

android {
    namespace = "com.example.vehicleosdemo"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.vehicleosdemo"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // Core
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.cardview:cardview:1.0.0")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}

// Automatically sync token files from _TransformedTokens before every build
afterEvaluate {
    val syncTask = tasks.register("syncTokens") {
        group = "build"
        description = "Sync design token XML files from _TransformedTokens to app/src/main/res/values"
        
        // Always run this task (don't cache)
        outputs.upToDateWhen { false }
        
        doLast {
            if (tokensSourceDir.exists() && tokensSourceDir.isDirectory) {
                println("")
                println("🔄 Syncing tokens from: ${tokensSourceDir.absolutePath}")
                println("   Destination: ${tokensDestDir.absolutePath}")
                println("   Brand/Theme: $tokenBrandTheme")
                
                tokensSourceDir.listFiles { file -> file.extension == "xml" }?.forEach { file ->
                    file.copyTo(File(tokensDestDir, file.name), overwrite = true)
                }
                
                println("✓ Token files synced successfully")
                println("")
            } else {
                println("")
                println("⚠ Warning: Token source directory not found: ${tokensSourceDir.absolutePath}")
                println("⚠ Make sure to run: python3 _Scripts/token_transformer_full_coverage.py . --modes")
                println("")
            }
        }
    }
    
    // Automatically sync tokens before every build
    tasks.named("preBuild") {
        dependsOn(syncTask)
    }
}

