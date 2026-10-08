package com.shilora.app.ui.screens.analysis

import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shilora.app.data.repository.ScanRepository
import com.shilora.app.domain.model.ScanResult
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed class AnalysisUiState {
    data class Progress(val stageIndex: Int, val stageName: String) : AnalysisUiState()
    data class Success(val scanResult: ScanResult) : AnalysisUiState()
    data class Error(val message: String) : AnalysisUiState()
}

class AnalysisViewModel(
    private val scanRepository: ScanRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<AnalysisUiState>(
        AnalysisUiState.Progress(0, STAGES[0])
    )
    val uiState: StateFlow<AnalysisUiState> = _uiState.asStateFlow()

    fun startAnalysis(context: Context, imageUri: Uri) {
        viewModelScope.launch {
            _uiState.value = AnalysisUiState.Progress(0, STAGES[0])

            // Launch progress stage simulator concurrently while the real backend API call executes
            val progressJob = launch {
                for (index in STAGES.indices) {
                    _uiState.value = AnalysisUiState.Progress(index, STAGES[index])
                    delay(1200)
                }
            }

            val result = scanRepository.analyzeImage(context, imageUri)
            progressJob.cancel()

            result.fold(
                onSuccess = { scanResult ->
                    _uiState.value = AnalysisUiState.Success(scanResult)
                },
                onFailure = { error ->
                    val userMessage = when {
                        error.message?.contains("Unable to resolve host", ignoreCase = true) == true ||
                        error.message?.contains("Failed to connect", ignoreCase = true) == true ->
                            "Could not connect to the SHILORA epigraphy engine. Please verify network connectivity."
                        error.message?.contains("timeout", ignoreCase = true) == true ->
                            "Analysis request timed out. Processing deep inscription images can take up to a minute."
                        else ->
                            error.message ?: "SHILORA could not read enough of this inscription reliably."
                    }
                    _uiState.value = AnalysisUiState.Error(userMessage)
                }
            )
        }
    }

    companion object {
        val STAGES = listOf(
            "Preparing inscription image",
            "Reading inscription structure",
            "Detecting inscription lines",
            "Transcribing Old Kannada",
            "Building translation",
            "Preparing historical explanation"
        )
    }
}
