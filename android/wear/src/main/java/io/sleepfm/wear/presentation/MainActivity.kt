package io.sleepfm.wear.presentation

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.Composable
import dagger.hilt.android.AndroidEntryPoint
import io.sleepfm.wear.presentation.navigation.WearNavHost
import io.sleepfm.wear.presentation.theme.SleepFMWearTheme

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            SleepFMWearTheme {
                WearNavHost()
            }
        }
    }
}
