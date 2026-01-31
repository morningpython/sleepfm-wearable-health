package io.sleepfm.android

import android.app.Application
import dagger.hilt.android.HiltAndroidApp
import timber.log.Timber

/**
 * SleepFM Android Application
 * 
 * Main Application class with Hilt dependency injection setup.
 */
@HiltAndroidApp
class SleepFMApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        
        // Initialize Timber for logging
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
        
        Timber.d("SleepFM Application initialized")
    }
}
