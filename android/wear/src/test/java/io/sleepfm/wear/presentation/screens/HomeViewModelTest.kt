package io.sleepfm.wear.presentation.screens

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.sleepfm.wear.data.model.SleepSession
import io.sleepfm.wear.data.repository.PhoneConnectionRepository
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
class HomeViewModelTest {

    private lateinit var sleepTrackingRepository: SleepTrackingRepository
    private lateinit var phoneConnectionRepository: PhoneConnectionRepository
    private lateinit var viewModel: HomeViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        sleepTrackingRepository = mockk(relaxed = true)
        phoneConnectionRepository = mockk(relaxed = true)
        
        every { sleepTrackingRepository.isTracking } returns flowOf(false)
        every { phoneConnectionRepository.connectionStatus } returns flowOf(
            PhoneConnectionRepository.ConnectionStatus(isConnected = false)
        )
        coEvery { sleepTrackingRepository.getLastSession() } returns null
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state is not tracking`() = runTest {
        viewModel = HomeViewModel(sleepTrackingRepository, phoneConnectionRepository)
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertFalse(state.isTracking)
        assertFalse(state.isLoading)
        assertNull(state.error)
    }

    @Test
    fun `observes tracking state changes`() = runTest {
        val trackingFlow = MutableStateFlow(false)
        every { sleepTrackingRepository.isTracking } returns trackingFlow
        
        viewModel = HomeViewModel(sleepTrackingRepository, phoneConnectionRepository)
        advanceUntilIdle()
        
        assertFalse(viewModel.uiState.value.isTracking)
        
        // When tracking starts
        trackingFlow.value = true
        advanceUntilIdle()
        
        assertTrue(viewModel.uiState.value.isTracking)
    }

    @Test
    fun `observes phone connection status`() = runTest {
        val connectionFlow = MutableStateFlow(
            PhoneConnectionRepository.ConnectionStatus(isConnected = false)
        )
        every { phoneConnectionRepository.connectionStatus } returns connectionFlow
        
        viewModel = HomeViewModel(sleepTrackingRepository, phoneConnectionRepository)
        advanceUntilIdle()
        
        assertFalse(viewModel.uiState.value.isPhoneConnected)
        
        // When phone connects
        connectionFlow.value = PhoneConnectionRepository.ConnectionStatus(isConnected = true)
        advanceUntilIdle()
        
        assertTrue(viewModel.uiState.value.isPhoneConnected)
    }

    @Test
    fun `loads last sleep data on init`() = runTest {
        val session = mockk<SleepSession>(relaxed = true) {
            every { durationMinutes } returns 480 // 8 hours
        }
        coEvery { sleepTrackingRepository.getLastSession() } returns session
        
        viewModel = HomeViewModel(sleepTrackingRepository, phoneConnectionRepository)
        advanceUntilIdle()
        
        assertEquals("8시간 0분", viewModel.uiState.value.lastSleepDuration)
    }

    @Test
    fun `startTracking calls repository`() = runTest {
        viewModel = HomeViewModel(sleepTrackingRepository, phoneConnectionRepository)
        advanceUntilIdle()
        
        viewModel.startTracking()
        advanceUntilIdle()
        
        coVerify { sleepTrackingRepository.startTracking() }
    }

    @Test
    fun `startTracking shows error on failure`() = runTest {
        coEvery { sleepTrackingRepository.startTracking() } throws Exception("Sensor error")
        
        viewModel = HomeViewModel(sleepTrackingRepository, phoneConnectionRepository)
        advanceUntilIdle()
        
        viewModel.startTracking()
        advanceUntilIdle()
        
        assertNotNull(viewModel.uiState.value.error)
    }
}
