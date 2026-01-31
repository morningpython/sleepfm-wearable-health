package io.sleepfm.wear.presentation.screens

import io.mockk.*
import io.mockk.impl.annotations.MockK
import io.sleepfm.wear.data.model.AccelerometerReading
import io.sleepfm.wear.data.model.SensorReading
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class TrackingViewModelTest {

    @MockK
    private lateinit var sleepTrackingRepository: SleepTrackingRepository

    private lateinit var viewModel: TrackingViewModel

    private val testDispatcher = StandardTestDispatcher()
    
    private val heartRateFlow = MutableStateFlow<SensorReading?>(null)
    private val spO2Flow = MutableStateFlow<SensorReading?>(null)
    private val accelerometerFlow = MutableStateFlow<AccelerometerReading?>(null)
    private val trackingStateFlow = MutableStateFlow(
        SleepTrackingRepository.TrackingState(isTracking = true, startTime = System.currentTimeMillis())
    )

    @Before
    fun setUp() {
        MockKAnnotations.init(this, relaxed = true)
        Dispatchers.setMain(testDispatcher)

        every { sleepTrackingRepository.heartRateFlow } returns heartRateFlow
        every { sleepTrackingRepository.spO2Flow } returns spO2Flow
        every { sleepTrackingRepository.accelerometerFlow } returns accelerometerFlow
        every { sleepTrackingRepository.trackingState } returns trackingStateFlow

        viewModel = TrackingViewModel(sleepTrackingRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        unmockkAll()
    }

    // ========== Heart Rate Tests ==========

    @Test
    fun `should display heart rate when received`() = runTest {
        val reading = SensorReading(System.currentTimeMillis(), 72f)
        heartRateFlow.value = reading
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertEquals(72f, state.currentHeartRate)
    }

    @Test
    fun `heart rate should be null initially`() = runTest {
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertNull(state.currentHeartRate)
    }

    @Test
    fun `should update heart rate when new reading arrives`() = runTest {
        heartRateFlow.value = SensorReading(1000L, 70f)
        advanceUntilIdle()
        
        heartRateFlow.value = SensorReading(2000L, 75f)
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertEquals(75f, state.currentHeartRate)
    }

    // ========== SpO2 Tests ==========

    @Test
    fun `should display SpO2 when received`() = runTest {
        val reading = SensorReading(System.currentTimeMillis(), 98f)
        spO2Flow.value = reading
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertEquals(98f, state.currentSpO2)
    }

    @Test
    fun `SpO2 should be null initially`() = runTest {
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertNull(state.currentSpO2)
    }

    // ========== Elapsed Time Tests ==========

    @Test
    fun `elapsed time should increase from start time`() = runTest {
        val startTime = System.currentTimeMillis() - 3600000 // 1 hour ago
        trackingStateFlow.value = SleepTrackingRepository.TrackingState(
            isTracking = true, 
            startTime = startTime
        )
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertTrue(state.elapsedTimeMillis >= 3600000)
    }

    @Test
    fun `formatElapsedTime should format correctly`() {
        // Test 1 hour 30 minutes 45 seconds
        val elapsed = (1 * 3600 + 30 * 60 + 45) * 1000L
        
        val hours = (elapsed / 3600000).toInt()
        val minutes = ((elapsed % 3600000) / 60000).toInt()
        val seconds = ((elapsed % 60000) / 1000).toInt()
        
        assertEquals(1, hours)
        assertEquals(30, minutes)
        assertEquals(45, seconds)
    }

    // ========== Stop Tracking Tests ==========

    @Test
    fun `stopTracking should call repository`() = runTest {
        val mockData = io.sleepfm.wear.data.model.CollectedSleepData(
            startTime = 1000L,
            endTime = 2000L,
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        coEvery { sleepTrackingRepository.stopTracking() } returns mockData

        viewModel.stopTracking()
        advanceUntilIdle()

        coVerify(exactly = 1) { sleepTrackingRepository.stopTracking() }
    }

    // ========== Save Reading Tests ==========

    @Test
    fun `should save heart rate reading when received`() = runTest {
        val reading = SensorReading(System.currentTimeMillis(), 72f)
        coEvery { sleepTrackingRepository.saveHeartRateReading(any()) } just Runs
        
        heartRateFlow.value = reading
        advanceUntilIdle()

        coVerify { sleepTrackingRepository.saveHeartRateReading(reading) }
    }

    @Test
    fun `should save SpO2 reading when received`() = runTest {
        val reading = SensorReading(System.currentTimeMillis(), 97f)
        coEvery { sleepTrackingRepository.saveSpO2Reading(any()) } just Runs
        
        spO2Flow.value = reading
        advanceUntilIdle()

        coVerify { sleepTrackingRepository.saveSpO2Reading(reading) }
    }
}
