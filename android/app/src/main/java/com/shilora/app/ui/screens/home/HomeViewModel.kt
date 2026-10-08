package com.shilora.app.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shilora.app.data.repository.HeritageRepository
import com.shilora.app.data.repository.LearningRepository
import com.shilora.app.data.repository.ScanRepository
import com.shilora.app.domain.model.HeritageItem
import com.shilora.app.domain.model.Lesson
import com.shilora.app.domain.model.ScanResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

import kotlinx.coroutines.flow.combine

data class HomeUiState(
    val recentScans: List<ScanResult> = emptyList(),
    val featuredHeritage: List<HeritageItem> = emptyList(),
    val quickLessons: List<Lesson> = emptyList(),
    val isLoading: Boolean = false
)

class HomeViewModel(
    private val scanRepository: ScanRepository,
    private val heritageRepository: HeritageRepository,
    private val learningRepository: LearningRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState(isLoading = true))
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadHomeData()
    }

    private fun loadHomeData() {
        viewModelScope.launch {
            combine(
                scanRepository.getSavedScans(),
                heritageRepository.getCuratedInscriptions(),
                learningRepository.getLessons()
            ) { scans, heritage, lessons ->
                HomeUiState(
                    recentScans = scans.take(3),
                    featuredHeritage = heritage.take(2),
                    quickLessons = lessons.take(2),
                    isLoading = false
                )
            }.collect { state ->
                _uiState.value = state
            }
        }
    }
}
