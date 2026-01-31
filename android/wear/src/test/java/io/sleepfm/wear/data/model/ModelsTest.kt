package io.sleepfm.wear.data.model

import org.junit.Assert.*
import org.junit.Test

class ModelsTest {

    // ========== SensorReading Tests ==========

    @Test
    fun `SensorReading should store timestamp and value`() {
        val reading = SensorReading(
            timestamp = 1706600000000L,
            value = 72.5f
        )

        assertEquals(1706600000000L, reading.timestamp)
        assertEquals(72.5f, reading.value, 0.001f)
    }

    @Test
    fun `SensorReading equality should work`() {
        val reading1 = SensorReading(1000L, 72f)
        val reading2 = SensorReading(1000L, 72f)
        val reading3 = SensorReading(1000L, 73f)

        assertEquals(reading1, reading2)
        assertNotEquals(reading1, reading3)
    }

    // ========== SleepSession Tests ==========

    @Test
    fun `SleepSession should store all fields`() {
        val heartRateReadings = listOf(SensorReading(1000L, 65f), SensorReading(2000L, 62f))
        val spO2Readings = listOf(SensorReading(1500L, 97f))
        
        val session = SleepSession(
            id = "session-123",
            startTime = 1000L,
            endTime = 2000L,
            durationMinutes = 480,
            sleepScore = 85,
            bedTime = "23:00",
            wakeTime = "07:00",
            deepMinutes = 120,
            lightMinutes = 240,
            remMinutes = 100,
            wakeMinutes = 20,
            avgHeartRate = 62,
            avgSpO2 = 97,
            heartRateReadings = heartRateReadings,
            spO2Readings = spO2Readings
        )

        assertEquals("session-123", session.id)
        assertEquals(1000L, session.startTime)
        assertEquals(2000L, session.endTime)
        assertEquals(480, session.durationMinutes)
        assertEquals(85, session.sleepScore)
        assertEquals("23:00", session.bedTime)
        assertEquals("07:00", session.wakeTime)
        assertEquals(120, session.deepMinutes)
        assertEquals(240, session.lightMinutes)
        assertEquals(100, session.remMinutes)
        assertEquals(20, session.wakeMinutes)
        assertEquals(62, session.avgHeartRate)
        assertEquals(97, session.avgSpO2)
        assertEquals(2, session.heartRateReadings.size)
        assertEquals(1, session.spO2Readings.size)
        assertFalse(session.synced)
    }

    @Test
    fun `SleepSession synced default should be false`() {
        val session = createTestSession()
        assertFalse(session.synced)
    }
    
    @Test
    fun `SleepSession synced can be set to true`() {
        val session = createTestSession().copy(synced = true)
        assertTrue(session.synced)
    }

    // ========== CollectedSleepData Tests ==========

    @Test
    fun `CollectedSleepData should store all sensor data`() {
        val heartRateData = listOf(
            SensorReading(1000L, 72f),
            SensorReading(2000L, 68f)
        )
        val spO2Data = listOf(
            SensorReading(1500L, 97f)
        )
        val accelData = listOf(
            AccelerometerReading(1000L, 0.1f, 0.2f, 9.8f)
        )

        val data = CollectedSleepData(
            startTime = 1000L,
            endTime = 3000L,
            heartRateData = heartRateData,
            spO2Data = spO2Data,
            accelerometerData = accelData
        )

        assertEquals(1000L, data.startTime)
        assertEquals(3000L, data.endTime)
        assertEquals(2, data.heartRateData.size)
        assertEquals(1, data.spO2Data.size)
        assertEquals(1, data.accelerometerData.size)
    }

    @Test
    fun `CollectedSleepData duration calculation`() {
        val data = CollectedSleepData(
            startTime = 1000L,
            endTime = 3600001L, // 1 hour + 1ms
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )

        val durationMs = data.endTime - data.startTime
        val durationMinutes = durationMs / 60000

        assertEquals(60, durationMinutes)
    }

    // ========== AccelerometerReading Tests ==========

    @Test
    fun `AccelerometerReading should store xyz values`() {
        val reading = AccelerometerReading(
            timestamp = 1000L,
            x = 0.5f,
            y = -0.3f,
            z = 9.81f
        )

        assertEquals(1000L, reading.timestamp)
        assertEquals(0.5f, reading.x, 0.001f)
        assertEquals(-0.3f, reading.y, 0.001f)
        assertEquals(9.81f, reading.z, 0.001f)
    }

    @Test
    fun `AccelerometerReading magnitude calculation`() {
        val reading = AccelerometerReading(
            timestamp = 1000L,
            x = 3f,
            y = 4f,
            z = 0f
        )

        // Magnitude = sqrt(x^2 + y^2 + z^2)
        val magnitude = kotlin.math.sqrt(
            reading.x * reading.x + 
            reading.y * reading.y + 
            reading.z * reading.z
        )

        assertEquals(5f, magnitude, 0.001f)
    }

    @Test
    fun `AccelerometerReading at rest should be approximately 9_8`() {
        // When device is at rest, accelerometer reads gravity
        val reading = AccelerometerReading(
            timestamp = 1000L,
            x = 0f,
            y = 0f,
            z = 9.81f
        )

        val magnitude = kotlin.math.sqrt(
            reading.x * reading.x + 
            reading.y * reading.y + 
            reading.z * reading.z
        )

        assertEquals(9.81f, magnitude, 0.1f)
    }
    
    // ========== Helper Functions ==========
    
    private fun createTestSession(): SleepSession {
        return SleepSession(
            id = "test-session",
            startTime = 1000L,
            endTime = 2000L,
            durationMinutes = 480,
            sleepScore = 85,
            bedTime = "23:00",
            wakeTime = "07:00",
            deepMinutes = 120,
            lightMinutes = 240,
            remMinutes = 100,
            wakeMinutes = 20,
            avgHeartRate = 62,
            avgSpO2 = 97,
            heartRateReadings = emptyList(),
            spO2Readings = emptyList()
        )
    }
}
