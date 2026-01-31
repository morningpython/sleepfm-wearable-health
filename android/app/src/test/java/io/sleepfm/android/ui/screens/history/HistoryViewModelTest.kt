package io.sleepfm.android.ui.screens.history

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
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

@OptIn(ExperimentalCoroutinesApi::class)
class HistoryViewModelTest {

    private lateinit var sleepRepository: SleepRepository
    private lateinit var viewModel: HistoryViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        sleepRepository = mockk(relaxed = true)
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(emptyList())
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state is loading then shows empty`() = runTest {
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertTrue(state.sessions.isEmpty())
        assertNull(state.error)
    }

    @Test
    fun `loadHistory shows sessions on success`() = runTest {
        // Given
        val sessions = listOf(
            SleepSession(
                id = 1,
                userId = 1,
                startTime = "2026-01-30T23:00:00",
                endTime = "2026-01-31T07:00:00",
                durationMinutes = 480,
                sleepQuality = 0.85f,
                efficiency = 0.92f,
                createdAt = "2026-01-30T23:00:00"
            ),
            SleepSession(
                id = 2,
                userId = 1,
                startTime = "2026-01-29T22:30:00",
                endTime = "2026-01-30T06:30:00",
                durationMinutes = 480,
                sleepQuality = 0.75f,
                efficiency = 0.88f,
                createdAt = "2026-01-29T22:30:00"
            )
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(sessions)

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals(2, state.sessions.size)
    }

    @Test
    fun `loadHistory shows error on failure`() = runTest {
        // Given
        coEvery { sleepRepository.getHistory(any()) } returns Result.failure(
            Exception("Network error")
        )

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then - error is set (loading may be false due to fallback)
        val state = viewModel.uiState.value
        assertEquals("Network error", state.error)
    }

    @Test
    fun `refresh calls loadHistory again`() = runTest {
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(emptyList())
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // When
        viewModel.refresh()
        advanceUntilIdle()

        // Then - should call getHistory twice (init + refresh)
        coVerify(exactly = 2) { sleepRepository.getHistory(any()) }
    }

    @Test
    fun `loadHistory shows loading during operation`() = runTest {
        coEvery { sleepRepository.getHistory(any()) } coAnswers {
            kotlinx.coroutines.delay(100)
            Result.success(emptyList())
        }
        viewModel = HistoryViewModel(sleepRepository)

        // Advance partially
        testDispatcher.scheduler.advanceTimeBy(50)

        // Should be loading
        assertTrue(viewModel.uiState.value.isLoading)

        // Complete
        advanceUntilIdle()
        assertFalse(viewModel.uiState.value.isLoading)
    }

    @Test
    fun `sessions are transformed correctly with all fields`() = runTest {
        // Given - session with all data
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:30:00",
            endTime = "2024-06-02T06:30:00",
            durationMinutes = 480,
            sleepQuality = 0.92f,
            efficiency = 0.95f,
            createdAt = "2024-06-02T06:30:00"
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertEquals(1, state.sessions.size)
        val historySession = state.sessions.first()
        assertEquals(1, historySession.id)
        assertEquals(95, historySession.efficiency)
        assertEquals("excellent", historySession.quality) // 0.92 >= 0.85
    }

    @Test
    fun `session quality is categorized correctly`() = runTest {
        // Given - sessions with different quality scores
        val sessions = listOf(
            SleepSession(1, 1, "2024-06-01T22:00:00", "2024-06-02T06:00:00", 480, 0.95f, 0.9f, null),
            SleepSession(2, 1, "2024-05-31T22:00:00", "2024-06-01T06:00:00", 480, 0.80f, 0.85f, null),
            SleepSession(3, 1, "2024-05-30T22:00:00", "2024-05-31T06:00:00", 480, 0.65f, 0.7f, null),
            SleepSession(4, 1, "2024-05-29T22:00:00", "2024-05-30T06:00:00", 480, 0.45f, 0.5f, null)
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(sessions)

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySessions = viewModel.uiState.value.sessions
        assertEquals("excellent", historySessions[0].quality) // >= 0.85
        assertEquals("good", historySessions[1].quality) // >= 0.70
        assertEquals("fair", historySessions[2].quality) // >= 0.55
        assertEquals("poor", historySessions[3].quality) // < 0.55
    }

    @Test
    fun `session with null endTime shows placeholder`() = runTest {
        // Given - session in progress
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = null,
            durationMinutes = null,
            sleepQuality = null,
            efficiency = null,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("--:--", historySession.wakeTime)
    }

    @Test
    fun `duration is formatted correctly`() = runTest {
        // Given - session with 8 hours 30 minutes
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:30:00",
            durationMinutes = 510, // 8h 30m
            sleepQuality = 0.8f,
            efficiency = 0.85f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertTrue(historySession.durationString.contains("8") && historySession.durationString.contains("30"))
    }

    @Test
    fun `error is cleared on successful refresh`() = runTest {
        // Given - first call fails, second succeeds
        coEvery { sleepRepository.getHistory(any()) } returnsMany listOf(
            Result.failure(Exception("Network error")),
            Result.success(emptyList())
        )
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()
        
        // Should have error
        assertEquals("Network error", viewModel.uiState.value.error)

        // When - refresh
        viewModel.refresh()
        advanceUntilIdle()

        // Then - error should be cleared
        assertNull(viewModel.uiState.value.error)
    }

    @Test
    fun `multiple sessions are ordered correctly`() = runTest {
        // Given - multiple sessions
        val sessions = listOf(
            SleepSession(3, 1, "2024-06-03T22:00:00", "2024-06-04T06:00:00", 480, 0.8f, 0.85f, null),
            SleepSession(2, 1, "2024-06-02T22:00:00", "2024-06-03T06:00:00", 480, 0.75f, 0.8f, null),
            SleepSession(1, 1, "2024-06-01T22:00:00", "2024-06-02T06:00:00", 480, 0.7f, 0.75f, null)
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(sessions)

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then - sessions should maintain order from API
        val historySessions = viewModel.uiState.value.sessions
        assertEquals(3, historySessions.size)
        assertEquals(3, historySessions[0].id)
        assertEquals(2, historySessions[1].id)
        assertEquals(1, historySessions[2].id)
    }

    @Test
    fun `formatDuration with hours and minutes`() = runTest {
        // Given - 7 hours 45 minutes (465 minutes)
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T05:45:00",
            durationMinutes = 465,
            sleepQuality = 0.8f,
            efficiency = 0.85f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("7시간 45분", historySession.durationString)
    }

    @Test
    fun `formatDuration with only minutes`() = runTest {
        // Given - 45 minutes
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-01T22:45:00",
            durationMinutes = 45,
            sleepQuality = 0.5f,
            efficiency = 0.6f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("45분", historySession.durationString)
    }

    @Test
    fun `formatDuration with zero minutes`() = runTest {
        // Given - 0 minutes
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-01T22:00:00",
            durationMinutes = 0,
            sleepQuality = 0f,
            efficiency = 0f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("0분", historySession.durationString)
    }

    @Test
    fun `formatDuration with exact hours`() = runTest {
        // Given - exactly 8 hours (480 minutes)
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:00:00",
            durationMinutes = 480,
            sleepQuality = 0.85f,
            efficiency = 0.9f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("8시간 0분", historySession.durationString)
    }

    @Test
    fun `quality mapping boundary at 0_85`() = runTest {
        // Given - exactly 0.85 quality
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:00:00",
            durationMinutes = 480,
            sleepQuality = 0.85f,
            efficiency = 0.9f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("excellent", historySession.quality)
    }

    @Test
    fun `quality mapping boundary at 0_70`() = runTest {
        // Given - exactly 0.70 quality
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:00:00",
            durationMinutes = 480,
            sleepQuality = 0.70f,
            efficiency = 0.75f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("good", historySession.quality)
    }

    @Test
    fun `quality mapping boundary at 0_50`() = runTest {
        // Given - exactly 0.50 quality
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:00:00",
            durationMinutes = 480,
            sleepQuality = 0.50f,
            efficiency = 0.55f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("fair", historySession.quality)
    }

    @Test
    fun `quality mapping poor for very low scores`() = runTest {
        // Given - very low quality (0.1)
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:00:00",
            durationMinutes = 480,
            sleepQuality = 0.1f,
            efficiency = 0.2f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("poor", historySession.quality)
    }

    @Test
    fun `session with null quality defaults to 0`() = runTest {
        // Given - null quality
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:00:00",
            durationMinutes = 480,
            sleepQuality = null,
            efficiency = 0.8f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("poor", historySession.quality) // 0 maps to poor
    }

    @Test
    fun `session with null efficiency defaults to 0`() = runTest {
        // Given - null efficiency
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:00:00",
            durationMinutes = 480,
            sleepQuality = 0.8f,
            efficiency = null,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals(0, historySession.efficiency)
    }

    @Test
    fun `session with null durationMinutes defaults to 0`() = runTest {
        // Given - null duration
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T06:00:00",
            durationMinutes = null,
            sleepQuality = 0.8f,
            efficiency = 0.85f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("0분", historySession.durationString)
    }

    @Test
    fun `invalid date string falls back to current date`() = runTest {
        // Given - invalid date format
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "invalid-date",
            endTime = "invalid-date",
            durationMinutes = 480,
            sleepQuality = 0.8f,
            efficiency = 0.85f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then - should not crash
        val historySessions = viewModel.uiState.value.sessions
        assertEquals(1, historySessions.size)
        assertNotNull(historySessions.first().dateString)
    }

    @Test
    fun `efficiency is converted to percentage correctly`() = runTest {
        // Given - various efficiency values
        val sessions = listOf(
            SleepSession(1, 1, "2024-06-01T22:00:00", "2024-06-02T06:00:00", 480, 0.8f, 1.0f, null),
            SleepSession(2, 1, "2024-05-31T22:00:00", "2024-06-01T06:00:00", 480, 0.8f, 0.5f, null),
            SleepSession(3, 1, "2024-05-30T22:00:00", "2024-05-31T06:00:00", 480, 0.8f, 0.0f, null)
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(sessions)

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySessions = viewModel.uiState.value.sessions
        assertEquals(100, historySessions[0].efficiency)
        assertEquals(50, historySessions[1].efficiency)
        assertEquals(0, historySessions[2].efficiency)
    }

    @Test
    fun `very long duration is formatted correctly`() = runTest {
        // Given - 15 hours 30 minutes
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00",
            endTime = "2024-06-02T13:30:00",
            durationMinutes = 930,
            sleepQuality = 0.6f,
            efficiency = 0.7f,
            createdAt = null
        )
        coEvery { sleepRepository.getHistory(any()) } returns Result.success(listOf(session))

        // When
        viewModel = HistoryViewModel(sleepRepository)
        advanceUntilIdle()

        // Then
        val historySession = viewModel.uiState.value.sessions.first()
        assertEquals("15시간 30분", historySession.durationString)
    }
}

