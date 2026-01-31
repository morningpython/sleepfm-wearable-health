package io.sleepfm.android.ui.screens.history

import org.junit.Assert.*
import org.junit.Test

class HistoryUiStateTest {

    @Test
    fun `default HistoryUiState has correct initial values`() {
        val state = HistoryUiState()
        
        assertFalse(state.isLoading)
        assertTrue(state.sessions.isEmpty())
        assertNull(state.error)
    }

    @Test
    fun `HistoryUiState with loading state`() {
        val state = HistoryUiState(isLoading = true)
        
        assertTrue(state.isLoading)
        assertTrue(state.sessions.isEmpty())
        assertNull(state.error)
    }

    @Test
    fun `HistoryUiState with sessions`() {
        val sessions = listOf(
            HistorySession(
                id = 1,
                dateString = "1월 30일 (금)",
                bedTime = "22:00",
                wakeTime = "06:00",
                durationString = "8시간",
                efficiency = 90,
                quality = "excellent"
            ),
            HistorySession(
                id = 2,
                dateString = "1월 29일 (목)",
                bedTime = "23:00",
                wakeTime = "07:00",
                durationString = "8시간",
                efficiency = 85,
                quality = "good"
            )
        )
        val state = HistoryUiState(sessions = sessions)
        
        assertEquals(2, state.sessions.size)
        assertEquals(1, state.sessions[0].id)
        assertEquals(2, state.sessions[1].id)
    }

    @Test
    fun `HistoryUiState with error`() {
        val state = HistoryUiState(error = "Network error")
        
        assertFalse(state.isLoading)
        assertEquals("Network error", state.error)
    }

    @Test
    fun `HistoryUiState copy preserves unchanged values`() {
        val sessions = listOf(
            HistorySession(1, "date", "22:00", "06:00", "8h", 90, "excellent")
        )
        val original = HistoryUiState(sessions = sessions, error = null)
        val copied = original.copy(isLoading = true)
        
        assertTrue(copied.isLoading)
        assertEquals(1, copied.sessions.size)
        assertNull(copied.error)
    }

    @Test
    fun `HistoryUiState equality works correctly`() {
        val state1 = HistoryUiState(isLoading = true)
        val state2 = HistoryUiState(isLoading = true)
        val state3 = HistoryUiState(isLoading = false)
        
        assertEquals(state1, state2)
        assertNotEquals(state1, state3)
    }

    @Test
    fun `HistoryUiState hashCode is consistent`() {
        val state1 = HistoryUiState(isLoading = true)
        val state2 = HistoryUiState(isLoading = true)
        
        assertEquals(state1.hashCode(), state2.hashCode())
    }
}

class HistorySessionTest {

    @Test
    fun `HistorySession holds correct values`() {
        val session = HistorySession(
            id = 1,
            dateString = "1월 30일 (금)",
            bedTime = "22:30",
            wakeTime = "06:30",
            durationString = "8시간",
            efficiency = 92,
            quality = "excellent"
        )
        
        assertEquals(1, session.id)
        assertEquals("1월 30일 (금)", session.dateString)
        assertEquals("22:30", session.bedTime)
        assertEquals("06:30", session.wakeTime)
        assertEquals("8시간", session.durationString)
        assertEquals(92, session.efficiency)
        assertEquals("excellent", session.quality)
    }

    @Test
    fun `HistorySession quality levels`() {
        val excellentSession = HistorySession(1, "", "", "", "", 95, "excellent")
        val goodSession = HistorySession(2, "", "", "", "", 80, "good")
        val fairSession = HistorySession(3, "", "", "", "", 65, "fair")
        val poorSession = HistorySession(4, "", "", "", "", 45, "poor")
        
        assertEquals("excellent", excellentSession.quality)
        assertEquals("good", goodSession.quality)
        assertEquals("fair", fairSession.quality)
        assertEquals("poor", poorSession.quality)
    }

    @Test
    fun `HistorySession equality works correctly`() {
        val session1 = HistorySession(1, "date", "22:00", "06:00", "8h", 90, "excellent")
        val session2 = HistorySession(1, "date", "22:00", "06:00", "8h", 90, "excellent")
        val session3 = HistorySession(2, "date", "22:00", "06:00", "8h", 90, "excellent")
        
        assertEquals(session1, session2)
        assertNotEquals(session1, session3)
    }

    @Test
    fun `HistorySession copy creates modified instance`() {
        val original = HistorySession(1, "date", "22:00", "06:00", "8h", 90, "excellent")
        val copied = original.copy(efficiency = 95)
        
        assertEquals(95, copied.efficiency)
        assertEquals(original.id, copied.id)
        assertEquals(original.quality, copied.quality)
    }

    @Test
    fun `HistorySession with placeholder wake time`() {
        val session = HistorySession(
            id = 1,
            dateString = "date",
            bedTime = "22:00",
            wakeTime = "--:--",
            durationString = "진행 중",
            efficiency = 0,
            quality = "poor"
        )
        
        assertEquals("--:--", session.wakeTime)
    }

    @Test
    fun `HistorySession efficiency is in valid range`() {
        val lowEfficiency = HistorySession(1, "", "", "", "", 0, "poor")
        val midEfficiency = HistorySession(2, "", "", "", "", 50, "fair")
        val highEfficiency = HistorySession(3, "", "", "", "", 100, "excellent")
        
        assertTrue(lowEfficiency.efficiency in 0..100)
        assertTrue(midEfficiency.efficiency in 0..100)
        assertTrue(highEfficiency.efficiency in 0..100)
    }

    @Test
    fun `HistorySession hashCode is consistent`() {
        val session1 = HistorySession(1, "date", "22:00", "06:00", "8h", 90, "excellent")
        val session2 = HistorySession(1, "date", "22:00", "06:00", "8h", 90, "excellent")
        
        assertEquals(session1.hashCode(), session2.hashCode())
    }
}
