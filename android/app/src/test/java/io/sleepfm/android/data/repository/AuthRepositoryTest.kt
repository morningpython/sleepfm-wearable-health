package io.sleepfm.android.data.repository

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import io.sleepfm.android.data.api.SleepFMApi
import io.sleepfm.android.data.local.TokenManager
import io.sleepfm.android.domain.model.AuthResponse
import io.sleepfm.android.domain.model.User
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import retrofit2.Response

class AuthRepositoryTest {

    private lateinit var api: SleepFMApi
    private lateinit var tokenManager: TokenManager
    private lateinit var repository: AuthRepository

    @Before
    fun setup() {
        api = mockk()
        tokenManager = mockk(relaxed = true)
        repository = AuthRepository(api, tokenManager)
    }

    @Test
    fun `login success saves tokens`() = runTest {
        // Given
        val email = "test@test.com"
        val password = "password123"
        val user = User(
            id = 1,
            email = email,
            username = "testuser",
            createdAt = "2026-01-01T00:00:00",
            isActive = true
        )
        val authResponse = AuthResponse(
            accessToken = "access_token",
            refreshToken = "refresh_token",
            tokenType = "Bearer",
            user = user
        )
        coEvery { api.login(any()) } returns Response.success(authResponse)

        // When
        val result = repository.login(email, password)

        // Then
        assertTrue(result.isSuccess)
        assertEquals(authResponse, result.getOrNull())
        coVerify { tokenManager.saveTokens("access_token", "refresh_token") }
        coVerify { tokenManager.saveUserInfo("1", email) }
    }

    @Test
    fun `login failure returns error`() = runTest {
        // Given
        coEvery { api.login(any()) } returns Response.error(401, mockk(relaxed = true))

        // When
        val result = repository.login("test@test.com", "wrong")

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `logout clears tokens`() = runTest {
        // When
        repository.logout()

        // Then
        coVerify { tokenManager.clearTokens() }
    }

    @Test
    fun `isLoggedIn returns token state`() = runTest {
        // Given
        coEvery { tokenManager.getAccessToken() } returns flowOf("some_token")

        // Then
        repository.isLoggedIn.collect { isLoggedIn ->
            assertTrue(isLoggedIn)
        }
    }

    @Test
    fun `register success saves tokens`() = runTest {
        // Given
        val email = "new@test.com"
        val password = "password123"
        val username = "newuser"
        val user = User(
            id = 2,
            email = email,
            username = username,
            createdAt = "2026-01-01T00:00:00",
            isActive = true
        )
        val authResponse = AuthResponse(
            accessToken = "new_access",
            refreshToken = "new_refresh",
            tokenType = "Bearer",
            user = user
        )
        coEvery { api.register(any()) } returns Response.success(authResponse)

        // When
        val result = repository.register(email, password, username)

        // Then
        assertTrue(result.isSuccess)
        coVerify { tokenManager.saveTokens("new_access", "new_refresh") }
    }

    @Test
    fun `register failure returns error`() = runTest {
        // Given
        coEvery { api.register(any()) } returns Response.error(400, mockk(relaxed = true))

        // When
        val result = repository.register("test@test.com", "password", "user")

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `getMe returns user on success`() = runTest {
        // Given
        val user = User(
            id = 1,
            email = "test@test.com",
            username = "testuser",
            createdAt = "2026-01-01T00:00:00",
            isActive = true
        )
        coEvery { api.getCurrentUser() } returns Response.success(user)

        // When
        val result = repository.getMe()

        // Then
        assertTrue(result.isSuccess)
        assertEquals(user, result.getOrNull())
    }

    @Test
    fun `getMe returns failure on error`() = runTest {
        // Given
        coEvery { api.getCurrentUser() } returns Response.error(401, mockk(relaxed = true))

        // When
        val result = repository.getMe()

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `refreshToken success saves new tokens`() = runTest {
        // Given
        val authResponse = AuthResponse(
            accessToken = "new_access",
            refreshToken = "new_refresh",
            tokenType = "Bearer",
            user = null
        )
        coEvery { tokenManager.getRefreshToken() } returns flowOf("old_refresh")
        coEvery { api.refreshToken(any()) } returns Response.success(authResponse)

        // When
        val result = repository.refreshToken()

        // Then
        assertTrue(result.isSuccess)
        coVerify { tokenManager.saveTokens("new_access", "new_refresh") }
    }

    @Test
    fun `refreshToken fails when no refresh token`() = runTest {
        // Given
        coEvery { tokenManager.getRefreshToken() } returns flowOf(null)

        // When
        val result = repository.refreshToken()

        // Then
        assertTrue(result.isFailure)
    }

    @Test
    fun `login handles exception`() = runTest {
        // Given
        coEvery { api.login(any()) } throws RuntimeException("Network error")

        // When
        val result = repository.login("test@test.com", "password")

        // Then
        assertTrue(result.isFailure)
    }
}
