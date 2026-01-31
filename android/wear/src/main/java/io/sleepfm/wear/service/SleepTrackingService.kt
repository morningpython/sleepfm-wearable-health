package io.sleepfm.wear.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.IBinder
import androidx.core.app.NotificationCompat
import dagger.hilt.android.AndroidEntryPoint
import io.sleepfm.wear.R
import io.sleepfm.wear.data.local.SleepDataStore
import io.sleepfm.wear.data.model.SensorReading
import io.sleepfm.wear.data.model.AccelerometerReading
import io.sleepfm.wear.presentation.MainActivity
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import timber.log.Timber
import javax.inject.Inject

/**
 * Foreground service for sleep tracking
 * Collects sensor data during sleep
 */
@AndroidEntryPoint
class SleepTrackingService : Service() {
    
    @Inject
    lateinit var sensorDataManager: SensorDataManager
    
    @Inject
    lateinit var sleepDataStore: SleepDataStore
    
    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    
    private var heartRateJob: Job? = null
    private var dataCollectionJob: Job? = null
    
    private val heartRateReadings = mutableListOf<SensorReading>()
    private val spO2Readings = mutableListOf<SensorReading>()
    private val accelerometerReadings = mutableListOf<AccelerometerReading>()
    
    companion object {
        const val CHANNEL_ID = "sleep_tracking_channel"
        const val NOTIFICATION_ID = 1001
        
        const val ACTION_START = "io.sleepfm.wear.action.START_TRACKING"
        const val ACTION_STOP = "io.sleepfm.wear.action.STOP_TRACKING"
    }
    
    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        Timber.d("SleepTrackingService created")
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startTracking()
            ACTION_STOP -> stopTracking()
        }
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
        Timber.d("SleepTrackingService destroyed")
    }
    
    private fun startTracking() {
        Timber.d("Starting sleep tracking")
        
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        
        // Store start time
        serviceScope.launch {
            sleepDataStore.setTrackingStartTime(System.currentTimeMillis())
            sleepDataStore.setIsTracking(true)
        }
        
        // Start sensor measurement
        serviceScope.launch {
            sensorDataManager.startMeasurement()
        }
        
        // Collect heart rate readings
        heartRateJob = serviceScope.launch {
            sensorDataManager.heartRateFlow.filterNotNull().collect { reading ->
                heartRateReadings.add(reading)
            }
        }
        
        // Collect SpO2 periodically
        dataCollectionJob = serviceScope.launch {
            while (isActive) {
                delay(30_000) // Every 30 seconds
                
                // Collect SpO2 if available
                val spO2 = sensorDataManager.spO2Flow.value
                spO2?.let {
                    spO2Readings.add(it)
                }
                
                // Save data periodically
                saveCollectedData()
            }
        }
        
        // Collect accelerometer data
        serviceScope.launch {
            sensorDataManager.accelerometerFlow.filterNotNull().collect { data ->
                accelerometerReadings.add(data)
            }
        }
    }
    
    private fun stopTracking() {
        Timber.d("Stopping sleep tracking")
        
        heartRateJob?.cancel()
        dataCollectionJob?.cancel()
        
        // Stop sensor measurement
        serviceScope.launch {
            sensorDataManager.stopMeasurement()
        }
        
        // Save final data
        serviceScope.launch {
            saveCollectedData()
            sleepDataStore.setIsTracking(false)
            sleepDataStore.setTrackingEndTime(System.currentTimeMillis())
            
            // Clear readings
            heartRateReadings.clear()
            spO2Readings.clear()
            accelerometerReadings.clear()
        }
        
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }
    
    private suspend fun saveCollectedData() {
        try {
            sleepDataStore.saveHeartRateReadings(heartRateReadings.toList())
            sleepDataStore.saveSpO2Readings(spO2Readings.toList())
            Timber.d("Saved ${heartRateReadings.size} HR readings, ${spO2Readings.size} SpO2 readings")
        } catch (e: Exception) {
            Timber.e(e, "Error saving sensor data")
        }
    }
    
    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "수면 추적",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "수면 추적 서비스 알림"
            setShowBadge(false)
        }
        
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.createNotificationChannel(channel)
    }
    
    private fun createNotification(): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )
        
        val stopIntent = Intent(this, SleepTrackingService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPendingIntent = PendingIntent.getService(
            this,
            0,
            stopIntent,
            PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("수면 추적 중")
            .setContentText("SleepFM이 수면 데이터를 수집하고 있습니다")
            .setSmallIcon(android.R.drawable.ic_menu_recent_history)
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .addAction(
                android.R.drawable.ic_media_pause,
                "중지",
                stopPendingIntent
            )
            .build()
    }
}
