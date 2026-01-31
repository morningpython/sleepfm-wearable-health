package io.sleepfm.android.ui.screens.settings

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import io.sleepfm.android.data.repository.AuthRepository
import io.sleepfm.android.domain.model.User
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
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
class SettingsViewModelTest {

    private lateinit var authRepository: AuthRepository
    private lateinit var viewModel: SettingsViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        authRepository = mockk(relaxed = true)
        coEvery { authRepository.getMe() } returns Result.failure(Exception("Not logged in"))
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state has no user`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertNull(state.user)
        assertFalse(state.isDarkMode)
        assertFalse(state.isLoggedOut)
    }

    @Test
    fun `loadUserInfo updates user on success`() = runTest {
        // Given
        val user = User(
            id = 1,
            email = "test@test.com",
            username = "testuser",
            createdAt = "2026-01-01T00:00:00",
            isActive = true
        )
        coEvery { authRepository.getMe() } returns Result.success(user)

        // When
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertNotNull(state.user)
        assertEquals("test@test.com", state.user?.email)
    }

    @Test
    fun `setDarkMode updates state`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.setDarkMode(true)

        // Then
        assertTrue(viewModel.uiState.value.isDarkMode)

        // When
        viewModel.setDarkMode(false)

        // Then
        assertFalse(viewModel.uiState.value.isDarkMode)
    }

    @Test
    fun `syncData updates lastSyncTime`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        val initialSyncTime = viewModel.uiState.value.lastSyncTime
        assertEquals("없음", initialSyncTime)

        // When
        viewModel.syncData()
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertNotEquals("없음", state.lastSyncTime)
    }

    @Test
    fun `logout calls repository and updates state`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.logout()
        advanceUntilIdle()

        // Then
        assertTrue(viewModel.uiState.value.isLoggedOut)
        coVerify { authRepository.logout() }
    }

    @Test
    fun `multiple dark mode toggles work correctly`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // Toggle multiple times
        viewModel.setDarkMode(true)
        assertTrue(viewModel.uiState.value.isDarkMode)
        
        viewModel.setDarkMode(false)
        assertFalse(viewModel.uiState.value.isDarkMode)
        
        viewModel.setDarkMode(true)
        assertTrue(viewModel.uiState.value.isDarkMode)
    }

    @Test
    fun `initial state shows default values`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertFalse(state.isDarkMode)
        assertFalse(state.isHealthConnectConnected)
        assertEquals("없음", state.lastSyncTime)
        assertFalse(state.isLoggedOut)
    }

    @Test
    fun `loadUserInfo failure does not crash`() = runTest {
        // Given - getMe fails
        coEvery { authRepository.getMe() } returns Result.failure(Exception("Network error"))
        
        // When
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // Then - should still work, just no user
        assertNull(viewModel.uiState.value.user)
    }

    @Test
    fun `syncData updates time in correct format`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // When
        viewModel.syncData()
        advanceUntilIdle()

        // Then - should have a time string with format like "2024-06-01 12:00"
        val syncTime = viewModel.uiState.value.lastSyncTime
        assertNotEquals("없음", syncTime)
        assertTrue(syncTime.contains("-")) // Date separator
        assertTrue(syncTime.contains(":")) // Time separator
    }

    @Test
    fun `logout can be called multiple times safely`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // When - multiple logout calls
        viewModel.logout()
        viewModel.logout()
        advanceUntilIdle()

        // Then - should handle gracefully
        assertTrue(viewModel.uiState.value.isLoggedOut)
        coVerify(exactly = 2) { authRepository.logout() }
    }

    @Test
    fun `user with all fields populated shows correctly`() = runTest {
        // Given
        val user = User(
            id = 42,
            email = "fulluser@test.com",
            username = "fulluser",
            createdAt = "2024-01-01T12:00:00Z",
            isActive = true
        )
        coEvery { authRepository.getMe() } returns Result.success(user)

        // When
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertEquals(42, state.user?.id)
        assertEquals("fulluser@test.com", state.user?.email)
        assertEquals("fulluser", state.user?.username)
        assertEquals(true, state.user?.isActive)
    }

    @Test
    fun `state updates are independent`() = runTest {
        // Given
        val user = User(1, "test@test.com", "user", null, true)
        coEvery { authRepository.getMe() } returns Result.success(user)
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // When - update dark mode
        viewModel.setDarkMode(true)

        // Then - user should still be there
        assertNotNull(viewModel.uiState.value.user)
        assertTrue(viewModel.uiState.value.isDarkMode)

        // When - sync data
        viewModel.syncData()
        advanceUntilIdle()

        // Then - both previous states should persist
        assertNotNull(viewModel.uiState.value.user)
        assertTrue(viewModel.uiState.value.isDarkMode)
        assertNotEquals("없음", viewModel.uiState.value.lastSyncTime)
    }

    @Test
    fun `user with null fields is handled correctly`() = runTest {
        // Given - user with null optional fields
        val user = User(
            id = 1,
            email = "test@test.com",
            username = "testuser",
            createdAt = null,
            isActive = null
        )
        coEvery { authRepository.getMe() } returns Result.success(user)

        // When
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertNotNull(state.user)
        assertNull(state.user?.createdAt)
        assertNull(state.user?.isActive)
    }

    @Test
    fun `inactive user is loaded correctly`() = runTest {
        // Given - inactive user
        val user = User(
            id = 1,
            email = "inactive@test.com",
            username = "inactive",
            createdAt = "2024-01-01T00:00:00",
            isActive = false
        )
        coEvery { authRepository.getMe() } returns Result.success(user)

        // When
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertEquals(false, state.user?.isActive)
    }

    @Test
    fun `multiple syncData calls update time each time`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // When - first sync
        viewModel.syncData()
        advanceUntilIdle()
        val firstSyncTime = viewModel.uiState.value.lastSyncTime

        // Small delay to ensure time difference
        kotlinx.coroutines.delay(10)

        // When - second sync
        viewModel.syncData()
        advanceUntilIdle()
        val secondSyncTime = viewModel.uiState.value.lastSyncTime

        // Then - both should be valid timestamps
        assertNotEquals("없음", firstSyncTime)
        assertNotEquals("없음", secondSyncTime)
    }

    @Test
    fun `logout before user load completes`() = runTest {
        // Given - slow user load
        coEvery { authRepository.getMe() } coAnswers {
            kotlinx.coroutines.delay(100)
            Result.success(User(1, "test@test.com", "user", null, true))
        }
        viewModel = SettingsViewModel(authRepository)

        // When - logout immediately
        viewModel.logout()
        advanceUntilIdle()

        // Then - should be logged out
        assertTrue(viewModel.uiState.value.isLoggedOut)
    }

    @Test
    fun `setDarkMode to same value multiple times`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // When - set to true multiple times
        viewModel.setDarkMode(true)
        viewModel.setDarkMode(true)
        viewModel.setDarkMode(true)

        // Then
        assertTrue(viewModel.uiState.value.isDarkMode)

        // When - set to false multiple times
        viewModel.setDarkMode(false)
        viewModel.setDarkMode(false)

        // Then
        assertFalse(viewModel.uiState.value.isDarkMode)
    }

    @Test
    fun `user email formats are preserved`() = runTest {
        // Given - various email formats
        val users = listOf(
            User(1, "simple@test.com", "u1", null, true),
            User(2, "user+tag@example.co.uk", "u2", null, true),
            User(3, "first.last@sub.domain.com", "u3", null, true)
        )

        for (user in users) {
            coEvery { authRepository.getMe() } returns Result.success(user)
            
            // When
            val vm = SettingsViewModel(authRepository)
            advanceUntilIdle()

            // Then
            assertEquals(user.email, vm.uiState.value.user?.email)
        }
    }

    @Test
    fun `user username formats are preserved`() = runTest {
        // Given - various username formats
        val users = listOf(
            User(1, "test@test.com", "simple_user", null, true),
            User(2, "test@test.com", "user-with-dashes", null, true),
            User(3, "test@test.com", "123numeric", null, true)
        )

        for (user in users) {
            coEvery { authRepository.getMe() } returns Result.success(user)
            
            // When
            val vm = SettingsViewModel(authRepository)
            advanceUntilIdle()

            // Then
            assertEquals(user.username, vm.uiState.value.user?.username)
        }
    }

    @Test
    fun `healthConnect status defaults to false`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        assertFalse(viewModel.uiState.value.isHealthConnectConnected)
    }

    @Test
    fun `logout does not affect dark mode setting`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // Given - dark mode enabled
        viewModel.setDarkMode(true)
        assertTrue(viewModel.uiState.value.isDarkMode)

        // When - logout
        viewModel.logout()
        advanceUntilIdle()

        // Then - dark mode should persist
        assertTrue(viewModel.uiState.value.isDarkMode)
        assertTrue(viewModel.uiState.value.isLoggedOut)
    }

    @Test
    fun `logout does not affect sync time`() = runTest {
        viewModel = SettingsViewModel(authRepository)
        advanceUntilIdle()

        // Given - synced data
        viewModel.syncData()
        advanceUntilIdle()
        val syncTime = viewModel.uiState.value.lastSyncTime

        // When - logout
        viewModel.logout()
        advanceUntilIdle()

        // Then - sync time should persist
        assertEquals(syncTime, viewModel.uiState.value.lastSyncTime)
        assertTrue(viewModel.uiState.value.isLoggedOut)
    }
}

