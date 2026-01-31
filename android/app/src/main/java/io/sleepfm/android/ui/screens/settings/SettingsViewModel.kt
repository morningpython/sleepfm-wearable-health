package io.sleepfm.android.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.sleepfm.android.data.repository.AuthRepository
import io.sleepfm.android.domain.model.User
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val user: User? = null,
    val isDarkMode: Boolean = false,
    val isHealthConnectConnected: Boolean = false,
    val lastSyncTime: String = "없음",
    val isLoggedOut: Boolean = false
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()
    
    init {
        loadUserInfo()
    }
    
    private fun loadUserInfo() {
        viewModelScope.launch {
            // Try to get user info from API
            authRepository.getMe().onSuccess { user ->
                _uiState.update { it.copy(user = user) }
            }
        }
    }
    
    fun setDarkMode(enabled: Boolean) {
        _uiState.update { it.copy(isDarkMode = enabled) }
        // TODO: Save preference to DataStore
    }
    
    fun syncData() {
        viewModelScope.launch {
            // TODO: Implement data sync
            val currentTime = java.text.SimpleDateFormat(
                "yyyy-MM-dd HH:mm", 
                java.util.Locale.getDefault()
            ).format(java.util.Date())
            
            _uiState.update { it.copy(lastSyncTime = currentTime) }
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _uiState.update { it.copy(isLoggedOut = true) }
        }
    }
}
