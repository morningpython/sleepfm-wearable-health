package io.sleepfm.android.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import io.sleepfm.android.data.local.entity.SleepSessionEntity
import kotlinx.coroutines.flow.Flow

/**
 * Sleep Session DAO
 */
@Dao
interface SleepSessionDao {

    @Query("SELECT * FROM sleep_sessions ORDER BY startTime DESC")
    fun getAllSessions(): Flow<List<SleepSessionEntity>>

    @Query("SELECT * FROM sleep_sessions WHERE id = :id")
    suspend fun getSessionById(id: Int): SleepSessionEntity?

    @Query("SELECT * FROM sleep_sessions ORDER BY startTime DESC LIMIT 1")
    suspend fun getLatestSession(): SleepSessionEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSession(session: SleepSessionEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSessions(sessions: List<SleepSessionEntity>)

    @Query("DELETE FROM sleep_sessions WHERE id = :id")
    suspend fun deleteSession(id: Int)

    @Query("DELETE FROM sleep_sessions")
    suspend fun deleteAllSessions()

    @Query("SELECT COUNT(*) FROM sleep_sessions")
    suspend fun getSessionCount(): Int
}
