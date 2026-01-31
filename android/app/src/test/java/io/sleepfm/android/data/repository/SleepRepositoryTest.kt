package io.sleepfm.android.data.repository

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import io.sleepfm.android.data.api.SleepFMApi
import io.sleepfm.android.data.local.SleepDatabase
import io.sleepfm.android.data.local.dao.SleepSessionDao
import io.sleepfm.android.domain.model.SleepSession
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import retrofit2.Response

class SleepRepositoryTest {

    private lateinit var api: SleepFMApi
    private lateinit var database: SleepDatabase
    private lateinit var dao: SleepSessionDao
    private lateinit var repository: SleepRepository

    @Before
    fun setup() {
        api = mockk()
        database = mockk()
        dao = mockk(relaxed = true)
        coEvery { database.sleepSessionDao() } returns dao
        repository = SleepRepository(api, database)
    }

    @Test
    fun `getSession returns session on success`() = runTest {
        // Given
        val sessionId = 1
        val session = SleepSession(
            id = sessionId,
            userId = 1,
            startTime = "2026-01-30T23:00:00",
            endTime = "2026-01-31T07:00:00",
            durationMinutes = 480,
            sleepQuality = 0.85f,
            efficiency = 0.92f,
            createdAt = "2026-01-30T23:00:00"
        )
        coEvery { api.getSession(sessionId) } returns Response.success(session)

        // When
        val result = repository.getSession(sessionId)

        // Then
        assertTrue(result.isSuccess)
        assertEquals(session, result.getOrNull())
    }

    @Test
    fun `getSession returns failure on error`() = runTest {
        // Given
        coEvery { api.getSession(any()) } returns Response.error(404, mockk(relaxed = true))

        // When
        val result = repository.getSession(999)

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `getHistory returns sessions and caches locally`() = runTest {
        // Given
        val sessions = listOf(
            SleepSession(id = 1, userId = 1, startTime = "2026-01-30T23:00:00", endTime = "2026-01-31T07:00:00", durationMinutes = 480, sleepQuality = 0.8f, efficiency = 0.9f, createdAt = "2026-01-30T23:00:00"),
            SleepSession(id = 2, userId = 1, startTime = "2026-01-29T23:00:00", endTime = "2026-01-30T06:30:00", durationMinutes = 450, sleepQuality = 0.75f, efficiency = 0.88f, createdAt = "2026-01-29T23:00:00")
        )
        coEvery { api.getHistory(any()) } returns Response.success(sessions)

        // When
        val result = repository.getHistory(30)

        // Then
        assertTrue(result.isSuccess)
        assertEquals(2, result.getOrNull()?.size)
        coVerify(exactly = 2) { dao.insertSession(any()) }
    }

    @Test
    fun `getLatestSession returns session on success`() = runTest {
        // Given
        val session = SleepSession(
            id = 1, userId = 1, startTime = "2026-01-30T23:00:00",
            endTime = "2026-01-31T07:00:00", durationMinutes = 480,
            sleepQuality = 0.85f, efficiency = 0.92f,
            createdAt = "2026-01-30T23:00:00"
        )
        coEvery { api.getLatestSession() } returns Response.success(session)

        // When
        val result = repository.getLatestSession()

        // Then
        assertTrue(result.isSuccess)
        assertEquals(480, result.getOrNull()?.durationMinutes)
    }

    @Test
    fun `analyzeSession returns analysis on success`() = runTest {
        // Given
        val analysis = mockk<io.sleepfm.android.domain.model.AnalysisResponse>(relaxed = true)
        coEvery { api.getAnalysis(any()) } returns Response.success(analysis)

        // When
        val result = repository.analyzeSession(1)

        // Then
        assertTrue(result.isSuccess)
    }

    @Test
    fun `analyzeSession returns failure on error`() = runTest {
        // Given
        coEvery { api.getAnalysis(any()) } returns Response.error(500, mockk(relaxed = true))

        // When
        val result = repository.analyzeSession(1)

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `getHistory returns failure on error`() = runTest {
        // Given
        coEvery { api.getHistory(any()) } returns Response.error(500, mockk(relaxed = true))

        // When
        val result = repository.getHistory(30)

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `getLatestSession returns failure on error`() = runTest {
        // Given
        coEvery { api.getLatestSession() } returns Response.error(404, mockk(relaxed = true))

        // When
        val result = repository.getLatestSession()

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `predictDiseaseRisk returns result on success`() = runTest {
        // Given
        val riskResponse = mockk<io.sleepfm.android.domain.model.DiseaseRiskResponse>(relaxed = true)
        coEvery { api.getDiseaseRisk(any()) } returns Response.success(riskResponse)

        // When
        val result = repository.predictDiseaseRisk(1)

        // Then
        assertTrue(result.isSuccess)
    }

    @Test
    fun `predictDiseaseRisk returns failure on error`() = runTest {
        // Given
        coEvery { api.getDiseaseRisk(any()) } returns Response.error(500, mockk(relaxed = true))

        // When
        val result = repository.predictDiseaseRisk(1)

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `getSession handles exception`() = runTest {
        // Given
        coEvery { api.getSession(any()) } throws RuntimeException("Network error")

        // When
        val result = repository.getSession(1)

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `getHistory handles exception`() = runTest {
        // Given
        coEvery { api.getHistory(any()) } throws RuntimeException("Network error")

        // When
        val result = repository.getHistory()

        // Then
        assertTrue(result.isFailure)
    }
}
