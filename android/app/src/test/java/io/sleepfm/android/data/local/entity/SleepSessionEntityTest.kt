package io.sleepfm.android.data.local.entity

import org.junit.Assert.*
import org.junit.Test
import java.util.*

class SleepSessionEntityTest {

    @Test
    fun `SleepSessionEntity holds all required fields`() {
        val now = Date()
        val startTime = Date(now.time - 8 * 60 * 60 * 1000) // 8 hours ago
        
        val entity = SleepSessionEntity(
            id = 1,
            userId = 42,
            startTime = startTime,
            endTime = now,
            duration = 480,
            sleepQuality = 0.85f,
            efficiency = 0.92f,
            syncedAt = now,
            createdAt = startTime
        )
        
        assertEquals(1, entity.id)
        assertEquals(42, entity.userId)
        assertEquals(startTime, entity.startTime)
        assertEquals(now, entity.endTime)
        assertEquals(480, entity.duration)
        assertEquals(0.85f, entity.sleepQuality!!, 0.001f)
        assertEquals(0.92f, entity.efficiency!!, 0.001f)
        assertEquals(now, entity.syncedAt)
        assertEquals(startTime, entity.createdAt)
    }

    @Test
    fun `SleepSessionEntity with nullable fields as null`() {
        val now = Date()
        
        val entity = SleepSessionEntity(
            id = 1,
            userId = 1,
            startTime = now,
            endTime = null,
            duration = null,
            sleepQuality = null,
            efficiency = null,
            syncedAt = null,
            createdAt = now
        )
        
        assertNull(entity.endTime)
        assertNull(entity.duration)
        assertNull(entity.sleepQuality)
        assertNull(entity.efficiency)
        assertNull(entity.syncedAt)
    }

    @Test
    fun `SleepSessionEntity in progress session has no end time`() {
        val startTime = Date()
        
        val inProgressSession = SleepSessionEntity(
            id = 1,
            userId = 1,
            startTime = startTime,
            endTime = null,
            duration = null,
            sleepQuality = null,
            efficiency = null,
            syncedAt = null,
            createdAt = startTime
        )
        
        assertNotNull(inProgressSession.startTime)
        assertNull(inProgressSession.endTime)
    }

    @Test
    fun `SleepSessionEntity copy creates modified instance`() {
        val now = Date()
        val original = SleepSessionEntity(
            id = 1,
            userId = 1,
            startTime = now,
            endTime = null,
            duration = null,
            sleepQuality = null,
            efficiency = null,
            syncedAt = null,
            createdAt = now
        )
        
        val completed = original.copy(
            endTime = Date(now.time + 480 * 60 * 1000),
            duration = 480,
            sleepQuality = 0.9f,
            efficiency = 0.95f
        )
        
        assertEquals(original.id, completed.id)
        assertEquals(original.userId, completed.userId)
        assertNotNull(completed.endTime)
        assertEquals(480, completed.duration)
        assertEquals(0.9f, completed.sleepQuality!!, 0.001f)
        assertEquals(0.95f, completed.efficiency!!, 0.001f)
    }

    @Test
    fun `SleepSessionEntity equality works correctly`() {
        val now = Date()
        val entity1 = SleepSessionEntity(
            id = 1, userId = 1, startTime = now, endTime = null,
            duration = null, sleepQuality = null, efficiency = null,
            syncedAt = null, createdAt = now
        )
        val entity2 = SleepSessionEntity(
            id = 1, userId = 1, startTime = now, endTime = null,
            duration = null, sleepQuality = null, efficiency = null,
            syncedAt = null, createdAt = now
        )
        val entity3 = SleepSessionEntity(
            id = 2, userId = 1, startTime = now, endTime = null,
            duration = null, sleepQuality = null, efficiency = null,
            syncedAt = null, createdAt = now
        )
        
        assertEquals(entity1, entity2)
        assertNotEquals(entity1, entity3)
    }

    @Test
    fun `SleepSessionEntity hashCode is consistent`() {
        val now = Date()
        val entity1 = SleepSessionEntity(
            id = 1, userId = 1, startTime = now, endTime = null,
            duration = null, sleepQuality = null, efficiency = null,
            syncedAt = null, createdAt = now
        )
        val entity2 = SleepSessionEntity(
            id = 1, userId = 1, startTime = now, endTime = null,
            duration = null, sleepQuality = null, efficiency = null,
            syncedAt = null, createdAt = now
        )
        
        assertEquals(entity1.hashCode(), entity2.hashCode())
    }

    @Test
    fun `SleepSessionEntity with synced status`() {
        val now = Date()
        val syncedAt = Date()
        
        val syncedEntity = SleepSessionEntity(
            id = 1,
            userId = 1,
            startTime = now,
            endTime = Date(now.time + 480 * 60 * 1000),
            duration = 480,
            sleepQuality = 0.85f,
            efficiency = 0.90f,
            syncedAt = syncedAt,
            createdAt = now
        )
        
        assertNotNull(syncedEntity.syncedAt)
    }

    @Test
    fun `SleepSessionEntity duration calculation scenario`() {
        val now = Date()
        val startTime = Date(now.time - 6 * 60 * 60 * 1000) // 6 hours ago
        
        val entity = SleepSessionEntity(
            id = 1,
            userId = 1,
            startTime = startTime,
            endTime = now,
            duration = 360, // 6 hours in minutes
            sleepQuality = 0.75f,
            efficiency = 0.85f,
            syncedAt = null,
            createdAt = startTime
        )
        
        assertEquals(360, entity.duration)
    }

    @Test
    fun `SleepSessionEntity quality values in valid range`() {
        val now = Date()
        
        // Low quality
        val lowQuality = SleepSessionEntity(
            id = 1, userId = 1, startTime = now, endTime = now,
            duration = 300, sleepQuality = 0.2f, efficiency = 0.3f,
            syncedAt = null, createdAt = now
        )
        assertTrue(lowQuality.sleepQuality!! >= 0f && lowQuality.sleepQuality!! <= 1f)
        
        // High quality
        val highQuality = SleepSessionEntity(
            id = 2, userId = 1, startTime = now, endTime = now,
            duration = 480, sleepQuality = 0.95f, efficiency = 0.98f,
            syncedAt = null, createdAt = now
        )
        assertTrue(highQuality.sleepQuality!! >= 0f && highQuality.sleepQuality!! <= 1f)
        assertTrue(highQuality.efficiency!! >= 0f && highQuality.efficiency!! <= 1f)
    }
}
