package com.shilora.app.ui.screens.assistant

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shilora.app.data.repository.AssistantRepository
import com.shilora.app.data.repository.ScanRepository
import com.shilora.app.domain.model.ChatMessage
import com.shilora.app.domain.model.ScanResult
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class AiAssistantViewModel(
    private val assistantRepository: AssistantRepository,
    private val scanRepository: ScanRepository
) : ViewModel() {

    val messages: StateFlow<List<ChatMessage>> = assistantRepository.messages

    private var activeScan: ScanResult? = null

    fun loadScanContext(scanId: String?) {
        if (scanId == null) return
        viewModelScope.launch {
            activeScan = scanRepository.getScanById(scanId)
        }
    }

    fun sendMessage(query: String) {
        if (query.isBlank()) return
        viewModelScope.launch {
            assistantRepository.sendMessage(query, activeScan)
        }
    }

    fun getActiveScan(): ScanResult? = activeScan
}
