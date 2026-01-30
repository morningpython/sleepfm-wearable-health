package io.sleepfm.android.di

import android.content.Context
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import io.sleepfm.android.data.local.SleepDatabase
import io.sleepfm.android.data.local.TokenManager
import javax.inject.Singleton

/**
 * App Module - Provides application-wide dependencies
 */
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideTokenManager(
        @ApplicationContext context: Context
    ): TokenManager {
        return TokenManager(context)
    }

    @Provides
    @Singleton
    fun provideSleepDatabase(
        @ApplicationContext context: Context
    ): SleepDatabase {
        return SleepDatabase.getInstance(context)
    }
}
