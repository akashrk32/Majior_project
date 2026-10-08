package com.shilora.app.data.api

import com.google.gson.annotations.SerializedName

data class ShiloraAnalyzeRequest(
    @SerializedName("image") val imageBase64: String,
    @SerializedName("inscription_name") val inscriptionName: String = "mobile_capture"
)

data class ShiloraAnalyzeResponse(
    @SerializedName("success") val success: Boolean,
    @SerializedName("input_image") val inputImage: String?,
    @SerializedName("pipeline_status") val pipelineStatus: String?,
    @SerializedName("binarization_status") val binarizationStatus: String?,
    @SerializedName("segmentation_status") val segmentationStatus: String?,
    @SerializedName("line_reconstruction_status") val lineReconstructionStatus: String?,
    @SerializedName("ocr_status") val ocrStatus: String?,
    @SerializedName("translation_status") val translationStatus: String?,
    @SerializedName("stage_confidences") val stageConfidences: StageConfidencesDto?,
    @SerializedName("dimensions") val dimensions: DimensionsDto?,
    @SerializedName("timings_seconds") val timingsSeconds: Map<String, Float>?,
    @SerializedName("binarization_metrics") val binarizationMetrics: BinarizationMetricsDto?,
    @SerializedName("segmentation_summary") val segmentationSummary: SegmentationSummaryDto?,
    @SerializedName("raw_ocr_text") val rawOcrText: String?,
    @SerializedName("normalized_old_kannada") val normalizedOldKannada: String?,
    @SerializedName("modern_kannada") val modernKannada: String?,
    @SerializedName("english") val english: String?,
    @SerializedName("inscription_summary") val inscriptionSummary: String?,
    @SerializedName("uncertain_tokens") val uncertainTokens: List<String>?,
    @SerializedName("lines") val lines: List<LineDto>?,
    @SerializedName("warnings") val warnings: List<String>?
)

data class StageConfidencesDto(
    @SerializedName("binarization_confidence") val binarizationConfidence: Float?,
    @SerializedName("line_reconstruction_confidence") val lineReconstructionConfidence: Float?,
    @SerializedName("ocr_confidence") val ocrConfidence: Float?,
    @SerializedName("translation_lexical_confidence") val translationLexicalConfidence: Float?
)

data class DimensionsDto(
    @SerializedName("width") val width: Int?,
    @SerializedName("height") val height: Int?
)

data class BinarizationMetricsDto(
    @SerializedName("foreground_ratio") val foregroundRatio: Float?,
    @SerializedName("total_connected_components") val totalConnectedComponents: Int?,
    @SerializedName("valid_character_candidates") val validCharacterCandidates: Int?,
    @SerializedName("median_component_area") val medianComponentArea: Float?,
    @SerializedName("threshold_applied") val thresholdApplied: Float?
)

data class SegmentationSummaryDto(
    @SerializedName("total_lines_reconstructed") val totalLinesReconstructed: Int?,
    @SerializedName("valid_characters_detected") val validCharactersDetected: Int?
)

data class LineDto(
    @SerializedName("line_index") val lineIndex: Int,
    @SerializedName("bbox") val bbox: List<Int>?,
    @SerializedName("transcription") val transcription: String?,
    @SerializedName("crop_path") val cropPath: String?
)
