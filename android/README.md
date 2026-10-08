# SHILORA Native Android Application
### Shila-Lekha Optical Recognition & Analysis (ಶಿಲಾಲೇಖ ಆಪ್ಟಿಕಲ್ ರೆಕಗ್ನಿಷನ್ & ಅನಾಲಿಸಿಸ್)

A production-grade, native Android application built with **Kotlin**, **Jetpack Compose**, **Material 3**, and **CameraX** for discovering, reading, understanding, and researching historical Kannada stone inscriptions.

---

## 🏛️ Brand Color System (Strict 60 : 30 : 10 Ratio)

| Role | Color Name | Hex Code | Purpose & Distribution |
|---|---|---|---|
| **60%** | **Sage Green** | `#9CAF88` | Major surfaces, screen identity, background, headers, visual breathing space |
| **30%** | **Concrete Grey** | `#A7A7A7` | Cards, secondary surfaces, input panels, lesson containers, stone borders |
| **10%** | **Burnt Amber** | `#CC5500` | Primary CTA ("SCAN INSCRIPTION"), active indicators, selected tabs, confidence alerts |

Accessibility neutrals (`#1B1D1A` for readable text and `#FAFAF8` for high contrast text) are used strictly for typography contrast.

---

## 📐 Architecture & Package Structure

The project follows Modern Android Architecture (Unidirectional Data Flow + MVVM + Clean Architecture):

```
android/app/src/main/java/com/shilora/app/
├── ShiloraApp.kt                     # Application entry point (ServiceLocator initialization)
├── MainActivity.kt                   # Root ComponentActivity with Compose content
├── di/
│   └── ServiceLocator.kt             # Dependency injection container & singleton provider
├── domain/
│   └── model/
│       ├── ScanModels.kt             # ScanResult, InscriptionLine, ConfidenceLevel, BinarizationStats
│       └── HeritageModels.kt         # HeritageItem, Lesson, QuizQuestion, ChatMessage
├── data/
│   ├── api/
│   │   ├── ShiloraApiService.kt      # Retrofit interface (POST /api/shilora/analyze)
│   │   └── ShiloraApiModels.kt       # Request & Response DTOs
│   ├── local/
│   │   ├── ScanDao.kt                # Room DAO for offline persistent scan library
│   │   ├── ScanEntity.kt             # Room Entity
│   │   └── ShiloraDatabase.kt        # Room Database & JSON TypeConverters
│   └── repository/
│       ├── ScanRepository.kt         # Real API execution + image encoding + local Room caching
│       ├── HeritageRepository.kt     # Curated epigraphical database (Halmidi, Badami, Atakur, Belur)
│       ├── LearningRepository.kt     # Epigraphy curriculum, archaic characters (ಱ, ೞ), quiz engine
│       └── AssistantRepository.kt    # Domain-focused AI assistant with scan context injection
├── theme/
│   ├── Color.kt                      # 60:30:10 brand color tokens
│   ├── Type.kt                       # Heritage Serif headings + clean sans-serif body
│   └── Theme.kt                      # Material 3 ShiloraTheme definition
└── ui/
    ├── components/
    │   ├── ShiloraComponents.kt      # Reusable buttons, cards, confidence badges, top bars
    │   └── FloatingAssistant.kt     # Bottom-right floating assistant trigger
    ├── navigation/
    │   ├── ShiloraDestinations.kt    # Type-safe navigation routes & 4 bottom nav items
    │   └── ShiloraNavigation.kt      # Central Compose NavHost & Scaffold
    └── screens/
        ├── splash/                   # 01. Splash Screen
        ├── onboarding/               # 02. 3-step Onboarding
        ├── home/                     # 03. Product Home (Single SCAN CTA)
        ├── scanner/                  # 04. CameraX Viewfinder & Gallery Import
        ├── confirmation/             # 05. Image Confirmation (USE THIS IMAGE vs RETAKE)
        ├── analysis/                 # 06. 6-stage Epigraphical Progress Screen
        ├── result/                   # 07. Dedicated Result Screen (Summary, Old/Modern Kannada, English, Trust)
        ├── explore/                  # 08. Heritage Explorer & Detail Screens
        ├── learn/                    # 09. Epigraphy Hub, Lessons & Quiz Screen
        ├── myscans/                  # 10. Research Library Screen
        ├── research/                 # 11. Field & Research Notes Documentation
        ├── assistant/                # 12. Full-screen Domain AI Assistant
        ├── settings/                 # 13. Settings Screen
        ├── about/                    # 14. Mission & Epigraphical Ethics Screen
        └── future/                   # 15. Field Mode, Inscription Compare & Contribution Stubs
```

---

## 🔒 Strict Information Architecture & Product Rules

1. **One User Intent = One Entry Point:**
   - **Scan Flow:** `Home` → `SCAN INSCRIPTION` CTA → `Scanner` → `Confirm` → `Analyze` → `Result`
   - **Explore:** `Explore` tab → Discovery only. Never opens the camera.
   - **Learn:** `Learn` tab → Education & Quizzes. Never opens the camera.
   - **My Scans:** `My Scans` tab → Personal research library. Never opens the camera.
   - **AI Assistant:** Floating assistant button on main tabs → Full-screen dedicated assistant.
2. **Dedicated Result Screen:**
   - Inscription results are displayed on a dedicated screen, never stuffed into the Home screen.
   - First-class section: **"WHAT THIS STONE CONTAINS"** (simple human-readable summary).
   - Line-by-line Old Kannada transcription, Modern Kannada translation, and scholarly English translation.
   - Transparent trust indicators: OCR confidence rating, interpretation status, and weathered/uncertain tokens.
3. **No Hallucinations or Fake Data:**
   - Results are powered by the backend orchestrator (`POST /api/shilora/analyze`).
   - If confidence is low, the UI clearly displays "Needs Review" / "Insufficient evidence for a reliable historical summary".

---

## 🚀 Running the Project

### In Android Studio:
1. Open Android Studio.
2. Select **Open** and choose the `android/` directory (`e:\Brahmi-OCR-main\android`).
3. Allow Gradle to sync.
4. Select an Android emulator (API 30+) or a connected physical device.
5. Run the app (`Shift + F10` or click **Run ▶**).

### Backend Connection:
- When running in the Android Emulator, the app connects to the host machine backend via `http://10.0.2.2:5000/api/shilora/analyze`.
- To target a physical device or remote server, modify `backendBaseUrl` in `com.shilora.app.di.ServiceLocator`.
