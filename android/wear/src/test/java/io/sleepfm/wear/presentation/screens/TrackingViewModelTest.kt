package io.sleepfm.wear.presentation.screens

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.sleepfm.wear.data.model.SensorReading
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class TrackingViewModelTest {

    private lateinit var sleepTrackingRepository: SleepTrackingRepository
    private lateinit var viewModel: TrackingViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        sleepTrackingRepository = mockk(relaxed = true)
        
        every { sleepTrackingRepository.heartRateFlow } returns flowOf(null)
        every { sleepTrackingRepository.spO2Flow } returns flowOf(null)
        every { sleepTrackingRepository.trackingState } returns MutableStateFlow(
            SleepTrackingRepository.TrackingState(isTracking = false)
        )
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state shows zero elapsed time`() = runTest {
        viewModel = TrackingViewModel(sleepTrackingRepository)
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertEquals("00:00:00", state.elapsedTime)
        assertEquals(0L, state.elapsedTimeMillis)
    }

    @Test
    fun `observes heart rate readings`() = runTest {
        val heartRateFlow = MutableStateFlow<SensorReading?>(null)
        every { sleepTrackingRepository.heartRateFlow } returns heartRateFlow
        
        viewModel = TrackingViewModel(sleepTrackingRepository)
        advanceUntilIdle()
        
        assertNull(viewModel.uiState.value.currentHeartRate)
        
        // When heart rate reading comes in
        val reading = SensorReading(timestamp = System.currentTimeMillis(), value = 72f)
        heartRateFlow.value = reading
        advanceUntilIdle()
        
        assertEquals(72f, viewModel.uiState.value.currentHeartRate)
        coVerify { sleepTrackingRepository.saveHeartRateReading(reading) }
    }

    @Test
    fun `observes SpO2 readings`() = runTest {
        val spO2Flow = MutableStateFlow<SensorReading?>(null)
        every { sleepTrackingRepository.spO2Flow } returns spO2Flow
        
        viewModel = TrackingViewModel(sleepTrackingRepository)
        advanceUntilIdle()
        
        assertNull(viewModel.uiState.value.currentSpO2)
        
        // When SpO2 reading comes in
        val reading = SensorReading(timestamp = System.currentTimeMillis(), value = 98f)
        spO2Flow.value = reading
        advanceUntilIdle()
        
        assertEquals(98f, viewModel.uiState.value.currentSpO2)
        coVerify { sleepTrackingRepository.saveSpO2Reading(reading) }
    }

    @Test
    fun `no sensor values when readings are null`() = runTest {
        every { sleepTrackingRepository.heartRateFlow } returns flowOf(null)
        every { sleepTrackingRepository.spO2Flow } returns flowOf(null)
        
        viewModel = TrackingViewModel(sleepTrackingRepository)
        advanceUntilIdle()
        
        assertNull(viewModel.uiState.value.currentHeartRate)
        assertNull(viewModel.uiState.value.currentSpO2)
    }
}
