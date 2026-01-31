package io.sleepfm.android.ui.screens.settings

import io.mockk.*
import io.sleepfm.android.data.local.UserPreferences
import io.sleepfm.android.data.repository.AuthRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class SettingsViewModelTest {

    private lateinit var viewModel: SettingsViewModel
    private lateinit var authRepository: AuthRepository
    private lateinit var userPreferences: UserPreferences
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        authRepository = mockk(relaxed = true)
        userPreferences = mockk(relaxed = true)
        
        // Default preferences
        every { userPreferences.notificationsEnabled } returns flowOf(true)
        every { userPreferences.darkModeEnabled } returns flowOf(false)
        every { userPreferences.autoTrackingEnabled } returns flowOf(true)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    // ========== Initial State Tests ==========

    @Test
    fun `initial state should load user preferences`() = runTest {
        // Given
        coEvery { authRepository.getCurrentUser() } returns mockk {
            every { email } returns "test@example.com"
            every { username } returns "TestUser"
        }

        // When
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertTrue(state.notificationsEnabled)
        assertFalse(state.darkModeEnabled)
        assertTrue(state.autoTrackingEnabled)
        assertEquals("test@example.com", state.userEmail)
    }

    // ========== Toggle Settings Tests ==========

    @Test
    fun `toggleNotifications should update preference`() = runTest {
        // Given
        coEvery { userPreferences.setNotificationsEnabled(any()) } just Runs
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()

        // When
        viewModel.toggleNotifications(false)
        advanceUntilIdle()

        // Then
        coVerify { userPreferences.setNotificationsEnabled(false) }
    }

    @Test
    fun `toggleDarkMode should update preference`() = runTest {
        // Given
        coEvery { userPreferences.setDarkModeEnabled(any()) } just Runs
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()

        // When
        viewModel.toggleDarkMode(true)
        advanceUntilIdle()

        // Then
        coVerify { userPreferences.setDarkModeEnabled(true) }
    }

    @Test
    fun `toggleAutoTracking should update preference`() = runTest {
        // Given
        coEvery { userPreferences.setAutoTrackingEnabled(any()) } just Runs
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()

        // When
        viewModel.toggleAutoTracking(false)
        advanceUntilIdle()

        // Then
        coVerify { userPreferences.setAutoTrackingEnabled(false) }
    }

    // ========== Logout Tests ==========

    @Test
    fun `logout should call auth repository and show success`() = runTest {
        // Given
        coEvery { authRepository.logout() } returns Result.success(Unit)
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()

        // When
        viewModel.logout()
        advanceUntilIdle()

        // Then
        coVerify { authRepository.logout() }
        assertTrue(viewModel.uiState.value.logoutSuccess)
    }

    @Test
    fun `logout should show error on failure`() = runTest {
        // Given
        coEvery { authRepository.logout() } returns Result.failure(RuntimeException("Network error"))
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()

        // When
        viewModel.logout()
        advanceUntilIdle()

        // Then
        assertNotNull(viewModel.uiState.value.error)
        assertFalse(viewModel.uiState.value.logoutSuccess)
    }

    // ========== Data Export Tests ==========

    @Test
    fun `exportData should trigger data export`() = runTest {
        // Given
        coEvery { authRepository.exportUserData() } returns Result.success("export_url")
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()

        // When
        viewModel.exportData()
        advanceUntilIdle()

        // Then
        coVerify { authRepository.exportUserData() }
        assertEquals("export_url", viewModel.uiState.value.exportUrl)
    }

    // ========== Delete Account Tests ==========

    @Test
    fun `deleteAccount should require confirmation`() = runTest {
        // Given
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()

        // When
        viewModel.requestDeleteAccount()

        // Then
        assertTrue(viewModel.uiState.value.showDeleteConfirmation)
    }

    @Test
    fun `confirmDeleteAccount should delete account`() = runTest {
        // Given
        coEvery { authRepository.deleteAccount() } returns Result.success(Unit)
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()
        viewModel.requestDeleteAccount()

        // When
        viewModel.confirmDeleteAccount()
        advanceUntilIdle()

        // Then
        coVerify { authRepository.deleteAccount() }
        assertTrue(viewModel.uiState.value.accountDeleted)
    }

    @Test
    fun `cancelDeleteAccount should hide confirmation`() = runTest {
        // Given
        viewModel = SettingsViewModel(authRepository, userPreferences)
        advanceUntilIdle()
        viewModel.requestDeleteAccount()

        // When
        viewModel.cancelDeleteAccount()

        // Then
        assertFalse(viewModel.uiState.value.showDeleteConfirmation)
    }
}
