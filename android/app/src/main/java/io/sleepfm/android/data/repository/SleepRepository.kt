package io.sleepfm.android.data.repository

import io.sleepfm.android.data.api.SleepFMApi
import io.sleepfm.android.data.local.SleepDatabase
import io.sleepfm.android.data.local.entity.SleepSessionEntity
import io.sleepfm.android.domain.model.*
import kotlinx.coroutines.flow.Flow
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SleepRepository @Inject constructor(
    private val api: SleepFMApi,
    private val database: SleepDatabase
) {
    private val dao = database.sleepSessionDao()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
    
    // Local data flows
    val allSessions: Flow<List<SleepSessionEntity>> = dao.getAllSessions()
    
    // Remote API calls
    suspend fun syncSession(request: SyncRequest): Result<SleepSession> {
        return try {
            val response = api.syncSession(request)
            if (response.isSuccessful && response.body() != null) {
                val session = response.body()!!
                saveSessionToLocal(session)
                Result.success(session)
            } else {
                Result.failure(Exception("Sync failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getHistory(days: Int = 30): Result<List<SleepSession>> {
        return try {
            val response = api.getHistory(days)
            if (response.isSuccessful && response.body() != null) {
                val sessions = response.body()!!
                sessions.forEach { session -> saveSessionToLocal(session) }
                Result.success(sessions)
            } else {
                Result.failure(Exception("Failed to get history: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getSession(sessionId: Int): Result<SleepSession> {
        return try {
            val response = api.getSession(sessionId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to get session: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun analyzeSession(sessionId: Int): Result<AnalysisResponse> {
        return try {
            val response = api.getAnalysis(sessionId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to analyze: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun predictDiseaseRisk(sessionId: Int): Result<DiseaseRiskResponse> {
        return try {
            val response = api.getDiseaseRisk(sessionId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to predict: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getLatestSession(): Result<SleepSession> {
        return try {
            val response = api.getLatestSession()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to get latest: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Local database operations
    suspend fun getLocalSession(sessionId: Int): SleepSessionEntity? {
        return dao.getSessionById(sessionId)
    }
    
    suspend fun getLatestLocalSession(): SleepSessionEntity? {
        return dao.getLatestSession()
    }
    
    suspend fun deleteLocalSession(session: SleepSessionEntity) {
        dao.deleteSession(session.id)
    }
    
    private suspend fun saveSessionToLocal(session: SleepSession) {
        val entity = SleepSessionEntity(
            id = session.id,
            userId = session.userId,
            startTime = parseDate(session.startTime),
            endTime = session.endTime?.let { parseDate(it) },
            duration = session.durationMinutes,
            sleepQuality = session.sleepQuality,
            efficiency = session.efficiency,
            syncedAt = Date(),
            createdAt = Date()
        )
        dao.insertSession(entity)
    }
    
    private fun parseDate(dateString: String): Date {
        return try {
            dateFormat.parse(dateString) ?: Date()
        } catch (e: Exception) {
            Date()
        }
    }
}
