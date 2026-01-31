# SleepFM Wear OS ProGuard Rules

# Keep Hilt classes
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }
-keep class * extends dagger.hilt.android.internal.managers.ComponentSupplier { *; }
-keep class * extends dagger.hilt.android.internal.managers.ViewComponentManager$FragmentContextWrapper { *; }

# Keep model classes for Gson serialization
-keep class io.sleepfm.wear.data.model.** { *; }

# Keep Health Services classes
-keep class androidx.health.services.client.** { *; }

# Keep Wear Tiles classes
-keep class androidx.wear.tiles.** { *; }
-keep class androidx.wear.protolayout.** { *; }

# Keep Watch Face Complications classes
-keep class androidx.wear.watchface.complications.** { *; }

# Keep Google Play Services Wearable
-keep class com.google.android.gms.wearable.** { *; }

# Keep Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# Keep Compose classes
-keep class androidx.compose.** { *; }

# General rules
-keepattributes *Annotation*
-keepattributes Signature
-keepattributes SourceFile,LineNumberTable

# Gson
-keep class com.google.gson.** { *; }
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer
