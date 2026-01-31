package io.sleepfm.wear.data.repository

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import io.sleepfm.wear.data.local.SleepDataStore
import io.sleepfm.wear.data.model.CollectedSleepData
import io.sleepfm.wear.data.model.SensorReading
import io.sleepfm.wear.data.model.SleepSession
import io.sleepfm.wear.service.SensorDataManager
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class SleepTrackingRepositoryTest {

    private lateinit var sensorDataManager: SensorDataManager
    private lateinit var sleepDataStore: SleepDataStore
    private lateinit var repository: SleepTrackingRepository

    @Before
    fun setup() {
        sensorDataManager = mockk(relaxed = true)
        sleepDataStore = mockk(relaxed = true)
        coEvery { sleepDataStore.isTracking } returns flowOf(false)
        repository = SleepTrackingRepository(sensorDataManager, sleepDataStore)
    }

    @Test
    fun `startTracking initializes tracking state and starts sensors`() = runTest {
        // When
        repository.startTracking()

        // Then
        coVerify { sleepDataStore.clearTrackingData() }
        coVerify { sleepDataStore.setIsTracking(true) }
        coVerify { sleepDataStore.setTrackingStartTime(any()) }
        coVerify { sensorDataManager.startMeasurement() }
        
        val state = repository.trackingState.value
        assertTrue(state.isTracking)
        assertNotNull(state.startTime)
    }

    @Test
    fun `stopTracking stops sensors and returns collected data`() = runTest {
        // Given
        val collectedData = CollectedSleepData(
            startTime = 1000L,
            endTime = 9000L,
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        coEvery { sleepDataStore.getCollectedSleepData() } returns collectedData

        // When
        val result = repository.stopTracking()

        // Then
        coVerify { sleepDataStore.setIsTracking(false) }
        coVerify { sensorDataManager.stopMeasurement() }
        assertEquals(collectedData, result)
        
        val state = repository.trackingState.value
        assertFalse(state.isTracking)
        assertNull(state.startTime)
    }

    @Test
    fun `saveHeartRateReading saves to data store`() = runTest {
        // Given
        val reading = SensorReading(
            timestamp = System.currentTimeMillis(),
            value = 72.0f
        )

        // When
        repository.saveHeartRateReading(reading)

        // Then
        coVerify { sleepDataStore.saveHeartRateReadings(listOf(reading)) }
    }

    @Test
    fun `saveSpO2Reading saves to data store`() = runTest {
        // Given
        val reading = SensorReading(
            timestamp = System.currentTimeMillis(),
            value = 98.0f
        )

        // When
        repository.saveSpO2Reading(reading)

        // Then
        coVerify { sleepDataStore.saveSpO2Readings(listOf(reading)) }
    }

    @Test
    fun `getLastSession returns session from data store`() = runTest {
        // Given
        val session = SleepSession(
            id = "session_1",
            startTime = 1000L,
            endTime = 9000L,
            durationMinutes = 133,
            sleepScore = 85,
            bedTime = "23:00",
            wakeTime = "07:00",
            deepMinutes = 60,
            lightMinutes = 30,
            remMinutes = 30,
            wakeMinutes = 13,
            avgHeartRate = 68,
            avgSpO2 = 97,
            heartRateReadings = emptyList(),
            spO2Readings = emptyList(),
            synced = false
        )
        coEvery { sleepDataStore.getLastSession() } returns session

        // When
        val result = repository.getLastSession()

        // Then
        assertEquals(session, result)
    }

    @Test
    fun `clearSession clears data store`() = runTest {
        // When
        repository.clearSession()

        // Then
        coVerify { sleepDataStore.clearTrackingData() }
    }

    @Test
    fun `initial trackingState is not tracking`() = runTest {
        // Then
        val state = repository.trackingState.value
        assertFalse(state.isTracking)
        assertNull(state.startTime)
    }

    @Test
    fun `startTracking sets startTime to current time`() = runTest {
        // Given
        val beforeStart = System.currentTimeMillis()

        // When
        repository.startTracking()

        // Then
        val state = repository.trackingState.value
        assertNotNull(state.startTime)
        assertTrue(state.startTime!! >= beforeStart)
    }

    @Test
    fun `stopTracking returns empty data when no readings collected`() = runTest {
        // Given
        val emptyData = CollectedSleepData(
            startTime = 0L,
            endTime = 1000L,
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        coEvery { sleepDataStore.getCollectedSleepData() } returns emptyData

        // When
        val result = repository.stopTracking()

        // Then
        assertTrue(result.heartRateData.isEmpty())
        assertTrue(result.spO2Data.isEmpty())
        assertTrue(result.accelerometerData.isEmpty())
    }

    @Test
    fun `multiple startTracking calls are idempotent`() = runTest {
        // When
        repository.startTracking()
        val firstState = repository.trackingState.value
        
        repository.startTracking()
        val secondState = repository.trackingState.value

        // Then - both should be tracking
        assertTrue(firstState.isTracking)
        assertTrue(secondState.isTracking)
    }

    @Test
    fun `getLastSession returns null when no session exists`() = runTest {
        // Given
        coEvery { sleepDataStore.getLastSession() } returns null

        // When
        val result = repository.getLastSession()

        // Then
        assertNull(result)
    }

    @Test
    fun `saveHeartRateReading with multiple readings`() = runTest {
        // Given
        val readings = listOf(
            SensorReading(timestamp = 1000L, value = 70f),
            SensorReading(timestamp = 2000L, value = 72f),
            SensorReading(timestamp = 3000L, value = 68f)
        )

        // When
        readings.forEach { repository.saveHeartRateReading(it) }

        // Then
        readings.forEach { reading ->
            coVerify { sleepDataStore.saveHeartRateReadings(listOf(reading)) }
        }
    }

    @Test
    fun `saveSpO2Reading with multiple readings`() = runTest {
        // Given
        val readings = listOf(
            SensorReading(timestamp = 1000L, value = 98f),
            SensorReading(timestamp = 2000L, value = 97f),
            SensorReading(timestamp = 3000L, value = 99f)
        )

        // When
        readings.forEach { repository.saveSpO2Reading(it) }

        // Then
        readings.forEach { reading ->
            coVerify { sleepDataStore.saveSpO2Readings(listOf(reading)) }
        }
    }
}
