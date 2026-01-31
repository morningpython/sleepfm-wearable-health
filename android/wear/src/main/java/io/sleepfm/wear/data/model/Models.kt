package io.sleepfm.wear.data.model

import com.google.gson.annotations.SerializedName

/**
 * Sensor reading data
 */
data class SensorReading(
    val timestamp: Long,
    val value: Float
)

/**
 * Sleep session data stored locally
 */
data class SleepSession(
    val id: String,
    val startTime: Long,
    val endTime: Long,
    val durationMinutes: Int,
    val sleepScore: Int,
    val bedTime: String,
    val wakeTime: String,
    val deepMinutes: Int,
    val lightMinutes: Int,
    val remMinutes: Int,
    val wakeMinutes: Int,
    val avgHeartRate: Int,
    val avgSpO2: Int,
    val heartRateReadings: List<SensorReading>,
    val spO2Readings: List<SensorReading>,
    val synced: Boolean = false
)

/**
 * Collected sleep data for sync
 */
data class CollectedSleepData(
    @SerializedName("start_time")
    val startTime: Long,
    @SerializedName("end_time")
    val endTime: Long,
    @SerializedName("heart_rate_data")
    val heartRateData: List<SensorReading>,
    @SerializedName("spo2_data")
    val spO2Data: List<SensorReading>,
    @SerializedName("accelerometer_data")
    val accelerometerData: List<AccelerometerReading>
)

data class AccelerometerReading(
    val timestamp: Long,
    val x: Float,
    val y: Float,
    val z: Float
)
