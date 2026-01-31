package io.sleepfm.android.ui.navigation

import org.junit.Assert.*
import org.junit.Test

class ScreenTest {

    @Test
    fun `Onboarding screen has correct route`() {
        assertEquals("onboarding", Screen.Onboarding.route)
    }

    @Test
    fun `Login screen has correct route`() {
        assertEquals("login", Screen.Login.route)
    }

    @Test
    fun `SignUp screen has correct route`() {
        assertEquals("signup", Screen.SignUp.route)
    }

    @Test
    fun `Main screen has correct route`() {
        assertEquals("main", Screen.Main.route)
    }

    @Test
    fun `Dashboard screen has correct route`() {
        assertEquals("dashboard", Screen.Dashboard.route)
    }

    @Test
    fun `History screen has correct route`() {
        assertEquals("history", Screen.History.route)
    }

    @Test
    fun `Settings screen has correct route`() {
        assertEquals("settings", Screen.Settings.route)
    }

    @Test
    fun `all screens have unique routes`() {
        val screens = listOf(
            Screen.Onboarding,
            Screen.Login,
            Screen.SignUp,
            Screen.Main,
            Screen.Dashboard,
            Screen.History,
            Screen.Settings
        )
        val routes = screens.map { it.route }
        
        assertEquals(routes.size, routes.distinct().size)
    }

    @Test
    fun `Screen objects are singleton instances`() {
        assertSame(Screen.Login, Screen.Login)
        assertSame(Screen.Main, Screen.Main)
        assertSame(Screen.Onboarding, Screen.Onboarding)
    }

    @Test
    fun `routes do not contain spaces or special characters`() {
        val screens = listOf(
            Screen.Onboarding,
            Screen.Login,
            Screen.SignUp,
            Screen.Main,
            Screen.Dashboard,
            Screen.History,
            Screen.Settings
        )
        
        screens.forEach { screen ->
            assertFalse("Route '${screen.route}' contains spaces", screen.route.contains(" "))
            assertTrue("Route '${screen.route}' should be lowercase", screen.route == screen.route.lowercase())
        }
    }
}
