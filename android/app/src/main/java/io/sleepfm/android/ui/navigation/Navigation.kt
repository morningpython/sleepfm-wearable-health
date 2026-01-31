package io.sleepfm.android.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import io.sleepfm.android.ui.screens.auth.LoginScreen
import io.sleepfm.android.ui.screens.auth.SignUpScreen
import io.sleepfm.android.ui.screens.dashboard.DashboardScreen
import io.sleepfm.android.ui.screens.history.HistoryScreen
import io.sleepfm.android.ui.screens.main.MainScreen
import io.sleepfm.android.ui.screens.onboarding.OnboardingScreen
import io.sleepfm.android.ui.screens.settings.SettingsScreen

/**
 * Navigation Routes
 */
sealed class Screen(val route: String) {
    object Onboarding : Screen("onboarding")
    object Login : Screen("login")
    object SignUp : Screen("signup")
    object Main : Screen("main")
    object Dashboard : Screen("dashboard")
    object History : Screen("history")
    object Settings : Screen("settings")
}

/**
 * Main Navigation Host
 */
@Composable
fun SleepFMNavHost(
    navController: NavHostController = rememberNavController(),
    viewModel: NavigationViewModel = hiltViewModel()
) {
    val isLoggedIn by viewModel.isLoggedIn.collectAsState()
    val hasSeenOnboarding by viewModel.hasSeenOnboarding.collectAsState()
    
    val startDestination = when {
        !hasSeenOnboarding -> Screen.Onboarding.route
        isLoggedIn -> Screen.Main.route
        else -> Screen.Login.route
    }
    
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        // Onboarding
        composable(Screen.Onboarding.route) {
            OnboardingScreen(
                onComplete = {
                    viewModel.setOnboardingSeen()
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }
        
        // Login
        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.Main.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateToSignUp = {
                    navController.navigate(Screen.SignUp.route)
                }
            )
        }
        
        // Sign Up
        composable(Screen.SignUp.route) {
            SignUpScreen(
                onSignUpSuccess = {
                    navController.navigate(Screen.Main.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // Main (with Bottom Navigation)
        composable(Screen.Main.route) {
            MainScreen(
                onLogout = {
                    viewModel.logout()
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Main.route) { inclusive = true }
                    }
                }
            )
        }
    }
}
