package com.shilora.app.domain.model

data class HeritageItem(
    val id: String,
    val title: String,
    val period: String,
    val dynasty: String,
    val century: String,
    val region: String,
    val inscriptionType: String,
    val summary: String,
    val transcriptionPreview: String,
    val englishTranslation: String,
    val imageUrl: String,
    val siteLocation: String,
    val epigraphicalSignificance: String
)

data class Lesson(
    val id: String,
    val title: String,
    val category: String,
    val estimatedMinutes: Int,
    val summary: String,
    val contentSections: List<LessonSection>
)

data class LessonSection(
    val heading: String,
    val body: String,
    val archaicCharacters: List<ArchaicCharacter>? = null
)

data class ArchaicCharacter(
    val halegannadaGlyph: String,
    val modernKannadaGlyph: String,
    val phoneticIast: String,
    val description: String
)

data class QuizQuestion(
    val id: String,
    val questionText: String,
    val characterPrompt: String? = null,
    val options: List<String>,
    val correctIndex: Int,
    val explanation: String
)

enum class ChatSender {
    USER,
    ASSISTANT
}

data class ChatMessage(
    val id: String,
    val sender: ChatSender,
    val text: String,
    val timestamp: Long = System.currentTimeMillis(),
    val relatedScanId: String? = null
)
