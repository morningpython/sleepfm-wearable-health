package io.sleepfm.android.domain.model

import org.junit.Assert.*
import org.junit.Test

class ModelsTest {

    // ==========================================
    // Auth Models Tests
    // ==========================================

    @Test
    fun `RegisterRequest should hold correct values`() {
        val request = RegisterRequest(
            email = "test@example.com",
            password = "password123",
            username = "testuser"
        )
        
        assertEquals("test@example.com", request.email)
        assertEquals("password123", request.password)
        assertEquals("testuser", request.username)
    }

    @Test
    fun `RegisterRequest copy should create new instance with modified values`() {
        val original = RegisterRequest("test@example.com", "password", "user")
        val copied = original.copy(username = "newuser")
        
        assertEquals("newuser", copied.username)
        assertEquals("test@example.com", copied.email)
        assertNotEquals(original, copied)
    }

    @Test
    fun `LoginRequest should hold correct values`() {
        val request = LoginRequest(
            email = "user@test.com",
            password = "secret"
        )
        
        assertEquals("user@test.com", request.email)
        assertEquals("secret", request.password)
    }

    @Test
    fun `RefreshRequest should hold refresh token`() {
        val request = RefreshRequest(refreshToken = "refresh_token_123")
        assertEquals("refresh_token_123", request.refreshToken)
    }

    @Test
    fun `AuthResponse should hold all auth data`() {
        val user = User(1, "test@example.com", "testuser", "2024-01-01", true)
        val response = AuthResponse(
            accessToken = "access_token",
            refreshToken = "refresh_token",
            tokenType = "Bearer",
            user = user
        )
        
        assertEquals("access_token", response.accessToken)
        assertEquals("refresh_token", response.refreshToken)
        assertEquals("Bearer", response.tokenType)
        assertNotNull(response.user)
        assertEquals(1, response.user?.id)
    }

    @Test
    fun `AuthResponse with null user should be valid`() {
        val response = AuthResponse(
            accessToken = "token",
            refreshToken = "refresh",
            tokenType = "Bearer",
            user = null
        )
        
        assertNull(response.user)
        assertEquals("token", response.accessToken)
    }

    @Test
    fun `User should hold all user data`() {
        val user = User(
            id = 42,
            email = "user@example.com",
            username = "myuser",
            createdAt = "2024-06-01T12:00:00Z",
            isActive = true
        )
        
        assertEquals(42, user.id)
        assertEquals("user@example.com", user.email)
        assertEquals("myuser", user.username)
        assertEquals("2024-06-01T12:00:00Z", user.createdAt)
        assertTrue(user.isActive!!)
    }

    @Test
    fun `User with nullable fields should be valid`() {
        val user = User(
            id = 1,
            email = "test@test.com",
            username = "user",
            createdAt = null,
            isActive = null
        )
        
        assertNull(user.createdAt)
        assertNull(user.isActive)
    }

    @Test
    fun `User equality should work correctly`() {
        val user1 = User(1, "test@test.com", "user", null, true)
        val user2 = User(1, "test@test.com", "user", null, true)
        val user3 = User(2, "test@test.com", "user", null, true)
        
        assertEquals(user1, user2)
        assertNotEquals(user1, user3)
    }

    // ==========================================
    // Sleep Session Models Tests
    // ==========================================

    @Test
    fun `SleepSession should hold all session data`() {
        val session = SleepSession(
            id = 1,
            userId = 42,
            startTime = "2024-06-01T22:00:00Z",
            endTime = "2024-06-02T06:00:00Z",
            durationMinutes = 480,
            sleepQuality = 0.85f,
            efficiency = 0.92f,
            createdAt = "2024-06-02T06:00:00Z"
        )
        
        assertEquals(1, session.id)
        assertEquals(42, session.userId)
        assertEquals("2024-06-01T22:00:00Z", session.startTime)
        assertEquals("2024-06-02T06:00:00Z", session.endTime)
        assertEquals(480, session.durationMinutes)
        assertEquals(0.85f, session.sleepQuality!!, 0.001f)
        assertEquals(0.92f, session.efficiency!!, 0.001f)
    }

    @Test
    fun `SleepSession with nullable fields should be valid`() {
        val session = SleepSession(
            id = 1,
            userId = 1,
            startTime = "2024-06-01T22:00:00Z",
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
    fun `SyncRequest should hold sensor data`() {
        val heartRateData = listOf(
            SensorReading("2024-06-01T22:00:00Z", 65f),
            SensorReading("2024-06-01T22:01:00Z", 62f)
        )
        val spO2Data = listOf(
            SensorReading("2024-06-01T22:00:00Z", 98f)
        )
        val accelerometerData = listOf(
            AccelerometerReading("2024-06-01T22:00:00Z", 0.1f, 0.2f, 9.8f)
        )
        
        val request = SyncRequest(
            startTime = "2024-06-01T22:00:00Z",
            endTime = "2024-06-02T06:00:00Z",
            heartRateData = heartRateData,
            spO2Data = spO2Data,
            accelerometerData = accelerometerData
        )
        
        assertEquals("2024-06-01T22:00:00Z", request.startTime)
        assertEquals("2024-06-02T06:00:00Z", request.endTime)
        assertEquals(2, request.heartRateData?.size)
        assertEquals(1, request.spO2Data?.size)
        assertEquals(1, request.accelerometerData?.size)
    }

    @Test
    fun `SyncRequest with null sensor data should be valid`() {
        val request = SyncRequest(
            startTime = "2024-06-01T22:00:00Z",
            endTime = "2024-06-02T06:00:00Z",
            heartRateData = null,
            spO2Data = null,
            accelerometerData = null
        )
        
        assertNull(request.heartRateData)
        assertNull(request.spO2Data)
        assertNull(request.accelerometerData)
    }

    @Test
    fun `SensorReading should hold timestamp and value`() {
        val reading = SensorReading(
            timestamp = "2024-06-01T22:00:00Z",
            value = 72.5f
        )
        
        assertEquals("2024-06-01T22:00:00Z", reading.timestamp)
        assertEquals(72.5f, reading.value, 0.01f)
    }

    @Test
    fun `AccelerometerReading should hold xyz values`() {
        val reading = AccelerometerReading(
            timestamp = "2024-06-01T22:00:00Z",
            x = 0.1f,
            y = 0.2f,
            z = 9.8f
        )
        
        assertEquals(0.1f, reading.x, 0.001f)
        assertEquals(0.2f, reading.y, 0.001f)
        assertEquals(9.8f, reading.z, 0.001f)
    }

    // ==========================================
    // Analysis Models Tests
    // ==========================================

    @Test
    fun `AnalysisResponse should hold stages and summary`() {
        val stages = listOf(
            SleepStage("22:00", "23:00", "light", 60),
            SleepStage("23:00", "01:00", "deep", 120)
        )
        val summary = SleepSummary(
            totalSleepMinutes = 480,
            sleepEfficiency = 0.92f,
            qualityScore = 85f,
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
    fun `SleepStage should hold stage information`() {
        val stage = SleepStage(
            startTime = "2024-06-01T22:00:00Z",
            endTime = "2024-06-01T23:30:00Z",
            stage = "deep",
            durationMinutes = 90
        )
        
        assertEquals("deep", stage.stage)
        assertEquals(90, stage.durationMinutes)
    }

    @Test
    fun `SleepStage stages should be valid types`() {
        val validStages = listOf("wake", "light", "deep", "rem")
        
        validStages.forEach { stageName ->
            val stage = SleepStage("start", "end", stageName, 60)
            assertTrue(stage.stage in validStages)
        }
    }

    @Test
    fun `SleepSummary should calculate correctly`() {
        val summary = SleepSummary(
            totalSleepMinutes = 450,
            sleepEfficiency = 0.90f,
            qualityScore = 82.5f,
            wakeMinutes = 30,
            lightMinutes = 180,
            deepMinutes = 120,
            remMinutes = 120
        )
        
        assertEquals(450, summary.totalSleepMinutes)
        assertEquals(0.90f, summary.sleepEfficiency, 0.001f)
        assertEquals(82.5f, summary.qualityScore, 0.1f)
        
        // Verify minutes add up (wake is separate)
        val sleepMinutes = summary.lightMinutes + summary.deepMinutes + summary.remMinutes
        assertEquals(420, sleepMinutes) // Should be close to totalSleepMinutes
    }

    // ==========================================
    // Disease Risk Models Tests
    // ==========================================

    @Test
    fun `DiseaseRiskResponse should hold predictions`() {
        val predictions = listOf(
            DiseaseRisk("sleep_apnea", "low", 0.15f, 0.92f, listOf("Maintain healthy weight")),
            DiseaseRisk("insomnia", "moderate", 0.45f, 0.85f, listOf("Reduce caffeine"))
        )
        
        val response = DiseaseRiskResponse(
            sessionId = 1,
            predictions = predictions
        )
        
        assertEquals(1, response.sessionId)
        assertEquals(2, response.predictions.size)
    }

    @Test
    fun `DiseaseRisk should hold risk data`() {
        val risk = DiseaseRisk(
            disease = "sleep_apnea",
            riskLevel = "high",
            riskScore = 0.75f,
            confidence = 0.88f,
            recommendations = listOf("Consult doctor", "Monitor symptoms")
        )
        
        assertEquals("sleep_apnea", risk.disease)
        assertEquals("high", risk.riskLevel)
        assertEquals(0.75f, risk.riskScore, 0.001f)
        assertEquals(0.88f, risk.confidence!!, 0.001f)
        assertEquals(2, risk.recommendations?.size)
    }

    @Test
    fun `DiseaseRisk risk levels should be valid`() {
        val validLevels = listOf("low", "moderate", "high")
        
        validLevels.forEach { level ->
            val risk = DiseaseRisk("test", level, 0.5f, null, null)
            assertTrue(risk.riskLevel in validLevels)
        }
    }

    @Test
    fun `DiseaseRisk with nullable fields should be valid`() {
        val risk = DiseaseRisk(
            disease = "insomnia",
            riskLevel = "low",
            riskScore = 0.1f,
            confidence = null,
            recommendations = null
        )
        
        assertNull(risk.confidence)
        assertNull(risk.recommendations)
    }

    @Test
    fun `DiseaseRisk with empty recommendations should be valid`() {
        val risk = DiseaseRisk(
            disease = "sleep_apnea",
            riskLevel = "low",
            riskScore = 0.05f,
            confidence = 0.95f,
            recommendations = emptyList()
        )
        
        assertTrue(risk.recommendations!!.isEmpty())
    }

    // ==========================================
    // Data Class Feature Tests
    // ==========================================

    @Test
    fun `data classes should implement hashCode correctly`() {
        val user1 = User(1, "test@test.com", "user", null, true)
        val user2 = User(1, "test@test.com", "user", null, true)
        
        assertEquals(user1.hashCode(), user2.hashCode())
    }

    @Test
    fun `data classes should implement toString`() {
        val user = User(1, "test@test.com", "user", null, true)
        val toString = user.toString()
        
        assertTrue(toString.contains("User"))
        assertTrue(toString.contains("test@test.com"))
        assertTrue(toString.contains("user"))
    }

    @Test
    fun `data classes should support destructuring`() {
        val user = User(1, "test@test.com", "user", "2024-01-01", true)
        val (id, email, username, createdAt, isActive) = user
        
        assertEquals(1, id)
        assertEquals("test@test.com", email)
        assertEquals("user", username)
        assertEquals("2024-01-01", createdAt)
        assertTrue(isActive!!)
    }

    @Test
    fun `SleepSession should support destructuring`() {
        val session = SleepSession(1, 1, "start", "end", 480, 0.85f, 0.9f, "created")
        val (id, userId, startTime, endTime, duration, quality, efficiency, createdAt) = session
        
        assertEquals(1, id)
        assertEquals(1, userId)
        assertEquals("start", startTime)
        assertEquals("end", endTime)
        assertEquals(480, duration)
    }
}
