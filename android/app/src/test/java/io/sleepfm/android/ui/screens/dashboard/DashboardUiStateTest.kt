package io.sleepfm.android.ui.screens.dashboard

import org.junit.Assert.*
import org.junit.Test

class DashboardUiStateTest {

    @Test
    fun `default DashboardUiState has correct initial values`() {
        val state = DashboardUiState()
        
        assertFalse(state.isLoading)
        assertEquals(0, state.sleepScore)
        assertEquals("수면 데이터를 불러오는 중...", state.scoreMessage)
        assertFalse(state.hasLastNightData)
        assertEquals("0시간 0분", state.totalSleepHours)
        assertEquals(0, state.sleepEfficiency)
        assertEquals("--:--", state.bedTime)
        assertEquals("--:--", state.wakeTime)
        assertEquals(0, state.wakeMinutes)
        assertEquals(0, state.lightMinutes)
        assertEquals(0, state.deepMinutes)
        assertEquals(0, state.remMinutes)
        assertTrue(state.diseaseRisks.isEmpty())
        assertFalse(state.isHealthConnectAvailable)
        assertNull(state.error)
    }

    @Test
    fun `DashboardUiState with sleep data`() {
        val state = DashboardUiState(
            hasLastNightData = true,
            sleepScore = 85,
            scoreMessage = "좋은 수면입니다",
            totalSleepHours = "7시간 30분",
            sleepEfficiency = 92,
            bedTime = "22:30",
            wakeTime = "06:00"
        )
        
        assertTrue(state.hasLastNightData)
        assertEquals(85, state.sleepScore)
        assertEquals("좋은 수면입니다", state.scoreMessage)
        assertEquals("7시간 30분", state.totalSleepHours)
        assertEquals(92, state.sleepEfficiency)
        assertEquals("22:30", state.bedTime)
        assertEquals("06:00", state.wakeTime)
    }

    @Test
    fun `DashboardUiState with sleep stage data`() {
        val state = DashboardUiState(
            wakeMinutes = 30,
            lightMinutes = 180,
            deepMinutes = 120,
            remMinutes = 90
        )
        
        assertEquals(30, state.wakeMinutes)
        assertEquals(180, state.lightMinutes)
        assertEquals(120, state.deepMinutes)
        assertEquals(90, state.remMinutes)
        
        // Total should be 420 minutes = 7 hours
        val totalMinutes = state.wakeMinutes + state.lightMinutes + state.deepMinutes + state.remMinutes
        assertEquals(420, totalMinutes)
    }

    @Test
    fun `DashboardUiState with disease risks`() {
        val risks = listOf(
            DashboardRisk("수면무호흡증", "낮음", 0.15f),
            DashboardRisk("불면증", "중간", 0.45f)
        )
        val state = DashboardUiState(diseaseRisks = risks)
        
        assertEquals(2, state.diseaseRisks.size)
        assertEquals("수면무호흡증", state.diseaseRisks[0].disease)
        assertEquals("낮음", state.diseaseRisks[0].level)
        assertEquals(0.15f, state.diseaseRisks[0].score, 0.001f)
    }

    @Test
    fun `DashboardUiState copy preserves unchanged values`() {
        val original = DashboardUiState(
            sleepScore = 80,
            bedTime = "23:00",
            wakeTime = "07:00"
        )
        val copied = original.copy(sleepScore = 90)
        
        assertEquals(90, copied.sleepScore)
        assertEquals("23:00", copied.bedTime)
        assertEquals("07:00", copied.wakeTime)
    }

    @Test
    fun `DashboardUiState equality works correctly`() {
        val state1 = DashboardUiState(sleepScore = 85)
        val state2 = DashboardUiState(sleepScore = 85)
        val state3 = DashboardUiState(sleepScore = 90)
        
        assertEquals(state1, state2)
        assertNotEquals(state1, state3)
    }

    @Test
    fun `DashboardRisk holds correct values`() {
        val risk = DashboardRisk(
            disease = "sleep_apnea",
            level = "high",
            score = 0.85f
        )
        
        assertEquals("sleep_apnea", risk.disease)
        assertEquals("high", risk.level)
        assertEquals(0.85f, risk.score, 0.001f)
    }

    @Test
    fun `DashboardRisk equality works correctly`() {
        val risk1 = DashboardRisk("test", "low", 0.1f)
        val risk2 = DashboardRisk("test", "low", 0.1f)
        val risk3 = DashboardRisk("test", "high", 0.9f)
        
        assertEquals(risk1, risk2)
        assertNotEquals(risk1, risk3)
    }
}
