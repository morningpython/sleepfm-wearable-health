package io.sleepfm.android.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

/**
 * Sleep Session Entity for Room Database
 */
@Entity(tableName = "sleep_sessions")
data class SleepSessionEntity(
    @PrimaryKey
    val id: Int,
    val userId: Int,
    val startTime: Date,
    val endTime: Date?,
    val duration: Int?, // in minutes
    val sleepQuality: Float?,
    val efficiency: Float?,
    val syncedAt: Date?,
    val createdAt: Date
)
