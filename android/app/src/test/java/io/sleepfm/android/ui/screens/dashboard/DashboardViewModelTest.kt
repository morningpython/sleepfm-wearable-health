package io.sleepfm.android.ui.screens.dashboard

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.sleepfm.android.data.local.entity.SleepSessionEntity
import io.sleepfm.android.data.repository.SleepRepository
import io.sleepfm.android.domain.model.SleepSession
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.util.Date

@OptIn(ExperimentalCoroutinesApi::class)
class DashboardViewModelTest {

    private lateinit var sleepRepository: SleepRepository
    private lateinit var viewModel: DashboardViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        sleepRepository = mockk(relaxed = true)
        coEvery { sleepRepository.getLatestLocalSession() } returns null
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state shows no data when no sessions`() = runTest {
        // Given
        coEvery { sleepRepository.getLatestLocalSession() } returns null
        
        // When
        viewModel = DashboardViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.hasLastNightData)
        assertEquals(0, state.sleepScore)
    }

    @Test
    fun `syncData calls repository getHistory`() = runTest {
        // Given
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(emptyList())
        viewModel = DashboardViewModel(sleepRepository)
        advanceUntilIdle()

        // When
        viewModel.syncData()
        advanceUntilIdle()

        // Then
        coVerify { sleepRepository.getHistory(any()) }
    }

    @Test
    fun `syncData shows error on failure`() = runTest {
        // Given
        coEvery { sleepRepository.getHistory(any()) } returns Result.failure(
            Exception("Network error")
        )
        viewModel = DashboardViewModel(sleepRepository)
        advanceUntilIdle()

        // When
        viewModel.syncData()
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals("Network error", state.error)
    }

    @Test
    fun `syncData shows no data message when empty`() = runTest {
        // Given
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(emptyList())
        viewModel = DashboardViewModel(sleepRepository)
        advanceUntilIdle()

        // When
        viewModel.syncData()
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertFalse(state.hasLastNightData)
        assertEquals(0, state.sleepScore)
    }

    @Test
    fun `syncData shows loading during operation`() = runTest {
        // Given
        coEvery { sleepRepository.getHistory(any()) } coAnswers {
            kotlinx.coroutines.delay(100)
            Result.success(emptyList())
        }
        viewModel = DashboardViewModel(sleepRepository)
        advanceUntilIdle()

        // When
        viewModel.syncData()
        testDispatcher.scheduler.advanceTimeBy(50)

        // Then - should be loading
        assertTrue(viewModel.uiState.value.isLoading)

        // Complete
        advanceUntilIdle()
        assertFalse(viewModel.uiState.value.isLoading)
    }
}
