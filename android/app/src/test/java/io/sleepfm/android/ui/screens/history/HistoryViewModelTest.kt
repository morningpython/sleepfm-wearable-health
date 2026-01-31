package io.sleepfm.android.ui.screens.history

import io.mockk.*
import io.sleepfm.android.data.repository.SleepRepository
import io.sleepfm.android.domain.model.SleepHistoryItem
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.time.LocalDate

@OptIn(ExperimentalCoroutinesApi::class)
class HistoryViewModelTest {

    private lateinit var viewModel: HistoryViewModel
    private lateinit var sleepRepository: SleepRepository
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        sleepRepository = mockk(relaxed = true)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    // ========== Initial State Tests ==========

    @Test
    fun `initial state should have empty sessions and loading false`() = runTest {
        // Given
        coEvery { sleepRepository.getAllSessions() } returns flowOf(emptyList())

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertTrue(state.sessions.isEmpty())
        assertFalse(state.isLoading)
        assertNull(state.error)
    }

    // ========== Load Sessions Tests ==========

    @Test
    fun `should load sessions from repository`() = runTest {
        // Given
        val sessions = listOf(
            createTestSession("1", LocalDate.of(2026, 1, 30)),
            createTestSession("2", LocalDate.of(2026, 1, 29))
        )
        coEvery { sleepRepository.getAllSessions() } returns flowOf(sessions)

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertEquals(2, state.sessions.size)
        assertEquals("1", state.sessions[0].id)
    }

    @Test
    fun `should show loading state while fetching sessions`() = runTest {
        // Given
        coEvery { sleepRepository.getAllSessions() } returns flowOf(emptyList())

        // When
        viewModel = HistoryViewModel(sleepRepository)

        // Then - check initial loading state before data loads
        assertTrue(viewModel.uiState.value.isLoading)
        
        advanceUntilIdle()
        assertFalse(viewModel.uiState.value.isLoading)
    }

    @Test
    fun `should show error when loading fails`() = runTest {
        // Given
        coEvery { sleepRepository.getAllSessions() } throws RuntimeException("Network error")

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertNotNull(state.error)
        assertTrue(state.error!!.contains("error") || state.error!!.contains("Error"))
    }

    // ========== Filter by Date Tests ==========

    @Test
    fun `filterByDate should filter sessions to selected date range`() = runTest {
        // Given
        val sessions = listOf(
            createTestSession("1", LocalDate.of(2026, 1, 30)),
            createTestSession("2", LocalDate.of(2026, 1, 25)),
            createTestSession("3", LocalDate.of(2026, 1, 20))
        )
        coEvery { sleepRepository.getAllSessions() } returns flowOf(sessions)
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // When - filter last 7 days from Jan 30
        viewModel.filterByDateRange(
            startDate = LocalDate.of(2026, 1, 24),
            endDate = LocalDate.of(2026, 1, 30)
        )
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertEquals(2, state.filteredSessions.size)
    }

    @Test
    fun `clearFilter should show all sessions`() = runTest {
        // Given
        val sessions = listOf(
            createTestSession("1", LocalDate.of(2026, 1, 30)),
            createTestSession("2", LocalDate.of(2026, 1, 20))
        )
        coEvery { sleepRepository.getAllSessions() } returns flowOf(sessions)
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()
        
        viewModel.filterByDateRange(
            startDate = LocalDate.of(2026, 1, 28),
            endDate = LocalDate.of(2026, 1, 30)
        )
        advanceUntilIdle()

        // When
        viewModel.clearFilter()
        advanceUntilIdle()

        // Then
        assertEquals(2, viewModel.uiState.value.filteredSessions.size)
    }

    // ========== Select Session Tests ==========

    @Test
    fun `selectSession should update selected session`() = runTest {
        // Given
        val sessions = listOf(createTestSession("1", LocalDate.of(2026, 1, 30)))
        coEvery { sleepRepository.getAllSessions() } returns flowOf(sessions)
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // When
        viewModel.selectSession(sessions[0])

        // Then
        assertEquals("1", viewModel.uiState.value.selectedSession?.id)
    }

    @Test
    fun `clearSelection should set selected session to null`() = runTest {
        // Given
        val sessions = listOf(createTestSession("1", LocalDate.of(2026, 1, 30)))
        coEvery { sleepRepository.getAllSessions() } returns flowOf(sessions)
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()
        viewModel.selectSession(sessions[0])

        // When
        viewModel.clearSelection()

        // Then
        assertNull(viewModel.uiState.value.selectedSession)
    }

    // ========== Refresh Tests ==========

    @Test
    fun `refresh should reload sessions from repository`() = runTest {
        // Given
        coEvery { sleepRepository.getAllSessions() } returns flowOf(emptyList())
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // When
        viewModel.refresh()
        advanceUntilIdle()

        // Then
        coVerify(atLeast = 2) { sleepRepository.getAllSessions() }
    }

    // ========== Helper Functions ==========

    private fun createTestSession(id: String, date: LocalDate): SleepHistoryItem {
        return SleepHistoryItem(
            id = id,
            date = date,
            bedTime = "23:00",
            wakeTime = "07:00",
            durationMinutes = 480,
            sleepScore = 85,
            deepMinutes = 120,
            lightMinutes = 240,
            remMinutes = 100,
            wakeMinutes = 20
        )
    }
}
