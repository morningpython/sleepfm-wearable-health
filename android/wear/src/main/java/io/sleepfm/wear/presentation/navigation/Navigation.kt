package io.sleepfm.wear.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.wear.compose.navigation.SwipeDismissableNavHost
import androidx.wear.compose.navigation.composable
import androidx.wear.compose.navigation.rememberSwipeDismissableNavController
import io.sleepfm.wear.presentation.screens.HomeScreen
import io.sleepfm.wear.presentation.screens.TrackingScreen
import io.sleepfm.wear.presentation.screens.SummaryScreen
import io.sleepfm.wear.presentation.screens.SettingsScreen

sealed class WearScreen(val route: String) {
    object Home : WearScreen("home")
    object Tracking : WearScreen("tracking")
    object Summary : WearScreen("summary")
    object Settings : WearScreen("settings")
}

@Composable
fun WearNavHost() {
    val navController = rememberSwipeDismissableNavController()
    
    SwipeDismissableNavHost(
        navController = navController,
        startDestination = WearScreen.Home.route
    ) {
        composable(WearScreen.Home.route) {
            HomeScreen(
                onStartTracking = {
                    navController.navigate(WearScreen.Tracking.route)
                },
                onViewSummary = {
                    navController.navigate(WearScreen.Summary.route)
                },
                onOpenSettings = {
                    navController.navigate(WearScreen.Settings.route)
                }
            )
        }
        
        composable(WearScreen.Tracking.route) {
            TrackingScreen(
                onStopTracking = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(WearScreen.Summary.route) {
            SummaryScreen()
        }
        
        composable(WearScreen.Settings.route) {
            SettingsScreen()
        }
    }
}
