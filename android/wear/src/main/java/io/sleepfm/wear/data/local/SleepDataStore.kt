package io.sleepfm.wear.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import dagger.hilt.android.qualifiers.ApplicationContext
import io.sleepfm.wear.data.model.CollectedSleepData
import io.sleepfm.wear.data.model.SensorReading
import io.sleepfm.wear.data.model.SleepSession
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "sleep_data")

@Singleton
class SleepDataStore @Inject constructor(
    @ApplicationContext private val context: Context,
    private val gson: Gson
) {
    private object Keys {
        val IS_TRACKING = booleanPreferencesKey("is_tracking")
        val TRACKING_START_TIME = longPreferencesKey("tracking_start_time")
        val TRACKING_END_TIME = longPreferencesKey("tracking_end_time")
        val HEART_RATE_READINGS = stringPreferencesKey("heart_rate_readings")
        val SPO2_READINGS = stringPreferencesKey("spo2_readings")
        val LAST_SESSION = stringPreferencesKey("last_session")
        val LAST_SYNC_TIME = longPreferencesKey("last_sync_time")
    }
    
    val isTracking: Flow<Boolean> = context.dataStore.data.map { prefs ->
        prefs[Keys.IS_TRACKING] ?: false
    }
    
    val trackingStartTime: Flow<Long?> = context.dataStore.data.map { prefs ->
        prefs[Keys.TRACKING_START_TIME]
    }
    
    suspend fun setIsTracking(isTracking: Boolean) {
        context.dataStore.edit { prefs ->
            prefs[Keys.IS_TRACKING] = isTracking
        }
    }
    
    suspend fun setTrackingStartTime(time: Long) {
        context.dataStore.edit { prefs ->
            prefs[Keys.TRACKING_START_TIME] = time
        }
    }
    
    suspend fun setTrackingEndTime(time: Long) {
        context.dataStore.edit { prefs ->
            prefs[Keys.TRACKING_END_TIME] = time
        }
    }
    
    suspend fun saveHeartRateReadings(readings: List<SensorReading>) {
        context.dataStore.edit { prefs ->
            val existingJson = prefs[Keys.HEART_RATE_READINGS] ?: "[]"
            val existingReadings: List<SensorReading> = gson.fromJson(
                existingJson,
                object : TypeToken<List<SensorReading>>() {}.type
            )
            val combinedReadings = existingReadings + readings
            prefs[Keys.HEART_RATE_READINGS] = gson.toJson(combinedReadings)
        }
    }
    
    suspend fun saveSpO2Readings(readings: List<SensorReading>) {
        context.dataStore.edit { prefs ->
            val existingJson = prefs[Keys.SPO2_READINGS] ?: "[]"
            val existingReadings: List<SensorReading> = gson.fromJson(
                existingJson,
                object : TypeToken<List<SensorReading>>() {}.type
            )
            val combinedReadings = existingReadings + readings
            prefs[Keys.SPO2_READINGS] = gson.toJson(combinedReadings)
        }
    }
    
    suspend fun getCollectedSleepData(): CollectedSleepData {
        val prefs = context.dataStore.data.first()
        
        val startTime = prefs[Keys.TRACKING_START_TIME] ?: System.currentTimeMillis()
        val endTime = prefs[Keys.TRACKING_END_TIME] ?: System.currentTimeMillis()
        
        val heartRateJson = prefs[Keys.HEART_RATE_READINGS] ?: "[]"
        val heartRateReadings: List<SensorReading> = gson.fromJson(
            heartRateJson,
            object : TypeToken<List<SensorReading>>() {}.type
        )
        
        val spO2Json = prefs[Keys.SPO2_READINGS] ?: "[]"
        val spO2Readings: List<SensorReading> = gson.fromJson(
            spO2Json,
            object : TypeToken<List<SensorReading>>() {}.type
        )
        
        return CollectedSleepData(
            startTime = startTime,
            endTime = endTime,
            heartRateData = heartRateReadings,
            spO2Data = spO2Readings,
            accelerometerData = emptyList() // Accelerometer data not persisted for battery saving
        )
    }
    
    suspend fun clearTrackingData() {
        context.dataStore.edit { prefs ->
            prefs.remove(Keys.IS_TRACKING)
            prefs.remove(Keys.TRACKING_START_TIME)
            prefs.remove(Keys.TRACKING_END_TIME)
            prefs.remove(Keys.HEART_RATE_READINGS)
            prefs.remove(Keys.SPO2_READINGS)
        }
    }
    
    suspend fun saveLastSession(session: SleepSession) {
        context.dataStore.edit { prefs ->
            prefs[Keys.LAST_SESSION] = gson.toJson(session)
        }
    }
    
    suspend fun getLastSession(): SleepSession? {
        val prefs = context.dataStore.data.first()
        val json = prefs[Keys.LAST_SESSION] ?: return null
        return try {
            gson.fromJson(json, SleepSession::class.java)
        } catch (e: Exception) {
            null
        }
    }
    
    suspend fun setLastSyncTime(time: Long) {
        context.dataStore.edit { prefs ->
            prefs[Keys.LAST_SYNC_TIME] = time
        }
    }
    
    val lastSyncTime: Flow<Long?> = context.dataStore.data.map { prefs ->
        prefs[Keys.LAST_SYNC_TIME]
    }
}
