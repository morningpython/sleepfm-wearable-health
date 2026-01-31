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
}
