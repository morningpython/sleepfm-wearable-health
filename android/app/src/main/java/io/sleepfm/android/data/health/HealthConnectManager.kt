package io.sleepfm.android.data.health

import android.content.Context
import android.content.Intent
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.OxygenSaturationRecord
import androidx.health.connect.client.records.SleepSessionRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import timber.log.Timber
import java.time.Instant
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Health Connect Manager
 * Manages Health Connect API integration for reading health data
 */
@Singleton
class HealthConnectManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val healthConnectClient by lazy { HealthConnectClient.getOrCreate(context) }
    
    companion object {
        val PERMISSIONS = setOf(
            HealthPermission.getReadPermission(HeartRateRecord::class),
            HealthPermission.getReadPermission(OxygenSaturationRecord::class),
            HealthPermission.getReadPermission(SleepSessionRecord::class),
            HealthPermission.getReadPermission(StepsRecord::class)
        )
    }
    
    /**
     * Check if Health Connect is available on the device
     */
    fun isAvailable(): Boolean {
        return try {
            val status = HealthConnectClient.getSdkStatus(context)
            status == HealthConnectClient.SDK_AVAILABLE
        } catch (e: Exception) {
            Timber.e(e, "Error checking Health Connect availability")
            false
        }
    }
    
    /**
     * Check if all required permissions are granted
     */
    suspend fun hasAllPermissions(): Boolean {
        return try {
            val granted = healthConnectClient.permissionController.getGrantedPermissions()
            PERMISSIONS.all { it in granted }
        } catch (e: Exception) {
            Timber.e(e, "Error checking permissions")
            false
        }
    }
    
    /**
     * Create permission request contract
     */
    fun createPermissionRequestContract(): PermissionController.PermissionLauncher {
        return healthConnectClient.permissionController
    }
    
    /**
     * Read heart rate data for a given time range
     */
    suspend fun readHeartRateData(
        startTime: Instant,
        endTime: Instant
    ): Result<List<HeartRateRecord>> {
        return try {
            val request = ReadRecordsRequest(
                recordType = HeartRateRecord::class,
                timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
            )
            val response = healthConnectClient.readRecords(request)
            Result.success(response.records)
        } catch (e: Exception) {
            Timber.e(e, "Error reading heart rate data")
            Result.failure(e)
        }
    }
    
    /**
     * Read oxygen saturation (SpO2) data for a given time range
     */
    suspend fun readOxygenSaturationData(
        startTime: Instant,
        endTime: Instant
    ): Result<List<OxygenSaturationRecord>> {
        return try {
            val request = ReadRecordsRequest(
                recordType = OxygenSaturationRecord::class,
                timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
            )
            val response = healthConnectClient.readRecords(request)
            Result.success(response.records)
        } catch (e: Exception) {
            Timber.e(e, "Error reading oxygen saturation data")
            Result.failure(e)
        }
    }
    
    /**
     * Read sleep session data for a given time range
     */
    suspend fun readSleepSessions(
        startTime: Instant,
        endTime: Instant
    ): Result<List<SleepSessionRecord>> {
        return try {
            val request = ReadRecordsRequest(
                recordType = SleepSessionRecord::class,
                timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
            )
            val response = healthConnectClient.readRecords(request)
            Result.success(response.records)
        } catch (e: Exception) {
            Timber.e(e, "Error reading sleep sessions")
            Result.failure(e)
        }
    }
    
    /**
     * Read last night's sleep data
     */
    suspend fun readLastNightSleep(): Result<SleepSessionRecord?> {
        return try {
            val now = ZonedDateTime.now()
            val startOfYesterday = now.minusDays(1).truncatedTo(ChronoUnit.DAYS)
            
            val request = ReadRecordsRequest(
                recordType = SleepSessionRecord::class,
                timeRangeFilter = TimeRangeFilter.between(
                    startOfYesterday.toInstant(),
                    now.toInstant()
                )
            )
            
            val response = healthConnectClient.readRecords(request)
            Result.success(response.records.lastOrNull())
        } catch (e: Exception) {
            Timber.e(e, "Error reading last night's sleep")
            Result.failure(e)
        }
    }
    
    /**
     * Read steps data for a given time range
     */
    suspend fun readStepsData(
        startTime: Instant,
        endTime: Instant
    ): Result<List<StepsRecord>> {
        return try {
            val request = ReadRecordsRequest(
                recordType = StepsRecord::class,
                timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
            )
            val response = healthConnectClient.readRecords(request)
            Result.success(response.records)
        } catch (e: Exception) {
            Timber.e(e, "Error reading steps data")
            Result.failure(e)
        }
    }
    
    /**
     * Get a flow of sleep data updates
     */
    fun getSleepDataFlow(): Flow<List<SleepSessionRecord>> = flow {
        val now = ZonedDateTime.now()
        val startOfWeek = now.minusDays(7).truncatedTo(ChronoUnit.DAYS)
        
        readSleepSessions(startOfWeek.toInstant(), now.toInstant())
            .onSuccess { sessions ->
                emit(sessions)
            }
    }
    
    /**
     * Open Health Connect app/settings
     */
    fun openHealthConnectSettings(): Intent? {
        return try {
            val intent = Intent("androidx.health.ACTION_HEALTH_CONNECT_SETTINGS")
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            intent
        } catch (e: Exception) {
            Timber.e(e, "Error creating Health Connect settings intent")
            null
        }
    }
}

/**
 * Data class representing aggregated sleep health data
 */
data class SleepHealthData(
    val heartRateSamples: List<HeartRateSample>,
    val oxygenSaturationSamples: List<OxygenSaturationSample>,
    val sleepSessions: List<SleepSessionData>
)

data class HeartRateSample(
    val timestamp: Instant,
    val beatsPerMinute: Long
)

data class OxygenSaturationSample(
    val timestamp: Instant,
    val percentage: Double
)

data class SleepSessionData(
    val startTime: Instant,
    val endTime: Instant,
    val stages: List<SleepStageData>
)

data class SleepStageData(
    val startTime: Instant,
    val endTime: Instant,
    val stage: SleepStageType
)

enum class SleepStageType {
    UNKNOWN,
    AWAKE,
    SLEEPING,
    OUT_OF_BED,
    LIGHT,
    DEEP,
    REM
}
