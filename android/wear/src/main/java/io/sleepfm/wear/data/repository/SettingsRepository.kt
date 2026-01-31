package io.sleepfm.wear.data.repository

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.settingsDataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

@Singleton
class SettingsRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private object Keys {
        val AUTO_TRACKING_ENABLED = booleanPreferencesKey("auto_tracking_enabled")
        val AUTO_SYNC_ENABLED = booleanPreferencesKey("auto_sync_enabled")
        val HAPTIC_FEEDBACK_ENABLED = booleanPreferencesKey("haptic_feedback_enabled")
        val ALWAYS_ON_DISPLAY_ENABLED = booleanPreferencesKey("always_on_display_enabled")
        val HEART_RATE_INTERVAL_SECONDS = intPreferencesKey("heart_rate_interval_seconds")
        val SPO2_INTERVAL_MINUTES = intPreferencesKey("spo2_interval_minutes")
        val BEDTIME_REMINDER_ENABLED = booleanPreferencesKey("bedtime_reminder_enabled")
        val BEDTIME_HOUR = intPreferencesKey("bedtime_hour")
        val BEDTIME_MINUTE = intPreferencesKey("bedtime_minute")
        val WAKE_TIME_HOUR = intPreferencesKey("wake_time_hour")
        val WAKE_TIME_MINUTE = intPreferencesKey("wake_time_minute")
    }
    
    val autoTrackingEnabled: Flow<Boolean> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.AUTO_TRACKING_ENABLED] ?: false
    }
    
    val autoSyncEnabled: Flow<Boolean> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.AUTO_SYNC_ENABLED] ?: true
    }
    
    val hapticFeedbackEnabled: Flow<Boolean> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.HAPTIC_FEEDBACK_ENABLED] ?: true
    }
    
    val alwaysOnDisplayEnabled: Flow<Boolean> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.ALWAYS_ON_DISPLAY_ENABLED] ?: false
    }
    
    val heartRateIntervalSeconds: Flow<Int> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.HEART_RATE_INTERVAL_SECONDS] ?: 60
    }
    
    val spO2IntervalMinutes: Flow<Int> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.SPO2_INTERVAL_MINUTES] ?: 15
    }
    
    val bedtimeReminderEnabled: Flow<Boolean> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.BEDTIME_REMINDER_ENABLED] ?: false
    }
    
    val bedtimeHour: Flow<Int> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.BEDTIME_HOUR] ?: 23
    }
    
    val bedtimeMinute: Flow<Int> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.BEDTIME_MINUTE] ?: 0
    }
    
    val wakeTimeHour: Flow<Int> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.WAKE_TIME_HOUR] ?: 7
    }
    
    val wakeTimeMinute: Flow<Int> = context.settingsDataStore.data.map { prefs ->
        prefs[Keys.WAKE_TIME_MINUTE] ?: 0
    }
    
    val settings: Flow<WearSettings> = context.settingsDataStore.data.map { prefs ->
        WearSettings(
            autoTrackingEnabled = prefs[Keys.AUTO_TRACKING_ENABLED] ?: false,
            autoSyncEnabled = prefs[Keys.AUTO_SYNC_ENABLED] ?: true,
            hapticFeedbackEnabled = prefs[Keys.HAPTIC_FEEDBACK_ENABLED] ?: true,
            alwaysOnDisplayEnabled = prefs[Keys.ALWAYS_ON_DISPLAY_ENABLED] ?: false,
            heartRateIntervalSeconds = prefs[Keys.HEART_RATE_INTERVAL_SECONDS] ?: 60,
            spO2IntervalMinutes = prefs[Keys.SPO2_INTERVAL_MINUTES] ?: 15,
            bedtimeReminderEnabled = prefs[Keys.BEDTIME_REMINDER_ENABLED] ?: false,
            bedtimeHour = prefs[Keys.BEDTIME_HOUR] ?: 23,
            bedtimeMinute = prefs[Keys.BEDTIME_MINUTE] ?: 0,
            wakeTimeHour = prefs[Keys.WAKE_TIME_HOUR] ?: 7,
            wakeTimeMinute = prefs[Keys.WAKE_TIME_MINUTE] ?: 0
        )
    }
    
    suspend fun setAutoTrackingEnabled(enabled: Boolean) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.AUTO_TRACKING_ENABLED] = enabled
        }
    }
    
    suspend fun setAutoSyncEnabled(enabled: Boolean) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.AUTO_SYNC_ENABLED] = enabled
        }
    }
    
    suspend fun setHapticFeedbackEnabled(enabled: Boolean) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.HAPTIC_FEEDBACK_ENABLED] = enabled
        }
    }
    
    suspend fun setAlwaysOnDisplayEnabled(enabled: Boolean) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.ALWAYS_ON_DISPLAY_ENABLED] = enabled
        }
    }
    
    suspend fun setHeartRateInterval(seconds: Int) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.HEART_RATE_INTERVAL_SECONDS] = seconds
        }
    }
    
    suspend fun setSpO2Interval(minutes: Int) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.SPO2_INTERVAL_MINUTES] = minutes
        }
    }
    
    suspend fun setBedtimeReminder(enabled: Boolean, hour: Int? = null, minute: Int? = null) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.BEDTIME_REMINDER_ENABLED] = enabled
            hour?.let { prefs[Keys.BEDTIME_HOUR] = it }
            minute?.let { prefs[Keys.BEDTIME_MINUTE] = it }
        }
    }
    
    suspend fun setWakeTime(hour: Int, minute: Int) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.WAKE_TIME_HOUR] = hour
            prefs[Keys.WAKE_TIME_MINUTE] = minute
        }
    }
    
    data class WearSettings(
        val autoTrackingEnabled: Boolean,
        val autoSyncEnabled: Boolean,
        val hapticFeedbackEnabled: Boolean,
        val alwaysOnDisplayEnabled: Boolean,
        val heartRateIntervalSeconds: Int,
        val spO2IntervalMinutes: Int,
        val bedtimeReminderEnabled: Boolean,
        val bedtimeHour: Int,
        val bedtimeMinute: Int,
        val wakeTimeHour: Int,
        val wakeTimeMinute: Int
    )
}
