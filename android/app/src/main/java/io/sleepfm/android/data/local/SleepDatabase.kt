package io.sleepfm.android.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import io.sleepfm.android.data.local.dao.SleepSessionDao
import io.sleepfm.android.data.local.entity.SleepSessionEntity

/**
 * Sleep Database - Room Database for local caching
 */
@Database(
    entities = [SleepSessionEntity::class],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class SleepDatabase : RoomDatabase() {

    abstract fun sleepSessionDao(): SleepSessionDao

    companion object {
        private const val DATABASE_NAME = "sleepfm_database"

        @Volatile
        private var instance: SleepDatabase? = null

        fun getInstance(context: Context): SleepDatabase {
            return instance ?: synchronized(this) {
                instance ?: buildDatabase(context).also { instance = it }
            }
        }

        private fun buildDatabase(context: Context): SleepDatabase {
            return Room.databaseBuilder(
                context.applicationContext,
                SleepDatabase::class.java,
                DATABASE_NAME
            )
                .fallbackToDestructiveMigration()
                .build()
        }
    }
}
