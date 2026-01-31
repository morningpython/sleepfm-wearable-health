package io.sleepfm.wear.tile

import androidx.wear.protolayout.ColorBuilders.argb
import androidx.wear.protolayout.DimensionBuilders.*
import androidx.wear.protolayout.LayoutElementBuilders.*
import androidx.wear.protolayout.ResourceBuilders.*
import androidx.wear.protolayout.TimelineBuilders.*
import androidx.wear.tiles.*
import androidx.wear.tiles.RequestBuilders.*
import com.google.common.util.concurrent.Futures
import com.google.common.util.concurrent.ListenableFuture
import dagger.hilt.android.AndroidEntryPoint
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.guava.future
import javax.inject.Inject

@AndroidEntryPoint
class SleepTileService : TileService() {
    
    companion object {
        private const val RESOURCES_VERSION = "1"
    }
    
    @Inject
    lateinit var sleepTrackingRepository: SleepTrackingRepository
    
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    
    override fun onTileRequest(requestParams: TileRequest): ListenableFuture<TileBuilders.Tile> {
        return scope.future {
            val isTracking = sleepTrackingRepository.isTracking.first()
            val lastSession = sleepTrackingRepository.getLastSession()
            
            TileBuilders.Tile.Builder()
                .setResourcesVersion(RESOURCES_VERSION)
                .setFreshnessIntervalMillis(60_000) // 1분마다 갱신
                .setTileTimeline(
                    Timeline.Builder()
                        .addTimelineEntry(
                            TimelineEntry.Builder()
                                .setLayout(
                                    Layout.Builder()
                                        .setRoot(createTileLayout(isTracking, lastSession?.durationMinutes))
                                        .build()
                                )
                                .build()
                        )
                        .build()
                )
                .build()
        }
    }
    
    override fun onTileResourcesRequest(requestParams: ResourcesRequest): ListenableFuture<Resources> {
        return Futures.immediateFuture(
            Resources.Builder()
                .setVersion(RESOURCES_VERSION)
                .build()
        )
    }
    
    private fun createTileLayout(isTracking: Boolean, lastSleepMinutes: Int?): LayoutElement {
        return Box.Builder()
            .setWidth(expand())
            .setHeight(expand())
            .setHorizontalAlignment(HORIZONTAL_ALIGN_CENTER)
            .setVerticalAlignment(VERTICAL_ALIGN_CENTER)
            .addContent(
                Column.Builder()
                    .setWidth(expand())
                    .setHorizontalAlignment(HORIZONTAL_ALIGN_CENTER)
                    .addContent(createTitleText())
                    .addContent(createSpacer(8))
                    .addContent(createStatusContent(isTracking, lastSleepMinutes))
                    .addContent(createSpacer(8))
                    .addContent(createActionHint(isTracking))
                    .build()
            )
            .build()
    }
    
    private fun createTitleText(): LayoutElement {
        return Text.Builder()
            .setText("SleepFM")
            .setFontStyle(
                FontStyle.Builder()
                    .setSize(sp(12f))
                    .setColor(argb(0xFF9C9C9C.toInt()))
                    .build()
            )
            .build()
    }
    
    private fun createStatusContent(isTracking: Boolean, lastSleepMinutes: Int?): LayoutElement {
        return if (isTracking) {
            createTrackingContent()
        } else {
            createLastSleepContent(lastSleepMinutes)
        }
    }
    
    private fun createTrackingContent(): LayoutElement {
        return Column.Builder()
            .setHorizontalAlignment(HORIZONTAL_ALIGN_CENTER)
            .addContent(
                Text.Builder()
                    .setText("🌙")
                    .setFontStyle(FontStyle.Builder().setSize(sp(32f)).build())
                    .build()
            )
            .addContent(
                Text.Builder()
                    .setText("수면 추적 중")
                    .setFontStyle(
                        FontStyle.Builder()
                            .setSize(sp(14f))
                            .setColor(argb(0xFF4ECDC4.toInt()))
                            .build()
                    )
                    .build()
            )
            .build()
    }
    
    private fun createLastSleepContent(lastSleepMinutes: Int?): LayoutElement {
        val sleepText = if (lastSleepMinutes != null) {
            val hours = lastSleepMinutes / 60
            val minutes = lastSleepMinutes % 60
            "${hours}시간 ${minutes}분"
        } else {
            "--"
        }
        
        return Column.Builder()
            .setHorizontalAlignment(HORIZONTAL_ALIGN_CENTER)
            .addContent(
                Text.Builder()
                    .setText(sleepText)
                    .setFontStyle(
                        FontStyle.Builder()
                            .setSize(sp(24f))
                            .setColor(argb(0xFFFFFFFF.toInt()))
                            .build()
                    )
                    .build()
            )
            .addContent(
                Text.Builder()
                    .setText("지난 밤 수면")
                    .setFontStyle(
                        FontStyle.Builder()
                            .setSize(sp(12f))
                            .setColor(argb(0xFF9C9C9C.toInt()))
                            .build()
                    )
                    .build()
            )
            .build()
    }
    
    private fun createActionHint(isTracking: Boolean): LayoutElement {
        val hintText = if (isTracking) "탭하여 확인" else "탭하여 시작"
        
        return Text.Builder()
            .setText(hintText)
            .setFontStyle(
                FontStyle.Builder()
                    .setSize(sp(10f))
                    .setColor(argb(0xFF666666.toInt()))
                    .build()
            )
            .build()
    }
    
    private fun createSpacer(height: Int): LayoutElement {
        return Spacer.Builder()
            .setHeight(dp(height.toFloat()))
            .build()
    }
}
