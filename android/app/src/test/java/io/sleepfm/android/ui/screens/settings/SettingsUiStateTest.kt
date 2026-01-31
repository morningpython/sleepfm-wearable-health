package io.sleepfm.android.ui.screens.settings

import io.sleepfm.android.domain.model.User
import org.junit.Assert.*
import org.junit.Test

class SettingsUiStateTest {

    @Test
    fun `default SettingsUiState has correct initial values`() {
        val state = SettingsUiState()
        
        assertNull(state.user)
        assertFalse(state.isDarkMode)
        assertFalse(state.isHealthConnectConnected)
        assertEquals("없음", state.lastSyncTime)
        assertFalse(state.isLoggedOut)
    }

    @Test
    fun `SettingsUiState with user`() {
        val user = User(
            id = 1,
            email = "test@example.com",
            username = "testuser",
            createdAt = "2024-01-01",
            isActive = true
        )
        val state = SettingsUiState(user = user)
        
        assertNotNull(state.user)
        assertEquals("test@example.com", state.user?.email)
        assertEquals("testuser", state.user?.username)
    }

    @Test
    fun `SettingsUiState with dark mode enabled`() {
        val state = SettingsUiState(isDarkMode = true)
        
        assertTrue(state.isDarkMode)
    }

    @Test
    fun `SettingsUiState with Health Connect connected`() {
        val state = SettingsUiState(isHealthConnectConnected = true)
        
        assertTrue(state.isHealthConnectConnected)
    }

    @Test
    fun `SettingsUiState with last sync time`() {
        val state = SettingsUiState(lastSyncTime = "2024-01-30 14:30")
        
        assertEquals("2024-01-30 14:30", state.lastSyncTime)
    }

    @Test
    fun `SettingsUiState with logged out state`() {
        val state = SettingsUiState(isLoggedOut = true)
        
        assertTrue(state.isLoggedOut)
    }

    @Test
    fun `SettingsUiState copy preserves unchanged values`() {
        val user = User(1, "test@test.com", "test", null, true)
        val original = SettingsUiState(
            user = user,
            isDarkMode = false,
            isHealthConnectConnected = true
        )
        val copied = original.copy(isDarkMode = true)
        
        assertTrue(copied.isDarkMode)
        assertEquals(user, copied.user)
        assertTrue(copied.isHealthConnectConnected)
    }

    @Test
    fun `SettingsUiState equality works correctly`() {
        val state1 = SettingsUiState(isDarkMode = true)
        val state2 = SettingsUiState(isDarkMode = true)
        val state3 = SettingsUiState(isDarkMode = false)
        
        assertEquals(state1, state2)
        assertNotEquals(state1, state3)
    }

    @Test
    fun `SettingsUiState hashCode is consistent`() {
        val state1 = SettingsUiState(isDarkMode = true, lastSyncTime = "10:00")
        val state2 = SettingsUiState(isDarkMode = true, lastSyncTime = "10:00")
        
        assertEquals(state1.hashCode(), state2.hashCode())
    }

    @Test
    fun `SettingsUiState with all fields set`() {
        val user = User(42, "full@test.com", "fulluser", "2024-01-01", true)
        val state = SettingsUiState(
            user = user,
            isDarkMode = true,
            isHealthConnectConnected = true,
            lastSyncTime = "2024-01-30 15:00",
            isLoggedOut = false
        )
        
        assertNotNull(state.user)
        assertTrue(state.isDarkMode)
        assertTrue(state.isHealthConnectConnected)
        assertEquals("2024-01-30 15:00", state.lastSyncTime)
        assertFalse(state.isLoggedOut)
    }
}
