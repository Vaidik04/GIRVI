package com.girvi.nativeapp.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [CustomerEntity::class, LoanEntity::class, PaymentEntity::class],
    version = 1,
    exportSchema = false
)
abstract class GirviDatabase : RoomDatabase() {
    abstract fun girviDao(): GirviDao

    companion object {
        @Volatile
        private var INSTANCE: GirviDatabase? = null

        fun get(context: Context): GirviDatabase {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    GirviDatabase::class.java,
                    "girvi_native.db"
                ).build().also { INSTANCE = it }
            }
        }
    }
}
