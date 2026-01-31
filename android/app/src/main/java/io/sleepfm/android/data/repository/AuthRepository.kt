package io.sleepfm.android.data.repository

import io.sleepfm.android.data.api.SleepFMApi
import io.sleepfm.android.data.local.TokenManager
import io.sleepfm.android.domain.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val api: SleepFMApi,
    private val tokenManager: TokenManager
) {
    val isLoggedIn: Flow<Boolean> = tokenManager.getAccessToken().map { it != null }
    val refreshToken: Flow<String?> = tokenManager.getRefreshToken()
    
    suspend fun register(email: String, password: String, username: String): Result<AuthResponse> {
        return try {
            val response = api.register(RegisterRequest(email, password, username))
            if (response.isSuccessful && response.body() != null) {
                saveAuthResponse(response.body()!!)
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Registration failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun login(email: String, password: String): Result<AuthResponse> {
        return try {
            val response = api.login(LoginRequest(email, password))
            if (response.isSuccessful && response.body() != null) {
                saveAuthResponse(response.body()!!)
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Login failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun refreshToken(): Result<AuthResponse> {
        return try {
            val refreshTokenValue = tokenManager.getRefreshToken().first()
            if (refreshTokenValue == null) {
                return Result.failure(IllegalStateException("No refresh token available"))
            }
            val response = api.refreshToken(RefreshRequest(refreshTokenValue))
            if (response.isSuccessful && response.body() != null) {
                saveAuthResponse(response.body()!!)
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Token refresh failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun logout() {
        tokenManager.clearTokens()
    }
    
    suspend fun getMe(): Result<User> {
        return try {
            val response = api.getCurrentUser()
            if (response.isSuccessful && response.body() != null) {
                val user = response.body()!!
                tokenManager.saveUserInfo(user.id.toString(), user.email)
                Result.success(user)
            } else {
                Result.failure(Exception("Failed to get user: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private suspend fun saveAuthResponse(response: AuthResponse) {
        tokenManager.saveTokens(response.accessToken, response.refreshToken)
        response.user?.let { 
            tokenManager.saveUserInfo(it.id.toString(), it.email) 
        }
    }
    
    // Onboarding status
    val hasCompletedOnboarding: Flow<Boolean> = tokenManager.hasSeenOnboarding()
    
    suspend fun setOnboardingCompleted() {
        tokenManager.setOnboardingSeen(true)
    }
}
