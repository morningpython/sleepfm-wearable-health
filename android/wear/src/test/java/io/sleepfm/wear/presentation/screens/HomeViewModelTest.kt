package io.sleepfm.wear.presentation.screens

import io.mockk.*
import io.mockk.impl.annotations.MockK
import io.sleepfm.wear.data.model.SensorReading
import io.sleepfm.wear.data.repository.PhoneConnectionRepository
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class HomeViewModelTest {

    @MockK
    private lateinit var sleepTrackingRepository: SleepTrackingRepository

    @MockK
    private lateinit var phoneConnectionRepository: PhoneConnectionRepository

    private lateinit var viewModel: HomeViewModel

    private val testDispatcher = StandardTestDispatcher()
    
    private val isTrackingFlow = MutableStateFlow(false)
    private val connectionStatusFlow = MutableStateFlow(
        PhoneConnectionRepository.ConnectionStatus(isConnected = false)
    )

    @Before
    fun setUp() {
        MockKAnnotations.init(this, relaxed = true)
        Dispatchers.setMain(testDispatcher)

        every { sleepTrackingRepository.isTracking } returns isTrackingFlow
        every { phoneConnectionRepository.connectionStatus } returns connectionStatusFlow

        viewModel = HomeViewModel(sleepTrackingRepository, phoneConnectionRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        unmockkAll()
    }

    // ========== Initial State Tests ==========

    @Test
    fun `initial state should not be tracking`() = runTest {
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertFalse(state.isTracking)
    }

    @Test
    fun `initial state should not be loading`() = runTest {
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertFalse(state.isLoading)
    }

    // ========== startTracking Tests ==========

    @Test
    fun `startTracking should call repository`() = runTest {
        coEvery { sleepTrackingRepository.startTracking() } just Runs

        viewModel.startTracking()
        advanceUntilIdle()

        coVerify(exactly = 1) { sleepTrackingRepository.startTracking() }
    }

    @Test
    fun `startTracking should set loading state`() = runTest {
        coEvery { sleepTrackingRepository.startTracking() } coAnswers {
            // Simulate delay
            kotlinx.coroutines.delay(100)
        }

        viewModel.startTracking()
        
        // Check loading state during operation
        val stateWhileLoading = viewModel.uiState.first()
        assertTrue(stateWhileLoading.isLoading)
    }

    @Test
    fun `startTracking should handle error`() = runTest {
        val exception = RuntimeException("Sensor error")
        coEvery { sleepTrackingRepository.startTracking() } throws exception

        viewModel.startTracking()
        advanceUntilIdle()

        val state = viewModel.uiState.first()
        assertFalse(state.isLoading)
        assertNotNull(state.error)
    }

    // ========== stopTracking Tests ==========

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

    // ========== Connection State Tests ==========

    @Test
    fun `should reflect phone connection status`() = runTest {
        connectionStatusFlow.value = PhoneConnectionRepository.ConnectionStatus(
            isConnected = true,
            connectedNodeId = "test-node"
        )
        
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertTrue(state.isPhoneConnected)
    }

    @Test
    fun `should show disconnected when phone not connected`() = runTest {
        connectionStatusFlow.value = PhoneConnectionRepository.ConnectionStatus(
            isConnected = false
        )
        
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertFalse(state.isPhoneConnected)
    }

    // ========== Tracking State Flow Tests ==========

    @Test
    fun `should update when tracking state changes`() = runTest {
        isTrackingFlow.value = true
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertTrue(state.isTracking)
    }

    @Test
    fun `should update when tracking stops`() = runTest {
        isTrackingFlow.value = true
        advanceUntilIdle()
        
        isTrackingFlow.value = false
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        assertFalse(state.isTracking)
    }

    // ========== Error Handling Tests ==========

    @Test
    fun `clearError should remove error from state`() = runTest {
        // First, trigger an error
        coEvery { sleepTrackingRepository.startTracking() } throws RuntimeException("Error")
        viewModel.startTracking()
        advanceUntilIdle()
        
        // Verify error exists
        var state = viewModel.uiState.first()
        assertNotNull(state.error)
        
        // Clear error
        viewModel.clearError()
        advanceUntilIdle()
        
        // Verify error is cleared
        state = viewModel.uiState.first()
        assertNull(state.error)
    }
}
