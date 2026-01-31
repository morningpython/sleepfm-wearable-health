package io.sleepfm.android.domain.model

import org.junit.Assert.*
import org.junit.Test

class DomainModelsTest {

    // ==========================================
    // Auth Models Tests
    // ==========================================

    @Test
    fun `RegisterRequest holds correct values`() {
        val request = RegisterRequest(
            email = "test@example.com",
            password = "secure123",
            username = "testuser"
        )
        
        assertEquals("test@example.com", request.email)
        assertEquals("secure123", request.password)
        assertEquals("testuser", request.username)
    }

    @Test
    fun `RegisterRequest equality works correctly`() {
        val request1 = RegisterRequest("a@b.com", "pass", "user")
        val request2 = RegisterRequest("a@b.com", "pass", "user")
        val request3 = RegisterRequest("c@d.com", "pass", "user")
        
        assertEquals(request1, request2)
        assertNotEquals(request1, request3)
    }

    @Test
    fun `LoginRequest holds correct values`() {
        val request = LoginRequest(
            email = "user@test.com",
            password = "password123"
        )
        
        assertEquals("user@test.com", request.email)
        assertEquals("password123", request.password)
    }

    @Test
    fun `LoginRequest copy creates modified instance`() {
        val original = LoginRequest("a@b.com", "pass1")
        val copied = original.copy(password = "pass2")
        
        assertEquals("a@b.com", copied.email)
        assertEquals("pass2", copied.password)
    }

    @Test
    fun `RefreshRequest holds refresh token`() {
        val request = RefreshRequest(refreshToken = "refresh_token_xyz")
        
        assertEquals("refresh_token_xyz", request.refreshToken)
    }

    @Test
    fun `AuthResponse holds all auth data`() {
        val user = User(1, "test@test.com", "testuser", "2024-01-01", true)
        val response = AuthResponse(
            accessToken = "access_token",
            refreshToken = "refresh_token",
            tokenType = "Bearer",
            user = user
        )
        
        assertEquals("access_token", response.accessToken)
        assertEquals("refresh_token", response.refreshToken)
        assertEquals("Bearer", response.tokenType)
        assertEquals(user, response.user)
    }

    @Test
    fun `AuthResponse with null user`() {
        val response = AuthResponse(
            accessToken = "token",
            refreshToken = "refresh",
            tokenType = "Bearer",
            user = null
        )
        
        assertNull(response.user)
    }

    @Test
    fun `User holds all fields`() {
        val user = User(
            id = 42,
            email = "user@sleepfm.io",
            username = "sleepuser",
            createdAt = "2024-01-15T10:30:00Z",
            isActive = true
        )
        
        assertEquals(42, user.id)
        assertEquals("user@sleepfm.io", user.email)
        assertEquals("sleepuser", user.username)
        assertEquals("2024-01-15T10:30:00Z", user.createdAt)
        assertTrue(user.isActive!!)
    }

    @Test
    fun `User with nullable fields as null`() {
        val user = User(
            id = 1,
            email = "test@test.com",
            username = "test",
            createdAt = null,
            isActive = null
        )
        
        assertNull(user.createdAt)
        assertNull(user.isActive)
    }

    // ==========================================
    // Sleep Session Models Tests
    // ==========================================

    @Test
    fun `SleepSession holds all fields`() {
        val session = SleepSession(
            id = 1,
            userId = 42,
            startTime = "2024-01-15T22:00:00Z",
            endTime = "2024-01-16T06:00:00Z",
            durationMinutes = 480,
            sleepQuality = 0.85f,
            efficiency = 0.92f,
            createdAt = "2024-01-16T06:01:00Z"
        )
        
        assertEquals(1, session.id)
        assertEquals(42, session.userId)
        assertEquals("2024-01-15T22:00:00Z", session.startTime)
        assertEquals("2024-01-16T06:00:00Z", session.endTime)
        assertEquals(480, session.durationMinutes)
        assertEquals(0.85f, session.sleepQuality!!, 0.001f)
        assertEquals(0.92f, session.efficiency!!, 0.001f)
    }

    @Test
    fun `SleepSession with nullable fields`() {
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-01-15T22:00:00Z",
            endTime = null,
            durationMinutes = null,
            sleepQuality = null,
            efficiency = null,
            createdAt = null
        )
        
        assertNull(session.endTime)
        assertNull(session.durationMinutes)
        assertNull(session.sleepQuality)
    }

    @Test
    fun `SyncRequest holds sensor data`() {
        val heartRateData = listOf(
            SensorReading("2024-01-15T22:00:00Z", 72.0f),
            SensorReading("2024-01-15T22:01:00Z", 70.0f)
        )
        val accelerometerData = listOf(
            AccelerometerReading("2024-01-15T22:00:00Z", 0.1f, 0.2f, 9.8f)
        )
        
        val request = SyncRequest(
            startTime = "2024-01-15T22:00:00Z",
            endTime = "2024-01-16T06:00:00Z",
            heartRateData = heartRateData,
            spO2Data = null,
            accelerometerData = accelerometerData
        )
        
        assertEquals(2, request.heartRateData?.size)
        assertNull(request.spO2Data)
        assertEquals(1, request.accelerometerData?.size)
    }

    @Test
    fun `SensorReading holds timestamp and value`() {
        val reading = SensorReading(
            timestamp = "2024-01-15T22:30:00Z",
            value = 98.5f
        )
        
        assertEquals("2024-01-15T22:30:00Z", reading.timestamp)
        assertEquals(98.5f, reading.value, 0.001f)
    }

    @Test
    fun `AccelerometerReading holds xyz values`() {
        val reading = AccelerometerReading(
            timestamp = "2024-01-15T22:30:00Z",
            x = 0.15f,
            y = -0.25f,
            z = 9.81f
        )
        
        assertEquals("2024-01-15T22:30:00Z", reading.timestamp)
        assertEquals(0.15f, reading.x, 0.001f)
        assertEquals(-0.25f, reading.y, 0.001f)
        assertEquals(9.81f, reading.z, 0.001f)
    }

    // ==========================================
    // Analysis Models Tests
    // ==========================================

    @Test
    fun `AnalysisResponse holds stages and summary`() {
        val stages = listOf(
            SleepStage("22:00", "23:00", "light", 60),
            SleepStage("23:00", "01:00", "deep", 120)
        )
        val summary = SleepSummary(
            totalSleepMinutes = 480,
            sleepEfficiency = 0.90f,
            qualityScore = 0.85f,
            wakeMinutes = 30,
            lightMinutes = 180,
            deepMinutes = 150,
            remMinutes = 120
        )
        
        val response = AnalysisResponse(
            sessionId = 1,
            stages = stages,
            summary = summary
        )
        
        assertEquals(1, response.sessionId)
        assertEquals(2, response.stages.size)
        assertEquals(480, response.summary.totalSleepMinutes)
    }

    @Test
    fun `SleepStage types are correct`() {
        val wakeStage = SleepStage("00:00", "00:10", "wake", 10)
        val lightStage = SleepStage("00:10", "01:00", "light", 50)
        val deepStage = SleepStage("01:00", "02:00", "deep", 60)
        val remStage = SleepStage("02:00", "02:30", "rem", 30)
        
        assertEquals("wake", wakeStage.stage)
        assertEquals("light", lightStage.stage)
        assertEquals("deep", deepStage.stage)
        assertEquals("rem", remStage.stage)
    }

    @Test
    fun `SleepSummary holds all metrics`() {
        val summary = SleepSummary(
            totalSleepMinutes = 450,
            sleepEfficiency = 0.90f,
            qualityScore = 0.85f,
            wakeMinutes = 30,
            lightMinutes = 180,
            deepMinutes = 150,
            remMinutes = 120
        )
        
        assertEquals(450, summary.totalSleepMinutes)
        assertEquals(0.90f, summary.sleepEfficiency, 0.001f)
        assertEquals(0.85f, summary.qualityScore, 0.001f)
        assertEquals(30, summary.wakeMinutes)
        assertEquals(180, summary.lightMinutes)
        assertEquals(150, summary.deepMinutes)
        assertEquals(120, summary.remMinutes)
    }

    // ==========================================
    // Disease Risk Models Tests
    // ==========================================

    @Test
    fun `DiseaseRiskResponse holds predictions`() {
        val predictions = listOf(
            DiseaseRisk("sleep_apnea", "moderate", 0.45f, 0.85f, listOf("Consult doctor")),
            DiseaseRisk("insomnia", "low", 0.20f, 0.90f, null)
        )
        
        val response = DiseaseRiskResponse(
            sessionId = 1,
            predictions = predictions
        )
        
        assertEquals(1, response.sessionId)
        assertEquals(2, response.predictions.size)
    }

    @Test
    fun `DiseaseRisk holds all fields`() {
        val risk = DiseaseRisk(
            disease = "sleep_apnea",
            riskLevel = "high",
            riskScore = 0.75f,
            confidence = 0.92f,
            recommendations = listOf("See a specialist", "Sleep study recommended")
        )
        
        assertEquals("sleep_apnea", risk.disease)
        assertEquals("high", risk.riskLevel)
        assertEquals(0.75f, risk.riskScore, 0.001f)
        assertEquals(0.92f, risk.confidence!!, 0.001f)
        assertEquals(2, risk.recommendations?.size)
    }

    @Test
    fun `DiseaseRisk with nullable confidence and recommendations`() {
        val risk = DiseaseRisk(
            disease = "insomnia",
            riskLevel = "low",
            riskScore = 0.15f,
            confidence = null,
            recommendations = null
        )
        
        assertNull(risk.confidence)
        assertNull(risk.recommendations)
    }

    @Test
    fun `DiseaseRisk levels are valid`() {
        val lowRisk = DiseaseRisk("test", "low", 0.1f, null, null)
        val moderateRisk = DiseaseRisk("test", "moderate", 0.5f, null, null)
        val highRisk = DiseaseRisk("test", "high", 0.8f, null, null)
        
        assertEquals("low", lowRisk.riskLevel)
        assertEquals("moderate", moderateRisk.riskLevel)
        assertEquals("high", highRisk.riskLevel)
    }

    @Test
    fun `DiseaseRisk equality works correctly`() {
        val risk1 = DiseaseRisk("apnea", "high", 0.8f, 0.9f, listOf("Test"))
        val risk2 = DiseaseRisk("apnea", "high", 0.8f, 0.9f, listOf("Test"))
        val risk3 = DiseaseRisk("insomnia", "high", 0.8f, 0.9f, listOf("Test"))
        
        assertEquals(risk1, risk2)
        assertNotEquals(risk1, risk3)
    }

    @Test
    fun `SleepStage copy works correctly`() {
        val original = SleepStage("22:00", "23:00", "light", 60)
        val copied = original.copy(stage = "deep")
        
        assertEquals("deep", copied.stage)
        assertEquals(original.startTime, copied.startTime)
        assertEquals(original.endTime, copied.endTime)
        assertEquals(original.durationMinutes, copied.durationMinutes)
    }

    @Test
    fun `SleepSummary equality works correctly`() {
        val summary1 = SleepSummary(450, 0.9f, 0.85f, 30, 180, 150, 120)
        val summary2 = SleepSummary(450, 0.9f, 0.85f, 30, 180, 150, 120)
        val summary3 = SleepSummary(400, 0.9f, 0.85f, 30, 180, 150, 120)
        
        assertEquals(summary1, summary2)
        assertNotEquals(summary1, summary3)
    }
}
