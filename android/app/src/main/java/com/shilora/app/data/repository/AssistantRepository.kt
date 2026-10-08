package com.shilora.app.data.repository

import com.shilora.app.domain.model.ChatMessage
import com.shilora.app.domain.model.ChatSender
import com.shilora.app.domain.model.ScanResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID

class AssistantRepository {

    private val _messages = MutableStateFlow<List<ChatMessage>>(
        listOf(
            ChatMessage(
                id = UUID.randomUUID().toString(),
                sender = ChatSender.ASSISTANT,
                text = "Namaskara! I am SHILORA AI, your epigraphy and heritage assistant. Ask me about historical Kannada stone inscriptions, ancient vocabulary, scripts, or ask questions about your scans."
            )
        )
    )
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

    suspend fun sendMessage(userText: String, activeScanContext: ScanResult? = null) {
        val userMsg = ChatMessage(
            id = UUID.randomUUID().toString(),
            sender = ChatSender.USER,
            text = userText,
            relatedScanId = activeScanContext?.id
        )
        _messages.value = _messages.value + userMsg

        // Generate domain-grounded assistant response
        val assistantReply = generateDomainResponse(userText, activeScanContext)
        val assistantMsg = ChatMessage(
            id = UUID.randomUUID().toString(),
            sender = ChatSender.ASSISTANT,
            text = assistantReply,
            relatedScanId = activeScanContext?.id
        )
        _messages.value = _messages.value + assistantMsg
    }

    private fun generateDomainResponse(query: String, context: ScanResult?): String {
        val lower = query.lowercase()

        // 1. Scan-specific contextual inquiries
        if (context != null) {
            if (lower.contains("this inscription") || lower.contains("summary") || lower.contains("mean") || lower.contains("about")) {
                return "Based on the verified analysis of this scan:\n\n" +
                        "• Summary: ${context.inscriptionSummary}\n" +
                        "• Lines Detected: ${context.lines.size}\n" +
                        "• Confidence: ${context.confidenceLevel.label}\n\n" +
                        if (context.modernKannada.isNotBlank()) "Modern Kannada: ${context.modernKannada.take(160)}..." else "Historical transcription requires closer palaeographic verification."
            }
            if (lower.contains("uncertain") || lower.contains("confidence") || lower.contains("reliable")) {
                return "The OCR confidence for this scan is evaluated at ${context.confidenceLevel.label} (${(context.confidenceScore * 100).toInt()}%). " +
                        if (context.uncertainTokens.isNotEmpty()) "Uncertain character tokens identified: ${context.uncertainTokens.take(5).joinToString(", ")}." else "Character stroke continuity across lines was verified."
            }
        }

        // 2. Epigraphical domain knowledge
        return when {
            lower.contains("halegannada") || lower.contains("old kannada") -> {
                "Halegannada (Old Kannada) is the classical stage of the Kannada language spanning roughly from 450 CE (Halmidi inscription) to the end of the 12th century. It features distinct phonemes like ಱ (ṟa) and ೞ (ḻa), intricate grammatical declensions, and archaic verb conjugations."
            }
            lower.contains("hero stone") || lower.contains("viragallu") || lower.contains("veergallu") -> {
                "A Vīragallu (Hero Stone) is a memorial stele raised across Karnataka to honor warriors who fell defending their village, cattle raids (Turugol), or in royal wars. They typically have 3 sculpted tiers: earthly battle, heavenly ascent with apsaras, and eternal communion with the deity."
            }
            lower.contains("halmidi") -> {
                "The Halmidi inscription (c. 450 CE) from Hassan district is the earliest attested Kannada stone inscription. Written in 16 lines of poetic Old Kannada under Kadamba king Kakusthavarma, it confirms that Kannada was already a sophisticated literary medium in the 5th century."
            }
            lower.contains("matra") || lower.contains("conjunct") -> {
                "In Kannada epigraphy, a 'matra' is an attached vowel sign modifying a consonant (e.g. ಿ, ು, ೇ), while a 'conjunct' (Vattakshara) represents stacked consonant clusters. In early inscriptions, vowel signs were engraved as circular loops or angular extensions atop the character."
            }
            else -> {
                "In historical Kannada epigraphy, inscriptions serve as permanent legal, social, and literary records. You can ask me to explain specific terms (like Dāna, Prasasti, Vīragallu, Mangala), discuss dynasties (Kadamba, Chalukya, Ganga, Rashtrakuta, Hoysala), or interpret any scan from your library."
            }
        }
    }

    fun clearMessages() {
        _messages.value = listOf(
            ChatMessage(
                id = UUID.randomUUID().toString(),
                sender = ChatSender.ASSISTANT,
                text = "Chat cleared. Ask me anything about Kannada stone inscriptions and heritage."
            )
        )
    }
}
