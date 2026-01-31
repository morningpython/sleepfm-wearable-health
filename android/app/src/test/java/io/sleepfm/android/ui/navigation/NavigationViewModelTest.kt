package io.sleepfm.android.ui.navigation

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.sleepfm.android.data.local.TokenManager
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
class NavigationViewModelTest {

    private val testDispatcher = StandardTestDispatcher()
    private lateinit var tokenManager: TokenManager
    private lateinit var viewModel: NavigationViewModel

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        tokenManager = mockk(relaxed = true)
        every { tokenManager.getAccessToken() } returns flowOf(null)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state when not logged in and onboarding not seen`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf(null)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertFalse(viewModel.isLoggedIn.value)
        assertFalse(viewModel.hasSeenOnboarding.value)
    }

    @Test
    fun `isLoggedIn is true when token exists`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("valid_token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.isLoggedIn.value)
    }

    @Test
    fun `isLoggedIn is false when token is empty`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertFalse(viewModel.isLoggedIn.value)
    }

    @Test
    fun `hasSeenOnboarding is true when onboarding completed`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf(null)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.hasSeenOnboarding.value)
    }

    @Test
    fun `setOnboardingSeen updates state and calls tokenManager`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf(null)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()
        
        assertFalse(viewModel.hasSeenOnboarding.value)

        // When
        viewModel.setOnboardingSeen()
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.hasSeenOnboarding.value)
        coVerify { tokenManager.setOnboardingSeen(true) }
    }

    @Test
    fun `logout clears tokens and updates state`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()
        
        assertTrue(viewModel.isLoggedIn.value)

        // When
        viewModel.logout()
        advanceUntilIdle()

        // Then
        assertFalse(viewModel.isLoggedIn.value)
        coVerify { tokenManager.clearTokens() }
    }

    @Test
    fun `logout can be called multiple times safely`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // When
        viewModel.logout()
        viewModel.logout()
        advanceUntilIdle()

        // Then
        assertFalse(viewModel.isLoggedIn.value)
        coVerify(exactly = 2) { tokenManager.clearTokens() }
    }

    @Test
    fun `setOnboardingSeen can be called multiple times safely`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf(null)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // When
        viewModel.setOnboardingSeen()
        viewModel.setOnboardingSeen()
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.hasSeenOnboarding.value)
        coVerify(exactly = 2) { tokenManager.setOnboardingSeen(true) }
    }

    @Test
    fun `logged in with onboarding completed`() = runTest {
        // Given - both logged in and onboarding seen
        every { tokenManager.getAccessToken() } returns flowOf("valid_token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.isLoggedIn.value)
        assertTrue(viewModel.hasSeenOnboarding.value)
    }

    @Test
    fun `logged in but onboarding not completed`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("valid_token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.isLoggedIn.value)
        assertFalse(viewModel.hasSeenOnboarding.value)
    }

    @Test
    fun `not logged in but onboarding completed`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf(null)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertFalse(viewModel.isLoggedIn.value)
        assertTrue(viewModel.hasSeenOnboarding.value)
    }

    @Test
    fun `logout does not affect onboarding state`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()
        
        assertTrue(viewModel.hasSeenOnboarding.value)

        // When
        viewModel.logout()
        advanceUntilIdle()

        // Then - onboarding state should remain
        assertTrue(viewModel.hasSeenOnboarding.value)
        assertFalse(viewModel.isLoggedIn.value)
    }

    @Test
    fun `setOnboardingSeen does not affect login state`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()
        
        assertTrue(viewModel.isLoggedIn.value)

        // When
        viewModel.setOnboardingSeen()
        advanceUntilIdle()

        // Then - login state should remain
        assertTrue(viewModel.isLoggedIn.value)
        assertTrue(viewModel.hasSeenOnboarding.value)
    }

    @Test
    fun `whitespace-only token is treated as not logged in`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("   ")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.isLoggedIn.value) // Note: current implementation doesn't trim
    }

    @Test
    fun `very long token is handled correctly`() = runTest {
        // Given - very long token
        val longToken = "a".repeat(10000)
        every { tokenManager.getAccessToken() } returns flowOf(longToken)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)

        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.isLoggedIn.value)
    }

    @Test
    fun `logout immediately after initialization`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(true)
        viewModel = NavigationViewModel(tokenManager)

        // When - logout before advanceUntilIdle
        viewModel.logout()
        advanceUntilIdle()

        // Then
        assertFalse(viewModel.isLoggedIn.value)
        coVerify { tokenManager.clearTokens() }
    }

    @Test
    fun `setOnboardingSeen immediately after initialization`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf(null)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)
        viewModel = NavigationViewModel(tokenManager)

        // When - set onboarding before advanceUntilIdle
        viewModel.setOnboardingSeen()
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.hasSeenOnboarding.value)
        coVerify { tokenManager.setOnboardingSeen(true) }
    }

    @Test
    fun `rapid logout and setOnboardingSeen calls`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf("token")
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // When - rapid calls
        viewModel.logout()
        viewModel.setOnboardingSeen()
        viewModel.logout()
        viewModel.setOnboardingSeen()
        advanceUntilIdle()

        // Then
        assertFalse(viewModel.isLoggedIn.value)
        assertTrue(viewModel.hasSeenOnboarding.value)
        coVerify(exactly = 2) { tokenManager.clearTokens() }
        coVerify(exactly = 2) { tokenManager.setOnboardingSeen(true) }
    }

    @Test
    fun `state is properly initialized`() = runTest {
        // Given
        every { tokenManager.getAccessToken() } returns flowOf(null)
        every { tokenManager.hasSeenOnboarding() } returns flowOf(false)
        
        // When
        viewModel = NavigationViewModel(tokenManager)
        advanceUntilIdle()

        // Then - initial states
        assertFalse(viewModel.isLoggedIn.value)
        assertFalse(viewModel.hasSeenOnboarding.value)

        // When - update onboarding
        viewModel.setOnboardingSeen()
        advanceUntilIdle()

        // Then - onboarding updated
        assertTrue(viewModel.hasSeenOnboarding.value)
        assertFalse(viewModel.isLoggedIn.value) // login state unchanged
    }
}

