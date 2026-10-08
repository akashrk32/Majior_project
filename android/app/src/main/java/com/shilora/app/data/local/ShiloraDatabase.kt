package com.shilora.app.data.local

import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase
import androidx.room.TypeConverter
import androidx.room.TypeConverters
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.shilora.app.domain.model.ConfidenceLevel
import com.shilora.app.domain.model.InscriptionLine
import kotlinx.coroutines.flow.Flow
import java.util.Date

@Entity(tableName = "scans")
data class ScanEntity(
    @PrimaryKey val id: String,
    val localImagePath: String,
    val timestamp: Long,
    val status: String,
    val binarizationStatus: String,
    val confidenceLevel: String,
    val confidenceScore: Float,
    val rawOcrText: String,
    val normalizedOldKannada: String,
    val modernKannada: String,
    val englishTranslation: String,
    val inscriptionSummary: String,
    val linesJson: String,
    val uncertainTokensJson: String,
    val foregroundRatio: Float,
    val validCharacterCandidates: Int,
    val researchNotes: String? = null,
    val siteName: String? = null,
    val villageName: String? = null,
    val templeName: String? = null
)

@Dao
interface ScanDao {
    @Query("SELECT * FROM scans ORDER BY timestamp DESC")
    fun getAllScans(): Flow<List<ScanEntity>>

    @Query("SELECT * FROM scans WHERE id = :id")
    suspend fun getScanById(id: String): ScanEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertScan(scan: ScanEntity)

    @Query("UPDATE scans SET researchNotes = :notes, siteName = :site, villageName = :village, templeName = :temple WHERE id = :id")
    suspend fun updateResearchNotes(id: String, notes: String?, site: String?, village: String?, temple: String?)

    @Query("DELETE FROM scans WHERE id = :id")
    suspend fun deleteScan(id: String)
}

class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? = date?.time
}

@Database(entities = [ScanEntity::class], version = 1, exportSchema = false)
@TypeConverters(Converters::class)
abstract class ShiloraDatabase : RoomDatabase() {
    abstract fun scanDao(): ScanDao
}
