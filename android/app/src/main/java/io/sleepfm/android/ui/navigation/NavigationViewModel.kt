package io.sleepfm.android.ui.navigation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.sleepfm.android.data.local.TokenManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Navigation ViewModel
 * Manages authentication state and onboarding status for navigation decisions.
 */
@HiltViewModel
class NavigationViewModel @Inject constructor(
    private val tokenManager: TokenManager
) : ViewModel() {

    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()

    private val _hasSeenOnboarding = MutableStateFlow(false)
    val hasSeenOnboarding: StateFlow<Boolean> = _hasSeenOnboarding.asStateFlow()

    init {
        checkAuthState()
        checkOnboardingState()
    }

    private fun checkAuthState() {
        viewModelScope.launch {
            tokenManager.getAccessToken().collect { token ->
                _isLoggedIn.value = !token.isNullOrEmpty()
            }
        }
    }

    private fun checkOnboardingState() {
        viewModelScope.launch {
            tokenManager.hasSeenOnboarding().collect { seen ->
                _hasSeenOnboarding.value = seen
            }
        }
    }

    fun setOnboardingSeen() {
        viewModelScope.launch {
            tokenManager.setOnboardingSeen(true)
            _hasSeenOnboarding.value = true
        }
    }

    fun logout() {
        viewModelScope.launch {
            tokenManager.clearTokens()
            _isLoggedIn.value = false
        }
    }
}
