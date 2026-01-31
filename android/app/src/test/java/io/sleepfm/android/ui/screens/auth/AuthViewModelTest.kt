package io.sleepfm.android.ui.screens.auth

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import io.sleepfm.android.data.repository.AuthRepository
import io.sleepfm.android.domain.model.AuthResponse
import io.sleepfm.android.domain.model.User
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class AuthViewModelTest {

    private lateinit var authRepository: AuthRepository
    private lateinit var viewModel: AuthViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        authRepository = mockk(relaxed = true)
        coEvery { authRepository.isLoggedIn } returns flowOf(false)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state is not loading and not logged in`() = runTest {
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertFalse(state.isLoggedIn)
        assertNull(state.error)
    }

    @Test
    fun `login success updates state to logged in`() = runTest {
        // Given
        val user = User(
            id = 1,
            email = "test@test.com",
            username = "testuser",
            createdAt = "2026-01-01T00:00:00",
            isActive = true
        )
        val authResponse = AuthResponse(
            accessToken = "token",
            refreshToken = "refresh",
            tokenType = "Bearer",
            user = user
        )
        coEvery { authRepository.login(any(), any()) } returns Result.success(authResponse)
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.login("test@test.com", "password123")
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertTrue(state.isLoggedIn)
        assertNull(state.error)
        coVerify { authRepository.login("test@test.com", "password123") }
    }

    @Test
    fun `login failure updates state with error`() = runTest {
        // Given
        coEvery { authRepository.login(any(), any()) } returns Result.failure(
            Exception("Invalid credentials")
        )
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.login("test@test.com", "wrong")
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertFalse(state.isLoggedIn)
        assertEquals("Invalid credentials", state.error)
    }

    @Test
    fun `register success updates state to logged in`() = runTest {
        // Given
        val user = User(
            id = 1,
            email = "new@test.com",
            username = "newuser",
            createdAt = "2026-01-01T00:00:00",
            isActive = true
        )
        val authResponse = AuthResponse(
            accessToken = "token",
            refreshToken = "refresh",
            tokenType = "Bearer",
            user = user
        )
        coEvery { authRepository.register(any(), any(), any()) } returns Result.success(authResponse)
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.register("new@test.com", "password123", "newuser")
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertTrue(state.isLoggedIn)
        coVerify { authRepository.register("new@test.com", "password123", "newuser") }
    }

    @Test
    fun `register failure updates state with error`() = runTest {
        // Given
        coEvery { authRepository.register(any(), any(), any()) } returns Result.failure(
            Exception("Email already exists")
        )
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.register("existing@test.com", "password", "user")
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals("Email already exists", state.error)
    }

    @Test
    fun `clearError clears error state`() = runTest {
        // Given
        coEvery { authRepository.login(any(), any()) } returns Result.failure(
            Exception("Error")
        )
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()
        viewModel.login("test@test.com", "wrong")
        advanceUntilIdle()
        assertNotNull(viewModel.uiState.value.error)

        // When
        viewModel.clearError()

        // Then
        assertNull(viewModel.uiState.value.error)
    }

    @Test
    fun `login shows loading state during operation`() = runTest {
        // Given
        coEvery { authRepository.login(any(), any()) } coAnswers {
            kotlinx.coroutines.delay(100)
            Result.success(mockk(relaxed = true))
        }
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.login("test@test.com", "password")

        // Advance partially to check loading state
        testDispatcher.scheduler.advanceTimeBy(50)

        // Then - should be loading
        assertTrue(viewModel.uiState.value.isLoading)

        // Complete the operation
        advanceUntilIdle()

        // Then - should not be loading anymore
        assertFalse(viewModel.uiState.value.isLoading)
    }

    @Test
    fun `register shows loading state during operation`() = runTest {
        // Given
        coEvery { authRepository.register(any(), any(), any()) } coAnswers {
            kotlinx.coroutines.delay(100)
            Result.success(mockk(relaxed = true))
        }
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.register("test@test.com", "password", "username")

        // Advance partially to check loading state
        testDispatcher.scheduler.advanceTimeBy(50)

        // Then - should be loading
        assertTrue(viewModel.uiState.value.isLoading)

        // Complete the operation
        advanceUntilIdle()

        // Then - should not be loading anymore
        assertFalse(viewModel.uiState.value.isLoading)
    }

    @Test
    fun `isLoggedIn flow updates state when repository changes`() = runTest {
        // Given - user is logged in
        coEvery { authRepository.isLoggedIn } returns flowOf(true)
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.uiState.value.isLoggedIn)
    }

    @Test
    fun `login clears previous error before starting`() = runTest {
        // Given - set up an initial error
        coEvery { authRepository.login(any(), any()) } returnsMany listOf(
            Result.failure(Exception("First error")),
            Result.success(mockk(relaxed = true))
        )
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // First login fails
        viewModel.login("test@test.com", "wrong")
        advanceUntilIdle()
        assertEquals("First error", viewModel.uiState.value.error)

        // When - login again (success)
        viewModel.login("test@test.com", "correct")
        advanceUntilIdle()
        
        // Then - error should be cleared and login succeeds
        assertNull(viewModel.uiState.value.error)
        assertTrue(viewModel.uiState.value.isLoggedIn)
    }

    @Test
    fun `register clears previous error before starting`() = runTest {
        // Given - set up an initial error
        coEvery { authRepository.register(any(), any(), any()) } returnsMany listOf(
            Result.failure(Exception("First error")),
            Result.success(mockk(relaxed = true))
        )
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // First register fails
        viewModel.register("test@test.com", "pass", "user")
        advanceUntilIdle()
        assertEquals("First error", viewModel.uiState.value.error)

        // When - register again
        viewModel.register("test2@test.com", "pass", "user2")
        advanceUntilIdle()
        
        // Then - error should be cleared
        assertNull(viewModel.uiState.value.error)
        assertTrue(viewModel.uiState.value.isLoggedIn)
    }

    @Test
    fun `login with null exception message shows default error`() = runTest {
        // Given
        coEvery { authRepository.login(any(), any()) } returns Result.failure(
            Exception(null as String?)
        )
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.login("test@test.com", "wrong")
        advanceUntilIdle()

        // Then - should show default Korean error message
        assertEquals("로그인에 실패했습니다", viewModel.uiState.value.error)
    }

    @Test
    fun `register with null exception message shows default error`() = runTest {
        // Given
        coEvery { authRepository.register(any(), any(), any()) } returns Result.failure(
            Exception(null as String?)
        )
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.register("test@test.com", "pass", "user")
        advanceUntilIdle()

        // Then - should show default Korean error message
        assertEquals("회원가입에 실패했습니다", viewModel.uiState.value.error)
    }

    @Test
    fun `clearError does not affect other state properties`() = runTest {
        // Given - login fails and we have an error
        coEvery { authRepository.login(any(), any()) } returns Result.failure(
            Exception("Error")
        )
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()
        viewModel.login("test@test.com", "wrong")
        advanceUntilIdle()
        
        val stateBeforeClear = viewModel.uiState.value

        // When
        viewModel.clearError()

        // Then
        val stateAfterClear = viewModel.uiState.value
        assertNull(stateAfterClear.error)
        assertEquals(stateBeforeClear.isLoading, stateAfterClear.isLoading)
        assertEquals(stateBeforeClear.isLoggedIn, stateAfterClear.isLoggedIn)
    }

    @Test
    fun `multiple rapid login calls should be handled correctly`() = runTest {
        // Given
        coEvery { authRepository.login(any(), any()) } coAnswers {
            kotlinx.coroutines.delay(50)
            Result.success(mockk(relaxed = true))
        }
        viewModel = AuthViewModel(authRepository)
        advanceUntilIdle()

        // When - rapid login calls
        viewModel.login("test1@test.com", "pass1")
        viewModel.login("test2@test.com", "pass2")
        advanceUntilIdle()

        // Then - both calls should complete without crash
        assertTrue(viewModel.uiState.value.isLoggedIn)
    }
}
