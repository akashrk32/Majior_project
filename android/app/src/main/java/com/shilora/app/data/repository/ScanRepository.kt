package com.shilora.app.data.repository

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.shilora.app.data.api.ShiloraApiService
import com.shilora.app.data.api.ShiloraAnalyzeRequest
import com.shilora.app.data.api.ShiloraAnalyzeResponse
import com.shilora.app.data.local.ScanDao
import com.shilora.app.data.local.ScanEntity
import com.shilora.app.domain.model.BinarizationStats
import com.shilora.app.domain.model.ConfidenceLevel
import com.shilora.app.domain.model.InscriptionLine
import com.shilora.app.domain.model.ScanResult
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.io.File
import java.util.Date
import java.util.UUID

class ScanRepository(
    private val apiService: ShiloraApiService,
    private val scanDao: ScanDao,
    private val gson: Gson = Gson()
) {

    fun getAllScans(): Flow<List<ScanResult>> = getSavedScans()

    fun getSavedScans(): Flow<List<ScanResult>> {
        return scanDao.getAllScans().map { entities ->
            entities.map { it.toDomain(gson) }
        }
    }

    suspend fun getScanById(id: String): ScanResult? {
        return withContext(Dispatchers.IO) {
            scanDao.getScanById(id)?.toDomain(gson)
        }
    }

    suspend fun analyzeImage(context: android.content.Context, uri: android.net.Uri): Result<ScanResult> {
        return withContext(Dispatchers.IO) {
            try {
                // Copy URI contents to a temporary cache file for processing
                val tempFile = File(context.cacheDir, "scan_${System.currentTimeMillis()}.jpg")
                context.contentResolver.openInputStream(uri)?.use { input ->
                    tempFile.outputStream().use { output ->
                        input.copyTo(output)
                    }
                } ?: return@withContext Result.failure(Exception("Cannot open image from URI"))

                analyzeInscription(tempFile.absolutePath)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    suspend fun analyzeInscription(imagePath: String): Result<ScanResult> {
        return withContext(Dispatchers.IO) {
            try {
                val file = File(imagePath)
                if (!file.exists()) {
                    return@withContext Result.failure(Exception("Image file does not exist: $imagePath"))
                }

                // Compress and encode to Base64 safely
                val bitmap = BitmapFactory.decodeFile(imagePath)
                    ?: return@withContext Result.failure(Exception("Could not decode image bitmap"))

                val outputStream = ByteArrayOutputStream()
                bitmap.compress(Bitmap.CompressFormat.JPEG, 90, outputStream)
                val imageBytes = outputStream.toByteArray()
                val imageBase64 = Base64.encodeToString(imageBytes, Base64.NO_WRAP)

                val request = ShiloraAnalyzeRequest(
                    imageBase64 = imageBase64,
                    inscriptionName = "scan_${System.currentTimeMillis()}"
                )

                val response = apiService.analyzeInscriptionJson(request)
                if (!response.isSuccessful) {
                    val errorBody = response.errorBody()?.string() ?: "Server returned code ${response.code()}"
                    return@withContext Result.failure(Exception("Analysis failed: $errorBody"))
                }

                val body = response.body()
                    ?: return@withContext Result.failure(Exception("Empty response body from server"))

                if (body.pipelineStatus == "UNSUPPORTED_OR_UNREADABLE") {
                    return@withContext Result.failure(Exception("SHILORA could not read enough of this inscription reliably. Check lighting and framing."))
                }

                val domainResult = mapResponseToDomain(body, imagePath)
                // Save to local scan library automatically
                scanDao.insertScan(domainResult.toEntity(gson))

                Result.success(domainResult)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    suspend fun updateResearchNotes(
        id: String,
        notes: String?,
        site: String?,
        village: String?,
        temple: String?
    ) {
        withContext(Dispatchers.IO) {
            scanDao.updateResearchNotes(id, notes, site, village, temple)
        }
    }

    suspend fun deleteScan(id: String) {
        withContext(Dispatchers.IO) {
            scanDao.deleteScan(id)
        }
    }

    private fun mapResponseToDomain(body: ShiloraAnalyzeResponse, imagePath: String): ScanResult {
        val ocrConf = body.stageConfidences?.ocrConfidence ?: 0.5f
        val transConf = body.stageConfidences?.translationLexicalConfidence ?: 0.0f
        val avgConf = (ocrConf + transConf) / 2.0f

        val level = when {
            avgConf >= 0.70f -> ConfidenceLevel.HIGH
            avgConf >= 0.40f -> ConfidenceLevel.MODERATE
            avgConf >= 0.20f -> ConfidenceLevel.LOW
            else -> ConfidenceLevel.UNCERTAIN
        }

        val lines = body.lines?.map { dto ->
            InscriptionLine(
                lineIndex = dto.lineIndex,
                transcription = dto.transcription ?: "",
                bbox = dto.bbox,
                cropPath = dto.cropPath
            )
        } ?: emptyList()

        val stats = body.binarizationMetrics?.let {
            BinarizationStats(
                foregroundRatio = it.foregroundRatio ?: 0f,
                totalConnectedComponents = it.totalConnectedComponents ?: 0,
                validCharacterCandidates = it.validCharacterCandidates ?: 0,
                medianComponentArea = it.medianComponentArea ?: 0f,
                thresholdApplied = it.thresholdApplied ?: 0.2f
            )
        }

        return ScanResult(
            id = UUID.randomUUID().toString(),
            localImagePath = imagePath,
            scannedAt = Date(),
            status = body.pipelineStatus ?: "SUCCESS",
            binarizationStatus = body.binarizationStatus ?: "SUCCESS",
            confidenceLevel = level,
            confidenceScore = avgConf,
            rawOcrText = body.rawOcrText ?: "",
            normalizedOldKannada = body.normalizedOldKannada ?: "",
            modernKannada = body.modernKannada ?: "",
            englishTranslation = body.english ?: "",
            inscriptionSummary = body.inscriptionSummary ?: "No inscription summary available.",
            lines = lines,
            uncertainTokens = body.uncertainTokens ?: emptyList(),
            binarizationStats = stats
        )
    }
}

fun ScanEntity.toDomain(gson: Gson): ScanResult {
    val lineListType = object : TypeToken<List<InscriptionLine>>() {}.type
    val tokenListType = object : TypeToken<List<String>>() {}.type
    val lines: List<InscriptionLine> = gson.fromJson(linesJson, lineListType) ?: emptyList()
    val uncertain: List<String> = gson.fromJson(uncertainTokensJson, tokenListType) ?: emptyList()

    return ScanResult(
        id = id,
        localImagePath = localImagePath,
        scannedAt = Date(timestamp),
        status = status,
        binarizationStatus = binarizationStatus,
        confidenceLevel = try { ConfidenceLevel.valueOf(confidenceLevel) } catch (e: Exception) { ConfidenceLevel.MODERATE },
        confidenceScore = confidenceScore,
        rawOcrText = rawOcrText,
        normalizedOldKannada = normalizedOldKannada,
        modernKannada = modernKannada,
        englishTranslation = englishTranslation,
        inscriptionSummary = inscriptionSummary,
        lines = lines,
        uncertainTokens = uncertain,
        binarizationStats = BinarizationStats(
            foregroundRatio = foregroundRatio,
            totalConnectedComponents = validCharacterCandidates,
            validCharacterCandidates = validCharacterCandidates,
            medianComponentArea = 50f,
            thresholdApplied = 0.2f
        ),
        researchNotes = researchNotes,
        siteName = siteName,
        villageName = villageName,
        templeName = templeName
    )
}

fun ScanResult.toEntity(gson: Gson): ScanEntity {
    return ScanEntity(
        id = id,
        localImagePath = localImagePath,
        timestamp = scannedAt.time,
        status = status,
        binarizationStatus = binarizationStatus,
        confidenceLevel = confidenceLevel.name,
        confidenceScore = confidenceScore,
        rawOcrText = rawOcrText,
        normalizedOldKannada = normalizedOldKannada,
        modernKannada = modernKannada,
        englishTranslation = englishTranslation,
        inscriptionSummary = inscriptionSummary,
        linesJson = gson.toJson(lines),
        uncertainTokensJson = gson.toJson(uncertainTokens),
        foregroundRatio = binarizationStats?.foregroundRatio ?: 0f,
        validCharacterCandidates = binarizationStats?.validCharacterCandidates ?: 0,
        researchNotes = researchNotes,
        siteName = siteName,
        villageName = villageName,
        templeName = templeName
    )
}
