package com.shilora.app.data.repository

import com.shilora.app.domain.model.HeritageItem
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf

class HeritageRepository {

    private val curatedHeritageItems = listOf(
        HeritageItem(
            id = "halmidi_001",
            title = "Halmidi Inscription",
            period = "Kadamba Dynasty",
            century = "c. 450 CE",
            dynasty = "Kadamba of Banavasi",
            region = "Hassan District",
            inscriptionType = "Land Grant & Commendation",
            summary = "Widely recognized as the earliest known Kannada stone inscription. Records a tax-free grant of villages (Palmidi and Mulivalli) awarded to Vijasamaya for military valor under King Kakusthavarma.",
            transcriptionPreview = "ನಮಃ ಶ್ರೀಮತ್ ಕದಂಬ ಪನ್ ತ್ಯಾಗ ಸಂಪನ್ನನ್...",
            englishTranslation = "Salutations. The glorious Kadamba king, rich in sacrifice and virtues, grants the villages of Palmidi and Mulivalli free of taxes to Vijasamaya.",
            imageUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Halmidi_inscription.jpg/800px-Halmidi_inscription.jpg",
            siteLocation = "Halmidi Village, Belur Taluk, Hassan",
            epigraphicalSignificance = "Landmark epigraph in linguistic history, establishing formal literary Old Kannada (Halegannada) usage in the 5th century CE."
        ),
        HeritageItem(
            id = "badami_cliff_002",
            title = "Badami Cliff Inscription of Mangalesha",
            period = "Early Chalukya",
            century = "578 CE",
            dynasty = "Chalukyas of Vatapi",
            region = "Bagalkot District",
            inscriptionType = "Temple Cave Dedication",
            summary = "Carved on the northern cliff face of Badami. Documents the consecration of the Vaishnava rock-cut cave temple and royal tax concessions.",
            transcriptionPreview = "ಸ್ವಸ್ತಿ ಶ್ರೀ ವಲ್ಲಭ ಪೃಥ್ವೀ ವಲ್ಲಭ ಮಹಾರಾಜಾಧಿರಾಜ...",
            englishTranslation = "Hail! The glorious king, beloved of fortune and earth, emperor of monarchs, consecrates this shrine to Vishnu.",
            imageUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Badami_Cave_Temples_Cliff.jpg/800px-Badami_Cave_Temples_Cliff.jpg",
            siteLocation = "Badami Rock Caves, Bagalkot",
            epigraphicalSignificance = "Key chronological anchor for early South Indian rock-cut architecture and early Chalukyan epigraphy."
        ),
        HeritageItem(
            id = "atakur_003",
            title = "Atakur Hero Stone (Vīragallu)",
            period = "Western Ganga / Rashtrakuta",
            century = "949 CE",
            dynasty = "Western Ganga Dynasty",
            region = "Mandya District",
            inscriptionType = "Memorial & Canine Heroism",
            summary = "Remarkable hero stone commemorating both a fallen soldier and his hunting hound Kali, who fought valiantly during the battle of Takkolam against the Chola forces.",
            transcriptionPreview = "ಶ್ರೀಮತು ಬೂತುಗಂ ಗಂಗ ಪೆರ್ಮಾನಡಿಯುಂ...",
            englishTranslation = "The glorious Butuga, Western Ganga sovereign, honors the faithful hound Kali who fought unto death.",
            imageUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Atakur_Inscription.jpg/800px-Atakur_Inscription.jpg",
            siteLocation = "Atakur, Maddur Taluk, Mandya",
            epigraphicalSignificance = "One of the most unique animal memorial inscriptions in world archaeology, combining poetic Old Kannada with battle history."
        ),
        HeritageItem(
            id = "belur_chennakeshava_004",
            title = "Belur Chennakeshava Hoysala Charter",
            period = "Hoysala Dynasty",
            century = "1117 CE",
            dynasty = "Hoysala Empire",
            region = "Hassan District",
            inscriptionType = "Temple Endowment & Royal Prasasti",
            summary = "Stone stele detailing the victory of King Vishnuvardhana at Talakadu against the Cholas and the subsequent endowment of the Vijayanarayana (Chennakeshava) temple.",
            transcriptionPreview = "ಶ್ರೀಮನ್ ಮಹಾಮಂಡಲೇಶ್ವರನ್ ವಿಷ್ಣುವರ್ಧನ ದೇವರ್...",
            englishTranslation = "The great ruler of provinces, King Vishnuvardhana, dedicates this sacred dwelling following victory at Talakadu.",
            imageUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Belur_Temple_Inscription.jpg/800px-Belur_Temple_Inscription.jpg",
            siteLocation = "Chennakeshava Temple Complex, Belur",
            epigraphicalSignificance = "Exquisite example of ornate Hoysala epigraphical calligraphy and detailed economic records of medieval Karnataka."
        )
    )

    fun getCuratedInscriptions(): Flow<List<HeritageItem>> = flowOf(curatedHeritageItems)

    fun getInscriptionById(id: String): HeritageItem? {
        return curatedHeritageItems.find { it.id == id }
    }
}
