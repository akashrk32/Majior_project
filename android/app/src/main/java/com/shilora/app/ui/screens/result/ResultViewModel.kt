package com.shilora.app.ui.screens.result

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shilora.app.data.repository.ScanRepository
import com.shilora.app.domain.model.ScanResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed class ResultUiState {
    data object Loading : ResultUiState()
    data class Success(val scanResult: ScanResult) : ResultUiState()
    data class Error(val message: String) : ResultUiState()
}

class ResultViewModel(
    private val scanRepository: ScanRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ResultUiState>(ResultUiState.Loading)
    val uiState: StateFlow<ResultUiState> = _uiState.asStateFlow()

    fun loadScanResult(scanId: String) {
        viewModelScope.launch {
            _uiState.value = ResultUiState.Loading
            val result = scanRepository.getScanById(scanId)
            if (result != null) {
                _uiState.value = ResultUiState.Success(result)
            } else {
                _uiState.value = ResultUiState.Error("Inscription scan not found in local records.")
            }
        }
    }
}
