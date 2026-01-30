package io.sleepfm.android.data.repository

import io.sleepfm.android.data.api.SleepFMApi
import io.sleepfm.android.data.local.TokenManager
import io.sleepfm.android.domain.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val api: SleepFMApi,
    private val tokenManager: TokenManager
) {
    val isLoggedIn: Flow<Boolean> = tokenManager.isLoggedIn
    val currentUser: Flow<User?> = tokenManager.user
    
    suspend fun register(email: String, password: String, username: String): Result<AuthResponse> {
        return try {
            val response = api.register(RegisterRequest(email, password, username))
            saveAuthResponse(response)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun login(email: String, password: String): Result<AuthResponse> {
        return try {
            val response = api.login(LoginRequest(email, password))
            saveAuthResponse(response)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun refreshToken(): Result<AuthResponse> {
        return try {
            val refreshToken = tokenManager.refreshToken.first()
            if (refreshToken == null) {
                return Result.failure(IllegalStateException("No refresh token available"))
            }
            val response = api.refreshToken(RefreshRequest(refreshToken))
            saveAuthResponse(response)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun logout() {
        tokenManager.clearTokens()
    }
    
    suspend fun getMe(): Result<User> {
        return try {
            val user = api.getMe()
            tokenManager.saveUser(user)
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private suspend fun saveAuthResponse(response: AuthResponse) {
        tokenManager.saveTokens(response.accessToken, response.refreshToken)
        response.user?.let { tokenManager.saveUser(it) }
    }
    
    // Onboarding status
    val hasCompletedOnboarding: Flow<Boolean> = tokenManager.hasCompletedOnboarding
    
    suspend fun setOnboardingCompleted() {
        tokenManager.setOnboardingCompleted()
    }
}
