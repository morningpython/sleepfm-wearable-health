package io.sleepfm.wear.presentation.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.sleepfm.wear.data.repository.PhoneConnectionRepository
import io.sleepfm.wear.data.repository.SettingsRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val isPhoneConnected: Boolean = false,
    val autoTrackingEnabled: Boolean = false,
    val hapticFeedbackEnabled: Boolean = true,
    val lastSyncTime: String = "없음",
    val isSyncing: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val phoneConnectionRepository: PhoneConnectionRepository,
    private val settingsRepository: SettingsRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()
    
    init {
        observePhoneConnection()
        loadSettings()
    }
    
    private fun observePhoneConnection() {
        viewModelScope.launch {
            phoneConnectionRepository.connectionStatus.collect { status ->
                _uiState.update { it.copy(isPhoneConnected = status.isConnected) }
            }
        }
    }
    
    private fun loadSettings() {
        viewModelScope.launch {
            combine(
                settingsRepository.autoTrackingEnabled,
                settingsRepository.hapticFeedbackEnabled
            ) { autoTracking, haptic ->
                Pair(autoTracking, haptic)
            }.collect { (autoTracking, haptic) ->
                _uiState.update {
                    it.copy(
                        autoTrackingEnabled = autoTracking,
                        hapticFeedbackEnabled = haptic
                    )
                }
            }
        }
    }
    
    fun setAutoTracking(enabled: Boolean) {
        viewModelScope.launch {
            settingsRepository.setAutoTrackingEnabled(enabled)
        }
    }
    
    fun setHapticFeedback(enabled: Boolean) {
        viewModelScope.launch {
            settingsRepository.setHapticFeedbackEnabled(enabled)
        }
    }
    
    fun syncWithPhone() {
        viewModelScope.launch {
            _uiState.update { it.copy(isSyncing = true, error = null) }
            val result = phoneConnectionRepository.requestSyncFromPhone()
            _uiState.update { 
                it.copy(
                    isSyncing = false,
                    error = result.exceptionOrNull()?.message
                )
            }
        }
    }
}
