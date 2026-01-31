package io.sleepfm.wear.presentation.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import io.sleepfm.wear.data.repository.PhoneConnectionRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val isTracking: Boolean = false,
    val lastSleepDuration: String? = null,
    val isPhoneConnected: Boolean = false,
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val sleepTrackingRepository: SleepTrackingRepository,
    private val phoneConnectionRepository: PhoneConnectionRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    
    init {
        observeTrackingState()
        observePhoneConnection()
        loadLastSleepData()
    }
    
    private fun observeTrackingState() {
        viewModelScope.launch {
            sleepTrackingRepository.isTracking.collect { isTracking ->
                _uiState.update { it.copy(isTracking = isTracking) }
            }
        }
    }
    
    private fun observePhoneConnection() {
        viewModelScope.launch {
            phoneConnectionRepository.connectionStatus.collect { status ->
                _uiState.update { it.copy(isPhoneConnected = status.isConnected) }
            }
        }
    }
    
    private fun loadLastSleepData() {
        viewModelScope.launch {
            val lastSession = sleepTrackingRepository.getLastSession()
            lastSession?.let { session ->
                val hours = session.durationMinutes / 60
                val minutes = session.durationMinutes % 60
                _uiState.update { 
                    it.copy(lastSleepDuration = "${hours}시간 ${minutes}분")
                }
            }
        }
    }
    
    fun startTracking() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                sleepTrackingRepository.startTracking()
                _uiState.update { it.copy(isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(isLoading = false, error = e.message ?: "추적을 시작할 수 없습니다")
                }
            }
        }
    }
    
    fun stopTracking() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                sleepTrackingRepository.stopTracking()
                _uiState.update { it.copy(isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(isLoading = false, error = e.message ?: "추적을 중지할 수 없습니다")
                }
            }
        }
    }
    
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
