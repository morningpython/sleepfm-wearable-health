package io.sleepfm.wear.service

import android.content.Context
import androidx.health.services.client.HealthServices
import androidx.health.services.client.MeasureCallback
import androidx.health.services.client.data.*
import dagger.hilt.android.qualifiers.ApplicationContext
import io.sleepfm.wear.data.model.AccelerometerReading
import io.sleepfm.wear.data.model.SensorReading
import kotlinx.coroutines.flow.*
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager for sensor data collection using Health Services API
 */
@Singleton
class SensorDataManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val healthServicesClient by lazy { HealthServices.getClient(context) }
    private val measureClient by lazy { healthServicesClient.measureClient }
    
    private val _heartRateFlow = MutableStateFlow<SensorReading?>(null)
    val heartRateFlow: StateFlow<SensorReading?> = _heartRateFlow.asStateFlow()
    
    private val _spO2Flow = MutableStateFlow<SensorReading?>(null)
    val spO2Flow: StateFlow<SensorReading?> = _spO2Flow.asStateFlow()
    
    private val _accelerometerFlow = MutableStateFlow<AccelerometerReading?>(null)
    val accelerometerFlow: StateFlow<AccelerometerReading?> = _accelerometerFlow.asStateFlow()
    
    private var heartRateCallback: MeasureCallback? = null
    private var isMonitoring = false
    
    /**
     * Check if heart rate measurement is supported
     */
    fun supportsHeartRate(): Boolean {
        // Assume heart rate is supported on Wear OS devices
        return true
    }
    
    /**
     * Start all sensor measurements
     */
    suspend fun startMeasurement() {
        if (isMonitoring) return
        isMonitoring = true
        startHeartRateMonitoringInternal()
    }
    
    /**
     * Stop all sensor measurements
     */
    suspend fun stopMeasurement() {
        isMonitoring = false
        stopHeartRateMonitoring()
    }
    
    private suspend fun startHeartRateMonitoringInternal() {
        val callback = object : MeasureCallback {
            override fun onAvailabilityChanged(
                dataType: DeltaDataType<*, *>,
                availability: Availability
            ) {
                Timber.d("Heart rate availability changed: $availability")
            }
            
            override fun onDataReceived(data: DataPointContainer) {
                val heartRatePoints = data.getData(DataType.HEART_RATE_BPM)
                heartRatePoints.forEach { dataPoint ->
                    val heartRate = dataPoint.value.toFloat()
                    val reading = SensorReading(System.currentTimeMillis(), heartRate)
                    _heartRateFlow.value = reading
                    Timber.d("Heart rate: $heartRate bpm")
                }
            }
        }
        
        heartRateCallback = callback
        
        try {
            measureClient.registerMeasureCallback(DataType.HEART_RATE_BPM, callback)
            Timber.d("Heart rate monitoring started")
        } catch (e: Exception) {
            Timber.e(e, "Error starting heart rate monitoring")
        }
    }
    
    /**
     * Stop heart rate monitoring
     */
    suspend fun stopHeartRateMonitoring() {
        heartRateCallback?.let { callback ->
            try {
                measureClient.unregisterMeasureCallbackAsync(DataType.HEART_RATE_BPM, callback)
                heartRateCallback = null
                Timber.d("Heart rate monitoring stopped")
            } catch (e: Exception) {
                Timber.e(e, "Error stopping heart rate monitoring")
            }
        }
    }
    
    /**
     * Collect accelerometer data
     */
    fun collectAccelerometerData(x: Float, y: Float, z: Float) {
        val reading = AccelerometerReading(System.currentTimeMillis(), x, y, z)
        _accelerometerFlow.value = reading
    }
    
    /**
     * Update SpO2 value (from passive monitoring or manual measurement)
     */
    fun updateSpO2(value: Float) {
        val reading = SensorReading(System.currentTimeMillis(), value)
        _spO2Flow.value = reading
    }
}
