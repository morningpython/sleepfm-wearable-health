package io.sleepfm.wear.di

import android.content.Context
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import io.sleepfm.wear.data.local.SleepDataStore
import io.sleepfm.wear.data.repository.PhoneConnectionRepository
import io.sleepfm.wear.data.repository.SettingsRepository
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import io.sleepfm.wear.service.SensorDataManager
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object WearModule {
    
    @Provides
    @Singleton
    fun provideGson(): Gson {
        return GsonBuilder()
            .setLenient()
            .create()
    }
    
    @Provides
    @Singleton
    fun provideSleepDataStore(
        @ApplicationContext context: Context,
        gson: Gson
    ): SleepDataStore {
        return SleepDataStore(context, gson)
    }
    
    @Provides
    @Singleton
    fun provideSensorDataManager(
        @ApplicationContext context: Context
    ): SensorDataManager {
        return SensorDataManager(context)
    }
    
    @Provides
    @Singleton
    fun provideSleepTrackingRepository(
        sensorDataManager: SensorDataManager,
        sleepDataStore: SleepDataStore
    ): SleepTrackingRepository {
        return SleepTrackingRepository(sensorDataManager, sleepDataStore)
    }
    
    @Provides
    @Singleton
    fun providePhoneConnectionRepository(
        @ApplicationContext context: Context,
        gson: Gson
    ): PhoneConnectionRepository {
        return PhoneConnectionRepository(context, gson)
    }
    
    @Provides
    @Singleton
    fun provideSettingsRepository(
        @ApplicationContext context: Context
    ): SettingsRepository {
        return SettingsRepository(context)
    }
}
