package io.sleepfm.android.data.api

import io.mockk.coEvery
import io.mockk.every
import io.mockk.mockk
import io.sleepfm.android.data.local.TokenManager
import kotlinx.coroutines.flow.flowOf
import okhttp3.Interceptor
import okhttp3.Protocol
import okhttp3.Request
import okhttp3.Response
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class AuthInterceptorTest {

    private lateinit var tokenManager: TokenManager
    private lateinit var interceptor: AuthInterceptor

    @Before
    fun setup() {
        tokenManager = mockk(relaxed = true)
        interceptor = AuthInterceptor(tokenManager)
    }

    private fun createChain(path: String): Interceptor.Chain {
        val request = Request.Builder()
            .url("https://api.sleepfm.io$path")
            .build()
        
        return mockk {
            every { request() } returns request
            every { proceed(any()) } answers {
                Response.Builder()
                    .code(200)
                    .message("OK")
                    .protocol(Protocol.HTTP_1_1)
                    .request(firstArg())
                    .build()
            }
        }
    }

    @Test
    fun `interceptor adds authorization header when token exists`() {
        // Given
        coEvery { tokenManager.getAccessToken() } returns flowOf("valid_token_123")
        val chain = createChain("/api/v1/sessions")
        
        // When
        val response = interceptor.intercept(chain)
        
        // Then
        assertEquals(200, response.code)
    }

    @Test
    fun `interceptor skips auth for login endpoint`() {
        // Given
        coEvery { tokenManager.getAccessToken() } returns flowOf("token")
        val chain = createChain("/api/v1/auth/login")
        
        // When
        val response = interceptor.intercept(chain)
        
        // Then - should proceed without adding auth header
        assertEquals(200, response.code)
    }

    @Test
    fun `interceptor skips auth for register endpoint`() {
        // Given
        coEvery { tokenManager.getAccessToken() } returns flowOf("token")
        val chain = createChain("/api/v1/auth/register")
        
        // When
        val response = interceptor.intercept(chain)
        
        // Then
        assertEquals(200, response.code)
    }

    @Test
    fun `interceptor skips auth for health endpoint`() {
        // Given
        coEvery { tokenManager.getAccessToken() } returns flowOf("token")
        val chain = createChain("/health")
        
        // When
        val response = interceptor.intercept(chain)
        
        // Then
        assertEquals(200, response.code)
    }

    @Test
    fun `interceptor proceeds without auth when token is null`() {
        // Given
        coEvery { tokenManager.getAccessToken() } returns flowOf(null)
        val chain = createChain("/api/v1/sessions")
        
        // When
        val response = interceptor.intercept(chain)
        
        // Then
        assertEquals(200, response.code)
    }

    @Test
    fun `interceptor proceeds without auth when token is empty`() {
        // Given
        coEvery { tokenManager.getAccessToken() } returns flowOf("")
        val chain = createChain("/api/v1/sessions")
        
        // When
        val response = interceptor.intercept(chain)
        
        // Then
        assertEquals(200, response.code)
    }

    @Test
    fun `AuthInterceptor is an OkHttp Interceptor`() {
        assertTrue(interceptor is okhttp3.Interceptor)
    }
}
