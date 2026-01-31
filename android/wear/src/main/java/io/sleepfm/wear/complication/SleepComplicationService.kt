package io.sleepfm.wear.complication

import androidx.wear.watchface.complications.data.*
import androidx.wear.watchface.complications.datasource.ComplicationDataSourceService
import androidx.wear.watchface.complications.datasource.ComplicationRequest
import dagger.hilt.android.AndroidEntryPoint
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import javax.inject.Inject

@AndroidEntryPoint
class SleepComplicationService : ComplicationDataSourceService() {
    
    @Inject
    lateinit var sleepTrackingRepository: SleepTrackingRepository
    
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    
    override fun getPreviewData(type: ComplicationType): ComplicationData? {
        return when (type) {
            ComplicationType.SHORT_TEXT -> createShortTextPreview()
            ComplicationType.LONG_TEXT -> createLongTextPreview()
            ComplicationType.RANGED_VALUE -> createRangedValuePreview()
            ComplicationType.SMALL_IMAGE -> createSmallImagePreview()
            else -> null
        }
    }
    
    override fun onComplicationRequest(
        request: ComplicationRequest,
        listener: ComplicationRequestListener
    ) {
        val data = runBlocking {
            createComplicationData(request.complicationType)
        }
        
        if (data != null) {
            listener.onComplicationData(data)
        } else {
            listener.onComplicationData(null)
        }
    }
    
    private suspend fun createComplicationData(type: ComplicationType): ComplicationData? {
        val isTracking = sleepTrackingRepository.isTracking.first()
        val lastSession = sleepTrackingRepository.getLastSession()
        
        return when (type) {
            ComplicationType.SHORT_TEXT -> createShortTextData(isTracking, lastSession?.durationMinutes)
            ComplicationType.LONG_TEXT -> createLongTextData(isTracking, lastSession?.durationMinutes)
            ComplicationType.RANGED_VALUE -> createRangedValueData(lastSession?.durationMinutes)
            ComplicationType.SMALL_IMAGE -> createSmallImageData(isTracking)
            else -> null
        }
    }
    
    private fun createShortTextPreview(): ComplicationData {
        return ShortTextComplicationData.Builder(
            text = PlainComplicationText.Builder("7h").build(),
            contentDescription = PlainComplicationText.Builder("수면 시간").build()
        )
            .setTitle(PlainComplicationText.Builder("수면").build())
            .build()
    }
    
    private fun createLongTextPreview(): ComplicationData {
        return LongTextComplicationData.Builder(
            text = PlainComplicationText.Builder("7시간 30분").build(),
            contentDescription = PlainComplicationText.Builder("지난 밤 수면").build()
        )
            .setTitle(PlainComplicationText.Builder("지난 밤 수면").build())
            .build()
    }
    
    private fun createRangedValuePreview(): ComplicationData {
        return RangedValueComplicationData.Builder(
            value = 7.5f,
            min = 0f,
            max = 10f,
            contentDescription = PlainComplicationText.Builder("수면 시간").build()
        )
            .setText(PlainComplicationText.Builder("7.5h").build())
            .setTitle(PlainComplicationText.Builder("수면").build())
            .build()
    }
    
    private fun createSmallImagePreview(): ComplicationData {
        return SmallImageComplicationData.Builder(
            smallImage = SmallImage.Builder(
                image = createMoonIcon(),
                type = SmallImageType.ICON
            ).build(),
            contentDescription = PlainComplicationText.Builder("수면 추적").build()
        ).build()
    }
    
    private fun createShortTextData(isTracking: Boolean, sleepMinutes: Int?): ComplicationData {
        val text = if (isTracking) {
            "추적 중"
        } else if (sleepMinutes != null) {
            val hours = sleepMinutes / 60
            val minutes = sleepMinutes % 60
            if (minutes > 0) "${hours}h${minutes}m" else "${hours}h"
        } else {
            "--"
        }
        
        return ShortTextComplicationData.Builder(
            text = PlainComplicationText.Builder(text).build(),
            contentDescription = PlainComplicationText.Builder("수면 시간").build()
        )
            .setTitle(PlainComplicationText.Builder("수면").build())
            .setTapAction(createTapAction())
            .build()
    }
    
    private fun createLongTextData(isTracking: Boolean, sleepMinutes: Int?): ComplicationData {
        val title = if (isTracking) "수면 추적 중" else "지난 밤 수면"
        val text = if (isTracking) {
            "탭하여 확인"
        } else if (sleepMinutes != null) {
            val hours = sleepMinutes / 60
            val minutes = sleepMinutes % 60
            "${hours}시간 ${minutes}분"
        } else {
            "데이터 없음"
        }
        
        return LongTextComplicationData.Builder(
            text = PlainComplicationText.Builder(text).build(),
            contentDescription = PlainComplicationText.Builder(title).build()
        )
            .setTitle(PlainComplicationText.Builder(title).build())
            .setTapAction(createTapAction())
            .build()
    }
    
    private fun createRangedValueData(sleepMinutes: Int?): ComplicationData {
        val hours = (sleepMinutes ?: 0) / 60f
        val text = if (sleepMinutes != null) {
            String.format("%.1fh", hours)
        } else {
            "--"
        }
        
        return RangedValueComplicationData.Builder(
            value = hours.coerceIn(0f, 12f),
            min = 0f,
            max = 10f, // 목표 수면 시간 10시간
            contentDescription = PlainComplicationText.Builder("수면 시간").build()
        )
            .setText(PlainComplicationText.Builder(text).build())
            .setTitle(PlainComplicationText.Builder("수면").build())
            .setTapAction(createTapAction())
            .build()
    }
    
    private fun createSmallImageData(isTracking: Boolean): ComplicationData {
        return SmallImageComplicationData.Builder(
            smallImage = SmallImage.Builder(
                image = createMoonIcon(),
                type = SmallImageType.ICON
            ).build(),
            contentDescription = PlainComplicationText.Builder(
                if (isTracking) "수면 추적 중" else "수면 추적"
            ).build()
        )
            .setTapAction(createTapAction())
            .build()
    }
    
    private fun createMoonIcon(): android.graphics.drawable.Icon {
        return android.graphics.drawable.Icon.createWithResource(
            this,
            android.R.drawable.ic_popup_sync // 기본 아이콘 사용 (실제로는 커스텀 아이콘 사용)
        )
    }
    
    private fun createTapAction(): android.app.PendingIntent {
        val intent = packageManager.getLaunchIntentForPackage(packageName)
        return android.app.PendingIntent.getActivity(
            this,
            0,
            intent,
            android.app.PendingIntent.FLAG_UPDATE_CURRENT or android.app.PendingIntent.FLAG_IMMUTABLE
        )
    }
}
