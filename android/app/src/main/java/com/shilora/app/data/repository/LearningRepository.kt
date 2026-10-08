package com.shilora.app.data.repository

import com.shilora.app.domain.model.ArchaicCharacter
import com.shilora.app.domain.model.Lesson
import com.shilora.app.domain.model.LessonSection
import com.shilora.app.domain.model.QuizQuestion
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf

class LearningRepository {

    private val lessons = listOf(
        Lesson(
            id = "lesson_archaic_letters",
            title = "Lost Characters: Archaic ಱ (ṟa) & ೞ (ḻa)",
            category = "Old Kannada Basics",
            estimatedMinutes = 6,
            summary = "Understand the two extinct Kannada phonemes that appear in almost all pre-13th century stone inscriptions.",
            contentSections = listOf(
                LessonSection(
                    heading = "The Extinct Retroflex Lateral ೞ (ḻa)",
                    body = "Known as 'Kula' or retroflex frictionless liquid, this sound corresponds phonetically to the Tamil 'ழ' (ḻ). In medieval Kannada, it merged entirely into 'ಳ' (ḷa) or 'ರ' (ra). When reading stones, spotting ೞ is a decisive chronological indicator of an inscription preceding the late 12th century.",
                    archaicCharacters = listOf(
                        ArchaicCharacter("ೞ", "ಳ / ರ", "ḻa", "Archaic retroflex central approximant. Found in words like 'ಏೞು' (seven) -> modern 'ಏಳು'.")
                    )
                ),
                LessonSection(
                    heading = "The Trilled Alveolar ಱ (ṟa)",
                    body = "Known as 'Sakatarepha', representing a hard trilled alveolar tap/trill distinct from common 'ರ' (ra). In modern Kannada, words with ಱ have merged into ordinary 'ರ'. On stones, it has a distinct horizontal crossbar through the loop.",
                    archaicCharacters = listOf(
                        ArchaicCharacter("ಱ", "ರ", "ṟa", "Hard trilled alveolar consonant. Found in words like 'ಅಱಿವ' (knowledge) -> modern 'ಅರಿವ'.")
                    )
                )
            )
        ),
        Lesson(
            id = "lesson_anatomy_inscription",
            title = "Anatomy of an Inscription: The 4 Sections",
            category = "Epigraphy Basics",
            estimatedMinutes = 8,
            summary = "Learn the standard 4-part formula that Indian scribes followed for over a millennium when carving royal charters.",
            contentSections = listOf(
                LessonSection(
                    heading = "1. The Mangala (Auspicious Invocation)",
                    body = "Every inscription begins with an invocation to the deity, e.g., 'ಸ್ವಸ್ತಿ' (Hail!), 'ಶ್ರೀ' (Fortune), or 'ನಮಸ್ತುಂಗ ಶಿರಶ್ಚುಂಬಿ ಚಂದ್ರಚಾಮರ ಚಾರವೇ' (Praise to Shiva)."
                ),
                LessonSection(
                    heading = "2. The Prasasti (Royal Eulogy & Genealogy)",
                    body = "Details the reigning king, dynasty, military campaigns, titles, and lineage to establish authority and establish the chronological Saka or regnal year."
                ),
                LessonSection(
                    heading = "3. The Dāna (The Grant or Memorial Purpose)",
                    body = "The core legal contract: description of the land boundaries (Chathusseema), tax exemptions (Sarvamanya), witnesses, and the beneficiary."
                ),
                LessonSection(
                    heading = "4. The Sāpa (Imprecatory Curse Formula)",
                    body = "Warning to future rulers against violating the grant: 'He who destroys this gift commits the sin of slaughtering a thousand tawny cows on the banks of the Ganges.'"
                )
            )
        ),
        Lesson(
            id = "lesson_hero_stones",
            title = "Reading Hero Stones (Vīragallu)",
            category = "Archaeological Types",
            estimatedMinutes = 5,
            summary = "How to interpret the 3 visual sculptural tiers of a memorial stone alongside its engraved text.",
            contentSections = listOf(
                LessonSection(
                    heading = "The Three Sculptural Panels",
                    body = "Lower tier: The mortal battle where the hero defends cattle (Turugol) or his village. Middle tier: Heavenly apsaras escorting the hero upwards. Top tier: The hero seated in the presence of Shiva Linga or the deity, achieving immortality."
                )
            )
        )
    )

    private val quizQuestions = listOf(
        QuizQuestion(
            id = "q1",
            questionText = "Which archaic Kannada letter merged into modern 'ಳ' (ḷa) or 'ರ' (ra) after the 12th century?",
            characterPrompt = "ೞ",
            options = listOf("ಱ (ṟa)", "ೞ (ḻa)", "ಙ (ṅa)", "ಞ (ña)"),
            correctIndex = 1,
            explanation = "ೞ (ḻa) is the ancient retroflex lateral approximant that gradually disappeared from Kannada speech and was replaced by ಳ or ರ."
        ),
        QuizQuestion(
            id = "q2",
            questionText = "What is the standard term for the opening invocation of an ancient stone inscription?",
            options = listOf("Prasasti", "Sāpa", "Mangala", "Dāna"),
            correctIndex = 2,
            explanation = "The 'Mangala' is the auspicious opening invoking deities such as Shiva, Vishnu, or the Tirthankaras."
        ),
        QuizQuestion(
            id = "q3",
            questionText = "A memorial stone erected in honor of a fallen warrior defending his village or cattle is known as:",
            options = listOf("Nisidhi", "Vīragallu (Hero Stone)", "Tamrashasana", "Silastambha"),
            correctIndex = 1,
            explanation = "A Vīragallu (Hero Stone) commemorates a warrior's supreme sacrifice during battle or cattle raids."
        )
    )

    fun getLessons(): Flow<List<Lesson>> = flowOf(lessons)

    fun getLessonById(id: String): Lesson? = lessons.find { it.id == id }

    fun getQuizQuestions(): List<QuizQuestion> = quizQuestions
}
