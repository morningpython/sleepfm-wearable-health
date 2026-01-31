package io.sleepfm.android.data.api

import io.sleepfm.android.data.local.TokenManager
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject

/**
 * Auth Interceptor - Adds JWT token to requests
 */
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Skip auth for public endpoints
        val publicEndpoints = listOf("/auth/login", "/auth/register", "/health")
        if (publicEndpoints.any { originalRequest.url.encodedPath.contains(it) }) {
            return chain.proceed(originalRequest)
        }
        
        // Get access token
        val token = runBlocking {
            tokenManager.getAccessToken().firstOrNull()
        }
        
        // Add Authorization header if token exists
        val request = if (!token.isNullOrEmpty()) {
            originalRequest.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
        } else {
            originalRequest
        }
        
        return chain.proceed(request)
    }
}
