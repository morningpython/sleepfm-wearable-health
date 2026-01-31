package io.sleepfm.wear.data.model

import org.junit.Assert.*
import org.junit.Test

class ModelsTest {

    // ==========================================
    // SensorReading Tests
    // ==========================================

    @Test
    fun `SensorReading should hold timestamp and value`() {
        val reading = SensorReading(
            timestamp = 1609459200000L,
            value = 72.5f
        )
        
        assertEquals(1609459200000L, reading.timestamp)
        assertEquals(72.5f, reading.value, 0.01f)
    }

    @Test
    fun `SensorReading equality works correctly`() {
        val reading1 = SensorReading(1000L, 70f)
        val reading2 = SensorReading(1000L, 70f)
        val reading3 = SensorReading(2000L, 70f)
        
        assertEquals(reading1, reading2)
        assertNotEquals(reading1, reading3)
    }

    @Test
    fun `SensorReading copy creates new instance`() {
        val original = SensorReading(1000L, 72f)
        val copied = original.copy(value = 75f)
        
        assertEquals(1000L, copied.timestamp)
        assertEquals(75f, copied.value, 0.01f)
        assertNotEquals(original, copied)
    }

    @Test
    fun `SensorReading hashCode is consistent`() {
        val reading1 = SensorReading(1000L, 70f)
        val reading2 = SensorReading(1000L, 70f)
        
        assertEquals(reading1.hashCode(), reading2.hashCode())
    }

    // ==========================================
    // SleepSession Tests
    // ==========================================

    @Test
    fun `SleepSession should hold all session data`() {
        val heartRateReadings = listOf(SensorReading(1000L, 65f))
        val spO2Readings = listOf(SensorReading(1000L, 98f))
        
        val session = SleepSession(
            id = "session_1",
            startTime = 1609459200000L,
            endTime = 1609488000000L,
            durationMinutes = 480,
            sleepScore = 85,
            bedTime = "22:00",
            wakeTime = "06:00",
            deepMinutes = 120,
            lightMinutes = 180,
            remMinutes = 120,
            wakeMinutes = 60,
            avgHeartRate = 62,
            avgSpO2 = 97,
            heartRateReadings = heartRateReadings,
            spO2Readings = spO2Readings,
            synced = false
        )
        
        assertEquals("session_1", session.id)
        assertEquals(480, session.durationMinutes)
        assertEquals(85, session.sleepScore)
        assertEquals("22:00", session.bedTime)
        assertEquals("06:00", session.wakeTime)
        assertEquals(120, session.deepMinutes)
        assertEquals(180, session.lightMinutes)
        assertEquals(120, session.remMinutes)
        assertEquals(60, session.wakeMinutes)
        assertEquals(62, session.avgHeartRate)
        assertEquals(97, session.avgSpO2)
        assertFalse(session.synced)
    }

    @Test
    fun `SleepSession default synced is false`() {
        val session = SleepSession(
            id = "test",
            startTime = 0L,
            endTime = 0L,
            durationMinutes = 0,
            sleepScore = 0,
            bedTime = "",
            wakeTime = "",
            deepMinutes = 0,
            lightMinutes = 0,
            remMinutes = 0,
            wakeMinutes = 0,
            avgHeartRate = 0,
            avgSpO2 = 0,
            heartRateReadings = emptyList(),
            spO2Readings = emptyList()
        )
        
        assertFalse(session.synced)
    }

    @Test
    fun `SleepSession can be marked as synced`() {
        val session = SleepSession(
            id = "test",
            startTime = 0L,
            endTime = 0L,
            durationMinutes = 0,
            sleepScore = 0,
            bedTime = "",
            wakeTime = "",
            deepMinutes = 0,
            lightMinutes = 0,
            remMinutes = 0,
            wakeMinutes = 0,
            avgHeartRate = 0,
            avgSpO2 = 0,
            heartRateReadings = emptyList(),
            spO2Readings = emptyList(),
            synced = true
        )
        
        assertTrue(session.synced)
    }

    @Test
    fun `SleepSession copy preserves all fields`() {
        val session = SleepSession(
            id = "original",
            startTime = 1000L,
            endTime = 2000L,
            durationMinutes = 480,
            sleepScore = 90,
            bedTime = "22:00",
            wakeTime = "06:00",
            deepMinutes = 100,
            lightMinutes = 200,
            remMinutes = 100,
            wakeMinutes = 80,
            avgHeartRate = 60,
            avgSpO2 = 98,
            heartRateReadings = listOf(SensorReading(1000L, 60f)),
            spO2Readings = listOf(SensorReading(1000L, 98f)),
            synced = false
        )
        
        val syncedSession = session.copy(synced = true)
        
        assertEquals(session.id, syncedSession.id)
        assertEquals(session.sleepScore, syncedSession.sleepScore)
        assertTrue(syncedSession.synced)
    }

    // ==========================================
    // CollectedSleepData Tests
    // ==========================================

    @Test
    fun `CollectedSleepData should hold all collected data`() {
        val heartRateData = listOf(
            SensorReading(1000L, 65f),
            SensorReading(2000L, 68f)
        )
        val spO2Data = listOf(
            SensorReading(1000L, 97f)
        )
        val accelerometerData = listOf(
            AccelerometerReading(1000L, 0.1f, 0.2f, 9.8f)
        )
        
        val collectedData = CollectedSleepData(
            startTime = 1000L,
            endTime = 10000L,
            heartRateData = heartRateData,
            spO2Data = spO2Data,
            accelerometerData = accelerometerData
        )
        
        assertEquals(1000L, collectedData.startTime)
        assertEquals(10000L, collectedData.endTime)
        assertEquals(2, collectedData.heartRateData.size)
        assertEquals(1, collectedData.spO2Data.size)
        assertEquals(1, collectedData.accelerometerData.size)
    }

    @Test
    fun `CollectedSleepData with empty lists`() {
        val collectedData = CollectedSleepData(
            startTime = 0L,
            endTime = 1000L,
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        
        assertTrue(collectedData.heartRateData.isEmpty())
        assertTrue(collectedData.spO2Data.isEmpty())
        assertTrue(collectedData.accelerometerData.isEmpty())
    }

    @Test
    fun `CollectedSleepData duration can be calculated`() {
        val collectedData = CollectedSleepData(
            startTime = 1000L,
            endTime = 9000L, // 8 seconds
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        
        val durationMs = collectedData.endTime - collectedData.startTime
        assertEquals(8000L, durationMs)
    }

    // ==========================================
    // AccelerometerReading Tests
    // ==========================================

    @Test
    fun `AccelerometerReading should hold xyz values`() {
        val reading = AccelerometerReading(
            timestamp = 1000L,
            x = 0.1f,
            y = 0.2f,
            z = 9.8f
        )
        
        assertEquals(1000L, reading.timestamp)
        assertEquals(0.1f, reading.x, 0.001f)
        assertEquals(0.2f, reading.y, 0.001f)
        assertEquals(9.8f, reading.z, 0.001f)
    }

    @Test
    fun `AccelerometerReading equality works correctly`() {
        val reading1 = AccelerometerReading(1000L, 0.1f, 0.2f, 9.8f)
        val reading2 = AccelerometerReading(1000L, 0.1f, 0.2f, 9.8f)
        val reading3 = AccelerometerReading(2000L, 0.1f, 0.2f, 9.8f)
        
        assertEquals(reading1, reading2)
        assertNotEquals(reading1, reading3)
    }

    @Test
    fun `AccelerometerReading can calculate magnitude`() {
        val reading = AccelerometerReading(
            timestamp = 1000L,
            x = 3f,
            y = 4f,
            z = 0f
        )
        
        // Manual magnitude calculation: sqrt(3^2 + 4^2 + 0^2) = 5
        val magnitude = kotlin.math.sqrt(
            reading.x * reading.x + 
            reading.y * reading.y + 
            reading.z * reading.z
        )
        assertEquals(5f, magnitude, 0.001f)
    }

    @Test
    fun `AccelerometerReading copy creates new instance`() {
        val original = AccelerometerReading(1000L, 0.1f, 0.2f, 9.8f)
        val copied = original.copy(x = 0.5f)
        
        assertEquals(0.5f, copied.x, 0.001f)
        assertEquals(original.y, copied.y, 0.001f)
        assertEquals(original.z, copied.z, 0.001f)
    }

    // ==========================================
    // Data Class Feature Tests
    // ==========================================

    @Test
    fun `SensorReading supports destructuring`() {
        val reading = SensorReading(1000L, 72f)
        val (timestamp, value) = reading
        
        assertEquals(1000L, timestamp)
        assertEquals(72f, value, 0.01f)
    }

    @Test
    fun `AccelerometerReading supports destructuring`() {
        val reading = AccelerometerReading(1000L, 1f, 2f, 3f)
        val (timestamp, x, y, z) = reading
        
        assertEquals(1000L, timestamp)
        assertEquals(1f, x, 0.001f)
        assertEquals(2f, y, 0.001f)
        assertEquals(3f, z, 0.001f)
    }

    @Test
    fun `data classes implement toString`() {
        val reading = SensorReading(1000L, 72f)
        val toString = reading.toString()
        
        assertTrue(toString.contains("SensorReading"))
        assertTrue(toString.contains("1000"))
        assertTrue(toString.contains("72"))
    }
}
