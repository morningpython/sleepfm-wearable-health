package io.sleepfm.wear.presentation.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit
import javax.inject.Inject

data class TrackingUiState(
    val elapsedTime: String = "00:00:00",
    val elapsedTimeMillis: Long = 0L,
    val currentHeartRate: Float? = null,
    val currentSpO2: Float? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class TrackingViewModel @Inject constructor(
    private val sleepTrackingRepository: SleepTrackingRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(TrackingUiState())
    val uiState: StateFlow<TrackingUiState> = _uiState.asStateFlow()
    
    init {
        observeSensorData()
        startElapsedTimeCounter()
    }
    
    private fun observeSensorData() {
        viewModelScope.launch {
            sleepTrackingRepository.heartRateFlow.collect { reading ->
                reading?.let {
                    _uiState.update { state -> state.copy(currentHeartRate = it.value) }
                    sleepTrackingRepository.saveHeartRateReading(it)
                }
            }
        }
        
        viewModelScope.launch {
            sleepTrackingRepository.spO2Flow.collect { reading ->
                reading?.let {
                    _uiState.update { state -> state.copy(currentSpO2 = it.value) }
                    sleepTrackingRepository.saveSpO2Reading(it)
                }
            }
        }
    }
    
    private fun startElapsedTimeCounter() {
        viewModelScope.launch {
            sleepTrackingRepository.trackingState.collect { state ->
                if (state.isTracking && state.startTime != null) {
                    launchElapsedTimeUpdater(state.startTime)
                }
            }
        }
    }
    
    private fun launchElapsedTimeUpdater(startTime: Long) {
        viewModelScope.launch {
            while (true) {
                val elapsed = System.currentTimeMillis() - startTime
                _uiState.update { 
                    it.copy(
                        elapsedTime = formatElapsedTime(elapsed),
                        elapsedTimeMillis = elapsed
                    )
                }
                delay(1000)
            }
        }
    }
    
    private fun formatElapsedTime(millis: Long): String {
        val hours = TimeUnit.MILLISECONDS.toHours(millis)
        val minutes = TimeUnit.MILLISECONDS.toMinutes(millis) % 60
        val seconds = TimeUnit.MILLISECONDS.toSeconds(millis) % 60
        return String.format("%02d:%02d:%02d", hours, minutes, seconds)
    }
    
    fun stopTracking() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
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
}
