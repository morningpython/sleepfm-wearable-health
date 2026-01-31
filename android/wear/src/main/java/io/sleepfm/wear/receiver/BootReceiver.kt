package io.sleepfm.wear.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import dagger.hilt.android.AndroidEntryPoint
import io.sleepfm.wear.data.repository.SettingsRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class BootReceiver : BroadcastReceiver() {
    
    @Inject
    lateinit var settingsRepository: SettingsRepository
    
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    
    override fun onReceive(context: Context, intent: Intent?) {
        if (intent?.action != Intent.ACTION_BOOT_COMPLETED) {
            return
        }
        
        val pendingResult = goAsync()
        
        scope.launch {
            try {
                val settings = settingsRepository.settings.first()
                
                // Auto-tracking 기능이 활성화되어 있으면 서비스 준비
                if (settings.autoTrackingEnabled) {
                    // 서비스를 즉시 시작하지 않고 알람 설정만 진행
                    // 취침 시간에 자동으로 시작되도록 설정
                    scheduleBedtimeTracking(context, settings)
                }
            } finally {
                pendingResult.finish()
            }
        }
    }
    
    private fun scheduleBedtimeTracking(
        context: Context,
        settings: SettingsRepository.WearSettings
    ) {
        // 취침 시간 알람 설정
        // 실제 구현에서는 AlarmManager를 사용하여 취침 시간에 서비스 시작
        // 이 예제에서는 간단히 로그만 남김
        android.util.Log.d(
            "BootReceiver",
            "Scheduled bedtime tracking: ${settings.bedtimeHour}:${settings.bedtimeMinute}"
        )
    }
}
