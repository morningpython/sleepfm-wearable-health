package io.sleepfm.android.ui.screens.auth

import org.junit.Assert.*
import org.junit.Test

class AuthUiStateTest {

    @Test
    fun `default AuthUiState has correct initial values`() {
        val state = AuthUiState()
        
        assertFalse(state.isLoading)
        assertFalse(state.isLoggedIn)
        assertNull(state.error)
    }

    @Test
    fun `AuthUiState with isLoading true`() {
        val state = AuthUiState(isLoading = true)
        
        assertTrue(state.isLoading)
        assertFalse(state.isLoggedIn)
        assertNull(state.error)
    }

    @Test
    fun `AuthUiState with isLoggedIn true`() {
        val state = AuthUiState(isLoggedIn = true)
        
        assertFalse(state.isLoading)
        assertTrue(state.isLoggedIn)
        assertNull(state.error)
    }

    @Test
    fun `AuthUiState with error message`() {
        val state = AuthUiState(error = "Login failed")
        
        assertFalse(state.isLoading)
        assertFalse(state.isLoggedIn)
        assertEquals("Login failed", state.error)
    }

    @Test
    fun `AuthUiState copy preserves unchanged values`() {
        val original = AuthUiState(isLoading = true, isLoggedIn = false, error = "Error")
        val copied = original.copy(isLoading = false)
        
        assertFalse(copied.isLoading)
        assertFalse(copied.isLoggedIn)
        assertEquals("Error", copied.error)
    }

    @Test
    fun `AuthUiState equality works correctly`() {
        val state1 = AuthUiState(isLoading = true, isLoggedIn = false, error = null)
        val state2 = AuthUiState(isLoading = true, isLoggedIn = false, error = null)
        val state3 = AuthUiState(isLoading = false, isLoggedIn = false, error = null)
        
        assertEquals(state1, state2)
        assertNotEquals(state1, state3)
    }

    @Test
    fun `AuthUiState hashCode is consistent`() {
        val state1 = AuthUiState(isLoading = true, isLoggedIn = false, error = "Test")
        val state2 = AuthUiState(isLoading = true, isLoggedIn = false, error = "Test")
        
        assertEquals(state1.hashCode(), state2.hashCode())
    }

    @Test
    fun `AuthUiState with all fields set`() {
        val state = AuthUiState(
            isLoading = true,
            isLoggedIn = true,
            error = "Some error"
        )
        
        assertTrue(state.isLoading)
        assertTrue(state.isLoggedIn)
        assertEquals("Some error", state.error)
    }
}
