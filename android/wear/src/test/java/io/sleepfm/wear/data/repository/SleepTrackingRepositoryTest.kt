package io.sleepfm.wear.data.repository

import io.mockk.*
import io.mockk.impl.annotations.MockK
import io.sleepfm.wear.data.local.SleepDataStore
import io.sleepfm.wear.data.model.CollectedSleepData
import io.sleepfm.wear.data.model.SensorReading
import io.sleepfm.wear.data.model.SleepSession
import io.sleepfm.wear.service.SensorDataManager
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class SleepTrackingRepositoryTest {

    @MockK
    private lateinit var sensorDataManager: SensorDataManager

    @MockK
    private lateinit var sleepDataStore: SleepDataStore

    private lateinit var repository: SleepTrackingRepository

    private val isTrackingFlow = MutableStateFlow(false)

    @Before
    fun setUp() {
        MockKAnnotations.init(this, relaxed = true)
        
        every { sleepDataStore.isTracking } returns isTrackingFlow
        
        repository = SleepTrackingRepository(sensorDataManager, sleepDataStore)
    }

    @After
    fun tearDown() {
        unmockkAll()
    }

    // ========== startTracking Tests ==========

    @Test
    fun `startTracking should clear previous data`() = runTest {
        // Given
        coEvery { sleepDataStore.clearTrackingData() } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sleepDataStore.setTrackingStartTime(any()) } just Runs
        coEvery { sensorDataManager.startMeasurement() } just Runs

        // When
        repository.startTracking()

        // Then
        coVerify(exactly = 1) { sleepDataStore.clearTrackingData() }
    }

    @Test
    fun `startTracking should set isTracking to true`() = runTest {
        // Given
        coEvery { sleepDataStore.clearTrackingData() } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sleepDataStore.setTrackingStartTime(any()) } just Runs
        coEvery { sensorDataManager.startMeasurement() } just Runs

        // When
        repository.startTracking()

        // Then
        coVerify { sleepDataStore.setIsTracking(true) }
    }

    @Test
    fun `startTracking should save start time`() = runTest {
        // Given
        coEvery { sleepDataStore.clearTrackingData() } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sleepDataStore.setTrackingStartTime(any()) } just Runs
        coEvery { sensorDataManager.startMeasurement() } just Runs

        // When
        val beforeTime = System.currentTimeMillis()
        repository.startTracking()
        val afterTime = System.currentTimeMillis()

        // Then
        coVerify { 
            sleepDataStore.setTrackingStartTime(match { it in beforeTime..afterTime })
        }
    }

    @Test
    fun `startTracking should start sensor measurement`() = runTest {
        // Given
        coEvery { sleepDataStore.clearTrackingData() } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sleepDataStore.setTrackingStartTime(any()) } just Runs
        coEvery { sensorDataManager.startMeasurement() } just Runs

        // When
        repository.startTracking()

        // Then
        coVerify(exactly = 1) { sensorDataManager.startMeasurement() }
    }

    @Test
    fun `startTracking should update tracking state`() = runTest {
        // Given
        coEvery { sleepDataStore.clearTrackingData() } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sleepDataStore.setTrackingStartTime(any()) } just Runs
        coEvery { sensorDataManager.startMeasurement() } just Runs

        // When
        repository.startTracking()

        // Then
        val state = repository.trackingState.first()
        assertTrue(state.isTracking)
        assertNotNull(state.startTime)
    }

    // ========== stopTracking Tests ==========

    @Test
    fun `stopTracking should set end time`() = runTest {
        // Given
        val mockData = CollectedSleepData(
            startTime = System.currentTimeMillis() - 3600000,
            endTime = System.currentTimeMillis(),
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        coEvery { sleepDataStore.setTrackingEndTime(any()) } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sensorDataManager.stopMeasurement() } just Runs
        coEvery { sleepDataStore.getCollectedSleepData() } returns mockData

        // When
        val beforeTime = System.currentTimeMillis()
        repository.stopTracking()
        val afterTime = System.currentTimeMillis()

        // Then
        coVerify { 
            sleepDataStore.setTrackingEndTime(match { it in beforeTime..afterTime })
        }
    }

    @Test
    fun `stopTracking should set isTracking to false`() = runTest {
        // Given
        val mockData = CollectedSleepData(
            startTime = System.currentTimeMillis() - 3600000,
            endTime = System.currentTimeMillis(),
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        coEvery { sleepDataStore.setTrackingEndTime(any()) } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sensorDataManager.stopMeasurement() } just Runs
        coEvery { sleepDataStore.getCollectedSleepData() } returns mockData

        // When
        repository.stopTracking()

        // Then
        coVerify { sleepDataStore.setIsTracking(false) }
    }

    @Test
    fun `stopTracking should stop sensor measurement`() = runTest {
        // Given
        val mockData = CollectedSleepData(
            startTime = System.currentTimeMillis() - 3600000,
            endTime = System.currentTimeMillis(),
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        coEvery { sleepDataStore.setTrackingEndTime(any()) } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sensorDataManager.stopMeasurement() } just Runs
        coEvery { sleepDataStore.getCollectedSleepData() } returns mockData

        // When
        repository.stopTracking()

        // Then
        coVerify(exactly = 1) { sensorDataManager.stopMeasurement() }
    }

    @Test
    fun `stopTracking should return collected data`() = runTest {
        // Given
        val expectedData = CollectedSleepData(
            startTime = 1000L,
            endTime = 2000L,
            heartRateData = listOf(SensorReading(1500L, 72f)),
            spO2Data = listOf(SensorReading(1500L, 98f)),
            accelerometerData = emptyList()
        )
        coEvery { sleepDataStore.setTrackingEndTime(any()) } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sensorDataManager.stopMeasurement() } just Runs
        coEvery { sleepDataStore.getCollectedSleepData() } returns expectedData

        // When
        val result = repository.stopTracking()

        // Then
        assertEquals(expectedData, result)
    }

    @Test
    fun `stopTracking should update tracking state to not tracking`() = runTest {
        // Given
        val mockData = CollectedSleepData(
            startTime = System.currentTimeMillis() - 3600000,
            endTime = System.currentTimeMillis(),
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        coEvery { sleepDataStore.setTrackingEndTime(any()) } just Runs
        coEvery { sleepDataStore.setIsTracking(any()) } just Runs
        coEvery { sensorDataManager.stopMeasurement() } just Runs
        coEvery { sleepDataStore.getCollectedSleepData() } returns mockData

        // When
        repository.stopTracking()

        // Then
        val state = repository.trackingState.first()
        assertFalse(state.isTracking)
        assertNull(state.startTime)
    }

    // ========== saveHeartRateReading Tests ==========

    @Test
    fun `saveHeartRateReading should delegate to data store`() = runTest {
        // Given
        val reading = SensorReading(System.currentTimeMillis(), 75f)
        coEvery { sleepDataStore.saveHeartRateReadings(any()) } just Runs

        // When
        repository.saveHeartRateReading(reading)

        // Then
        coVerify { sleepDataStore.saveHeartRateReadings(listOf(reading)) }
    }

    // ========== saveSpO2Reading Tests ==========

    @Test
    fun `saveSpO2Reading should delegate to data store`() = runTest {
        // Given
        val reading = SensorReading(System.currentTimeMillis(), 97f)
        coEvery { sleepDataStore.saveSpO2Readings(any()) } just Runs

        // When
        repository.saveSpO2Reading(reading)

        // Then
        coVerify { sleepDataStore.saveSpO2Readings(listOf(reading)) }
    }

    // ========== saveSleepSession Tests ==========

    @Test
    fun `saveSleepSession should delegate to data store`() = runTest {
        // Given
        val session = createTestSession()
        coEvery { sleepDataStore.saveLastSession(any()) } just Runs

        // When
        repository.saveSleepSession(session)

        // Then
        coVerify { sleepDataStore.saveLastSession(session) }
    }

    // ========== getLastSession Tests ==========

    @Test
    fun `getLastSession should return session from data store`() = runTest {
        // Given
        val expectedSession = createTestSession()
        coEvery { sleepDataStore.getLastSession() } returns expectedSession

        // When
        val result = repository.getLastSession()

        // Then
        assertEquals(expectedSession, result)
    }

    @Test
    fun `getLastSession should return null when no session exists`() = runTest {
        // Given
        coEvery { sleepDataStore.getLastSession() } returns null

        // When
        val result = repository.getLastSession()

        // Then
        assertNull(result)
    }

    // ========== clearSession Tests ==========

    @Test
    fun `clearSession should delegate to data store`() = runTest {
        // Given
        coEvery { sleepDataStore.clearTrackingData() } just Runs

        // When
        repository.clearSession()

        // Then
        coVerify(exactly = 1) { sleepDataStore.clearTrackingData() }
    }
    
    // ========== Helper Functions ==========
    
    private fun createTestSession(): SleepSession {
        return SleepSession(
            id = "test-id",
            startTime = 1000L,
            endTime = 2000L,
            durationMinutes = 60,
            sleepScore = 85,
            bedTime = "23:00",
            wakeTime = "00:00",
            deepMinutes = 20,
            lightMinutes = 25,
            remMinutes = 10,
            wakeMinutes = 5,
            avgHeartRate = 62,
            avgSpO2 = 97,
            heartRateReadings = emptyList(),
            spO2Readings = emptyList()
        )
    }
}
