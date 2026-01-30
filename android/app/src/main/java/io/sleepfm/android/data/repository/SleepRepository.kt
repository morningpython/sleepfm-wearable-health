package io.sleepfm.android.data.repository

import io.sleepfm.android.data.api.SleepFMApi
import io.sleepfm.android.data.local.SleepDatabase
import io.sleepfm.android.data.local.entity.SleepSessionEntity
import io.sleepfm.android.domain.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
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
    val latestSession: Flow<SleepSessionEntity?> = dao.getLatestSession()
    
    // Remote API calls
    suspend fun syncSession(request: SyncRequest): Result<SleepSession> {
        return try {
            val session = api.syncSession(request)
            // Save to local database
            saveSessionToLocal(session)
            Result.success(session)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getHistory(startDate: String? = null, endDate: String? = null): Result<List<SleepSession>> {
        return try {
            val sessions = api.getHistory(startDate, endDate)
            // Cache sessions locally
            sessions.forEach { saveSessionToLocal(it) }
            Result.success(sessions)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getSession(sessionId: Int): Result<SleepSession> {
        return try {
            val session = api.getSession(sessionId)
            Result.success(session)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun analyzeSession(sessionId: Int): Result<AnalysisResponse> {
        return try {
            val analysis = api.analyzeSession(sessionId)
            Result.success(analysis)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun predictDiseaseRisk(sessionId: Int): Result<DiseaseRiskResponse> {
        return try {
            val risk = api.predictDiseaseRisk(sessionId)
            Result.success(risk)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Local database operations
    suspend fun getLocalSession(sessionId: Int): SleepSessionEntity? {
        return dao.getSessionById(sessionId)
    }
    
    suspend fun deleteLocalSession(session: SleepSessionEntity) {
        dao.delete(session)
    }
    
    private suspend fun saveSessionToLocal(session: SleepSession) {
        val entity = SleepSessionEntity(
            id = session.id,
            userId = session.userId,
            startTime = parseDate(session.startTime),
            endTime = session.endTime?.let { parseDate(it) },
            durationMinutes = session.durationMinutes,
            sleepQuality = session.sleepQuality,
            efficiency = session.efficiency
        )
        dao.insert(entity)
    }
    
    private fun parseDate(dateString: String): Date {
        return try {
            dateFormat.parse(dateString) ?: Date()
        } catch (e: Exception) {
            Date()
        }
    }
}
