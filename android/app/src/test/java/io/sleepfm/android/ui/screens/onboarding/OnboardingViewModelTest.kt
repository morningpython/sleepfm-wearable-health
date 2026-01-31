package io.sleepfm.android.ui.screens.onboarding

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.sleepfm.android.data.repository.AuthRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class OnboardingViewModelTest {

    private val testDispatcher = StandardTestDispatcher()
    private lateinit var authRepository: AuthRepository
    private lateinit var viewModel: OnboardingViewModel

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        authRepository = mockk(relaxed = true)
        viewModel = OnboardingViewModel(authRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `completeOnboarding should call authRepository setOnboardingCompleted`() = runTest {
        // When
        viewModel.completeOnboarding()
        advanceUntilIdle()
        
        // Then
        coVerify { authRepository.setOnboardingCompleted() }
    }

    @Test
    fun `completeOnboarding can be called multiple times`() = runTest {
        // When
        viewModel.completeOnboarding()
        viewModel.completeOnboarding()
        advanceUntilIdle()
        
        // Then
        coVerify(exactly = 2) { authRepository.setOnboardingCompleted() }
    }

    @Test
    fun `viewModel is initialized correctly`() {
        assertNotNull(viewModel)
    }

    @Test
    fun `completeOnboarding succeeds when repository works`() = runTest {
        // Given
        coEvery { authRepository.setOnboardingCompleted() } just runs

        // When
        viewModel.completeOnboarding()
        advanceUntilIdle()

        // Then
        coVerify(exactly = 1) { authRepository.setOnboardingCompleted() }
    }
}
