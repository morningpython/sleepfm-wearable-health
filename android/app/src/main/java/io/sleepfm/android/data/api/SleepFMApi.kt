package io.sleepfm.android.data.api

import io.sleepfm.android.domain.model.AnalysisResponse
import io.sleepfm.android.domain.model.AuthResponse
import io.sleepfm.android.domain.model.DiseaseRiskResponse
import io.sleepfm.android.domain.model.LoginRequest
import io.sleepfm.android.domain.model.RefreshRequest
import io.sleepfm.android.domain.model.RegisterRequest
import io.sleepfm.android.domain.model.SleepSession
import io.sleepfm.android.domain.model.SyncRequest
import io.sleepfm.android.domain.model.User
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * SleepFM Backend API Interface
 */
interface SleepFMApi {

    // ==========================================
    // Auth Endpoints
    // ==========================================
    
    @POST("api/v1/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<AuthResponse>

    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>

    @POST("api/v1/auth/refresh")
    suspend fun refreshToken(@Body request: RefreshRequest): Response<AuthResponse>

    @POST("api/v1/auth/logout")
    suspend fun logout(): Response<Unit>

    @GET("api/v1/auth/me")
    suspend fun getCurrentUser(): Response<User>

    // ==========================================
    // Sessions Endpoints
    // ==========================================

    @GET("api/v1/sessions")
    suspend fun getSessions(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 20
    ): Response<List<SleepSession>>

    @GET("api/v1/sessions/{id}")
    suspend fun getSession(@Path("id") id: Int): Response<SleepSession>

    @GET("api/v1/sessions/latest")
    suspend fun getLatestSession(): Response<SleepSession>

    @POST("api/v1/sessions/sync")
    suspend fun syncSession(@Body request: SyncRequest): Response<SleepSession>

    @DELETE("api/v1/sessions/{id}")
    suspend fun deleteSession(@Path("id") id: Int): Response<Unit>

    // ==========================================
    // Analysis Endpoints
    // ==========================================

    @GET("api/v1/analysis/{sessionId}")
    suspend fun getAnalysis(@Path("sessionId") sessionId: Int): Response<AnalysisResponse>

    @GET("api/v1/analysis/disease-risk/{sessionId}")
    suspend fun getDiseaseRisk(@Path("sessionId") sessionId: Int): Response<DiseaseRiskResponse>

    // ==========================================
    // History Endpoints
    // ==========================================

    @GET("api/v1/history")
    suspend fun getHistory(
        @Query("days") days: Int = 30
    ): Response<List<SleepSession>>

    @GET("api/v1/history/stats")
    suspend fun getStats(
        @Query("days") days: Int = 30
    ): Response<Map<String, Any>>

    // ==========================================
    // Health Check
    // ==========================================

    @GET("api/v1/health")
    suspend fun healthCheck(): Response<Map<String, String>>
}
