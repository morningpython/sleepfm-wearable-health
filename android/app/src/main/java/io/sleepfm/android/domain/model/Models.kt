package io.sleepfm.android.domain.model

import com.google.gson.annotations.SerializedName

// ==========================================
// Auth Models
// ==========================================

data class RegisterRequest(
    val email: String,
    val password: String,
    val username: String
)

data class LoginRequest(
    val email: String,
    val password: String
)

data class RefreshRequest(
    @SerializedName("refresh_token")
    val refreshToken: String
)

data class AuthResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("refresh_token")
    val refreshToken: String,
    @SerializedName("token_type")
    val tokenType: String,
    val user: User?
)

data class User(
    val id: Int,
    val email: String,
    val username: String,
    @SerializedName("created_at")
    val createdAt: String?,
    @SerializedName("is_active")
    val isActive: Boolean?
)

// ==========================================
// Sleep Session Models
// ==========================================

data class SleepSession(
    val id: Int,
    @SerializedName("user_id")
    val userId: Int,
    @SerializedName("start_time")
    val startTime: String,
    @SerializedName("end_time")
    val endTime: String?,
    @SerializedName("duration_minutes")
    val durationMinutes: Int?,
    @SerializedName("sleep_quality")
    val sleepQuality: Float?,
    val efficiency: Float?,
    @SerializedName("created_at")
    val createdAt: String?
)

data class SyncRequest(
    @SerializedName("start_time")
    val startTime: String,
    @SerializedName("end_time")
    val endTime: String,
    @SerializedName("heart_rate_data")
    val heartRateData: List<SensorReading>?,
    @SerializedName("spo2_data")
    val spO2Data: List<SensorReading>?,
    @SerializedName("accelerometer_data")
    val accelerometerData: List<AccelerometerReading>?
)

data class SensorReading(
    val timestamp: String,
    val value: Float
)

data class AccelerometerReading(
    val timestamp: String,
    val x: Float,
    val y: Float,
    val z: Float
)

// ==========================================
// Analysis Models
// ==========================================

data class AnalysisResponse(
    @SerializedName("session_id")
    val sessionId: Int,
    val stages: List<SleepStage>,
    val summary: SleepSummary
)

data class SleepStage(
    @SerializedName("start_time")
    val startTime: String,
    @SerializedName("end_time")
    val endTime: String,
    val stage: String, // "wake", "light", "deep", "rem"
    @SerializedName("duration_minutes")
    val durationMinutes: Int
)

data class SleepSummary(
    @SerializedName("total_sleep_minutes")
    val totalSleepMinutes: Int,
    @SerializedName("sleep_efficiency")
    val sleepEfficiency: Float,
    @SerializedName("quality_score")
    val qualityScore: Float,
    @SerializedName("wake_minutes")
    val wakeMinutes: Int,
    @SerializedName("light_minutes")
    val lightMinutes: Int,
    @SerializedName("deep_minutes")
    val deepMinutes: Int,
    @SerializedName("rem_minutes")
    val remMinutes: Int
)

// ==========================================
// Disease Risk Models
// ==========================================

data class DiseaseRiskResponse(
    @SerializedName("session_id")
    val sessionId: Int,
    val predictions: List<DiseaseRisk>
)

data class DiseaseRisk(
    val disease: String,
    @SerializedName("risk_level")
    val riskLevel: String, // "low", "moderate", "high"
    @SerializedName("risk_score")
    val riskScore: Float,
    val confidence: Float?,
    val recommendations: List<String>?
)
