package com.shilora.app.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoStories
import androidx.compose.material.icons.filled.Collections
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.School
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(val route: String) {
    data object Splash : Screen("splash")
    data object Onboarding : Screen("onboarding")

    // Authentication Flow
    data object WelcomeAuth : Screen("auth_welcome")
    data object Login : Screen("auth_login")
    data object SignUp : Screen("auth_signup")
    data object ForgotPassword : Screen("auth_forgot_password")

    // Bottom Navigation Destinations
    data object Home : Screen("home")
    data object Explore : Screen("explore")
    data object Learn : Screen("learn")
    data object MyScans : Screen("my_scans")

    // Centralized Scanner Flow (Home -> Scanner -> Confirm -> Analysis -> Result)
    data object Scanner : Screen("scanner")
    data object ImageConfirmation : Screen("image_confirmation/{imageUri}") {
        fun createRoute(imageUri: String): String = "image_confirmation/$imageUri"
    }
    data object AnalysisProgress : Screen("analysis_progress/{imageUri}") {
        fun createRoute(imageUri: String): String = "analysis_progress/$imageUri"
    }
    data object InscriptionResult : Screen("inscription_result/{scanId}") {
        fun createRoute(scanId: String): String = "inscription_result/$scanId"
    }

    // Detail & Sub-screens
    data object ScanDetail : Screen("scan_detail/{scanId}") {
        fun createRoute(scanId: String): String = "scan_detail/$scanId"
    }
    data object ExploreDetail : Screen("explore_detail/{heritageId}") {
        fun createRoute(heritageId: String): String = "explore_detail/$heritageId"
    }
    data object LessonDetail : Screen("lesson_detail/{lessonId}") {
        fun createRoute(lessonId: String): String = "lesson_detail/$lessonId"
    }
    data object Quiz : Screen("quiz")
    data object ResearchNotes : Screen("research_notes/{scanId}") {
        fun createRoute(scanId: String): String = "research_notes/$scanId"
    }

    // Dedicated Full-Screen AI Assistant
    data object AiAssistant : Screen("ai_assistant?scanId={scanId}") {
        fun createRoute(scanId: String? = null): String =
            if (scanId != null) "ai_assistant?scanId=$scanId" else "ai_assistant"
    }

    // Settings & About
    data object Settings : Screen("settings")
    data object About : Screen("about")

    // Future-Ready Architectural Stubs
    data object FieldMode : Screen("field_mode")
    data object CompareInscriptions : Screen("compare_inscriptions")
    data object HeritageContribution : Screen("heritage_contribution")
}

// 4 Bottom Navigation Items Only (Strictly No Camera or Assistant tabs)
sealed class BottomNavItem(
    val route: String,
    val title: String,
    val icon: ImageVector
) {
    data object Home : BottomNavItem(Screen.Home.route, "Home", Icons.Default.Home)
    data object Explore : BottomNavItem(Screen.Explore.route, "Explore", Icons.Default.AutoStories)
    data object Learn : BottomNavItem(Screen.Learn.route, "Learn", Icons.Default.School)
    data object MyScans : BottomNavItem(Screen.MyScans.route, "My Scans", Icons.Default.Collections)
}
