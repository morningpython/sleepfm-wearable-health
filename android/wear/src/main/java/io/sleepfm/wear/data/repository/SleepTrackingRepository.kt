package io.sleepfm.wear.data.repository

import io.sleepfm.wear.data.local.SleepDataStore
import io.sleepfm.wear.data.model.CollectedSleepData
import io.sleepfm.wear.data.model.SensorReading
import io.sleepfm.wear.data.model.SleepSession
import io.sleepfm.wear.service.SensorDataManager
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SleepTrackingRepository @Inject constructor(
    private val sensorDataManager: SensorDataManager,
    private val sleepDataStore: SleepDataStore
) {
    private val _trackingState = MutableStateFlow(TrackingState())
    val trackingState: StateFlow<TrackingState> = _trackingState.asStateFlow()
    
    val isTracking: Flow<Boolean> = sleepDataStore.isTracking
    
    val heartRateFlow: Flow<SensorReading?> = sensorDataManager.heartRateFlow
    val spO2Flow: Flow<SensorReading?> = sensorDataManager.spO2Flow
    val accelerometerFlow: Flow<io.sleepfm.wear.data.model.AccelerometerReading?> = sensorDataManager.accelerometerFlow
    
    suspend fun startTracking() {
        val startTime = System.currentTimeMillis()
        sleepDataStore.clearTrackingData()
        sleepDataStore.setIsTracking(true)
        sleepDataStore.setTrackingStartTime(startTime)
        
        _trackingState.value = TrackingState(
            isTracking = true,
            startTime = startTime
        )
        
        sensorDataManager.startMeasurement()
    }
    
    suspend fun stopTracking(): CollectedSleepData {
        val endTime = System.currentTimeMillis()
        sleepDataStore.setTrackingEndTime(endTime)
        sleepDataStore.setIsTracking(false)
        
        sensorDataManager.stopMeasurement()
        
        val data = sleepDataStore.getCollectedSleepData()
        
        _trackingState.value = TrackingState(
            isTracking = false,
            startTime = null
        )
        
        return data
    }
    
    suspend fun saveHeartRateReading(reading: SensorReading) {
        sleepDataStore.saveHeartRateReadings(listOf(reading))
    }
    
    suspend fun saveSpO2Reading(reading: SensorReading) {
        sleepDataStore.saveSpO2Readings(listOf(reading))
    }
    
    suspend fun saveSleepSession(session: SleepSession) {
        sleepDataStore.saveLastSession(session)
    }
    
    suspend fun getLastSession(): SleepSession? {
        return sleepDataStore.getLastSession()
    }
    
    suspend fun getCollectedData(): CollectedSleepData {
        return sleepDataStore.getCollectedSleepData()
    }
    
    suspend fun clearSession() {
        sleepDataStore.clearTrackingData()
    }
    
    data class TrackingState(
        val isTracking: Boolean = false,
        val startTime: Long? = null
    )
}
