package com.shilora.app.domain.model

import java.util.Date

enum class ConfidenceLevel(val label: String) {
    HIGH("High Confidence"),
    MODERATE("Moderate Confidence"),
    LOW("Low Confidence"),
    UNCERTAIN("Needs Review")
}

data class InscriptionLine(
    val lineIndex: Int,
    val transcription: String,
    val bbox: List<Int>? = null,
    val cropPath: String? = null
)

data class BinarizationStats(
    val foregroundRatio: Float,
    val totalConnectedComponents: Int,
    val validCharacterCandidates: Int,
    val medianComponentArea: Float,
    val thresholdApplied: Float
)

data class ScanResult(
    val id: String,
    val localImagePath: String,
    val scannedAt: Date,
    val status: String,
    val binarizationStatus: String,
    val confidenceLevel: ConfidenceLevel,
    val confidenceScore: Float,
    val rawOcrText: String,
    val normalizedOldKannada: String,
    val modernKannada: String,
    val englishTranslation: String,
    val inscriptionSummary: String,
    val lines: List<InscriptionLine>,
    val uncertainTokens: List<String>,
    val binarizationStats: BinarizationStats?,
    val researchNotes: String? = null,
    val siteName: String? = null,
    val villageName: String? = null,
    val templeName: String? = null
)
