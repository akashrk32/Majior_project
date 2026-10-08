package com.shilora.app.ui.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.*
import androidx.navigation.navArgument
import com.shilora.app.theme.*
import com.shilora.app.ui.components.AssistantFloatingButton
import com.shilora.app.ui.screens.about.AboutScreen
import com.shilora.app.ui.screens.analysis.AnalysisProgressScreen
import com.shilora.app.ui.screens.assistant.AiAssistantScreen
import com.shilora.app.ui.screens.auth.ForgotPasswordScreen
import com.shilora.app.ui.screens.auth.LoginScreen
import com.shilora.app.ui.screens.auth.SignUpScreen
import com.shilora.app.ui.screens.auth.WelcomeAuthScreen
import com.shilora.app.ui.screens.confirmation.ImageConfirmationScreen
import com.shilora.app.ui.screens.explore.ExploreDetailScreen
import com.shilora.app.ui.screens.explore.ExploreScreen
import com.shilora.app.ui.screens.future.CompareInscriptionsScreen
import com.shilora.app.ui.screens.future.FieldModeScreen
import com.shilora.app.ui.screens.future.HeritageContributionScreen
import com.shilora.app.ui.screens.home.HomeScreen
import com.shilora.app.ui.screens.learn.LearnScreen
import com.shilora.app.ui.screens.learn.LessonDetailScreen
import com.shilora.app.ui.screens.learn.QuizScreen
import com.shilora.app.ui.screens.myscans.MyScansScreen
import com.shilora.app.ui.screens.onboarding.OnboardingScreen
import com.shilora.app.ui.screens.research.ResearchNotesScreen
import com.shilora.app.ui.screens.result.InscriptionResultScreen
import com.shilora.app.ui.screens.scanner.ScannerScreen
import com.shilora.app.ui.screens.settings.SettingsScreen
import com.shilora.app.ui.screens.splash.SplashScreen
import androidx.compose.ui.platform.LocalContext
import com.shilora.app.di.ServiceLocator
import com.shilora.app.domain.model.AuthState

@Composable
fun ShiloraAppNavigation(
    navController: NavHostController = rememberNavController()
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val context = LocalContext.current
    val authRepo = remember { ServiceLocator.getAuthRepository(context) }
    val authState by authRepo.authState.collectAsState()

    // Show bottom bar and floating assistant ONLY on the 4 main bottom nav tabs
    val bottomNavItems = listOf(
        BottomNavItem.Home,
        BottomNavItem.Explore,
        BottomNavItem.Learn,
        BottomNavItem.MyScans
    )
    val isMainTab = bottomNavItems.any { it.route == currentRoute }

    Scaffold(
        bottomBar = {
            if (isMainTab) {
                NavigationBar(
                    containerColor = SageGreenSurface,
                    contentColor = NeutralBlack,
                    tonalElevation = 6.dp
                ) {
                    bottomNavItems.forEach { item ->
                        val selected = currentRoute == item.route
                        NavigationBarItem(
                            selected = selected,
                            onClick = {
                                if (currentRoute != item.route) {
                                    navController.navigate(item.route) {
                                        popUpTo(navController.graph.findStartDestination().id) {
                                            saveState = true
                                        }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                }
                            },
                            icon = {
                                Icon(
                                    imageVector = item.icon,
                                    contentDescription = item.title,
                                    tint = if (selected) BurntAmber else NeutralDarkGrey
                                )
                            },
                            label = {
                                Text(
                                    text = item.title,
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        color = if (selected) BurntAmberDark else NeutralDarkGrey
                                    )
                                )
                            },
                            colors = NavigationBarItemDefaults.colors(
                                indicatorColor = BurntAmber.copy(alpha = 0.15f)
                            )
                        )
                    }
                }
            }
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            NavHost(
                navController = navController,
                startDestination = Screen.Splash.route,
                modifier = Modifier.fillMaxSize()
            ) {
                // 1. Splash & Onboarding & Auth
                composable(Screen.Splash.route) {
                    SplashScreen(
                        onSplashFinished = {
                            val destination = when (authState) {
                                is AuthState.Authenticated, is AuthState.Guest -> Screen.Home.route
                                is AuthState.Unauthenticated -> Screen.Onboarding.route
                                else -> Screen.Onboarding.route
                            }
                            navController.navigate(destination) {
                                popUpTo(Screen.Splash.route) { inclusive = true }
                            }
                        }
                    )
                }

                composable(Screen.Onboarding.route) {
                    OnboardingScreen(
                        onFinished = {
                            navController.navigate(Screen.WelcomeAuth.route) {
                                popUpTo(Screen.Onboarding.route) { inclusive = true }
                            }
                        }
                    )
                }

                composable(Screen.WelcomeAuth.route) {
                    WelcomeAuthScreen(
                        onLoginClick = { navController.navigate(Screen.Login.route) },
                        onSignUpClick = { navController.navigate(Screen.SignUp.route) },
                        onGuestClick = {
                            authRepo.continueAsGuest()
                            navController.navigate(Screen.Home.route) {
                                popUpTo(Screen.WelcomeAuth.route) { inclusive = true }
                            }
                        }
                    )
                }

                composable(Screen.Login.route) {
                    LoginScreen(
                        onLoginSuccess = {
                            navController.navigate(Screen.Home.route) {
                                popUpTo(Screen.WelcomeAuth.route) { inclusive = true }
                            }
                        },
                        onNavigateToSignUp = {
                            navController.navigate(Screen.SignUp.route)
                        },
                        onNavigateToForgotPassword = {
                            navController.navigate(Screen.ForgotPassword.route)
                        },
                        onContinueAsGuest = {
                            navController.navigate(Screen.Home.route) {
                                popUpTo(Screen.WelcomeAuth.route) { inclusive = true }
                            }
                        },
                        onBackClick = { navController.popBackStack() }
                    )
                }

                composable(Screen.SignUp.route) {
                    SignUpScreen(
                        onSignUpSuccess = {
                            navController.navigate(Screen.Home.route) {
                                popUpTo(Screen.WelcomeAuth.route) { inclusive = true }
                            }
                        },
                        onNavigateToLogin = {
                            navController.navigate(Screen.Login.route) {
                                popUpTo(Screen.SignUp.route) { inclusive = true }
                            }
                        },
                        onContinueAsGuest = {
                            navController.navigate(Screen.Home.route) {
                                popUpTo(Screen.WelcomeAuth.route) { inclusive = true }
                            }
                        },
                        onBackClick = { navController.popBackStack() }
                    )
                }

                composable(Screen.ForgotPassword.route) {
                    ForgotPasswordScreen(
                        onBackToLogin = {
                            navController.navigate(Screen.Login.route) {
                                popUpTo(Screen.ForgotPassword.route) { inclusive = true }
                            }
                        },
                        onBackClick = { navController.popBackStack() }
                    )
                }

                // 2. Main Tabs
                composable(Screen.Home.route) {
                    HomeScreen(
                        onScanClick = {
                            navController.navigate(Screen.Scanner.route)
                        },
                        onExploreClick = {
                            navController.navigate(Screen.Explore.route)
                        },
                        onLearnClick = {
                            navController.navigate(Screen.Learn.route)
                        },
                        onMyScansClick = {
                            navController.navigate(Screen.MyScans.route)
                        },
                        onAssistantClick = {
                            navController.navigate(Screen.AiAssistant.createRoute())
                        },
                        onSettingsClick = {
                            navController.navigate(Screen.Settings.route)
                        },
                        onScanResultClick = { scanId ->
                            navController.navigate(Screen.InscriptionResult.createRoute(scanId))
                        },
                        onExploreDetailClick = { heritageId ->
                            navController.navigate(Screen.ExploreDetail.createRoute(heritageId))
                        },
                        onLessonDetailClick = { lessonId ->
                            navController.navigate(Screen.LessonDetail.createRoute(lessonId))
                        }
                    )
                }

                composable(Screen.Explore.route) {
                    ExploreScreen(
                        onItemClick = { heritageId ->
                            navController.navigate(Screen.ExploreDetail.createRoute(heritageId))
                        }
                    )
                }

                composable(Screen.Learn.route) {
                    LearnScreen(
                        onLessonSelected = { lessonId ->
                            navController.navigate(Screen.LessonDetail.createRoute(lessonId))
                        },
                        onQuizSelected = {
                            navController.navigate(Screen.Quiz.route)
                        }
                    )
                }

                composable(Screen.MyScans.route) {
                    MyScansScreen(
                        onScanClick = { scanId ->
                            navController.navigate(Screen.InscriptionResult.createRoute(scanId))
                        }
                    )
                }

                // 3. Centralized Scanner Flow
                composable(Screen.Scanner.route) {
                    ScannerScreen(
                        onImageSelected = { encodedUri ->
                            navController.navigate(Screen.ImageConfirmation.createRoute(encodedUri))
                        },
                        onBackClick = {
                            navController.popBackStack()
                        }
                    )
                }

                composable(
                    route = Screen.ImageConfirmation.route,
                    arguments = listOf(navArgument("imageUri") { type = NavType.StringType })
                ) { backStackEntry ->
                    val imageUri = backStackEntry.arguments?.getString("imageUri") ?: ""
                    ImageConfirmationScreen(
                        encodedImageUri = imageUri,
                        onConfirmClick = { confirmedUri ->
                            navController.navigate(Screen.AnalysisProgress.createRoute(confirmedUri)) {
                                popUpTo(Screen.Scanner.route) { inclusive = true }
                            }
                        },
                        onRetakeClick = {
                            navController.popBackStack()
                        }
                    )
                }

                composable(
                    route = Screen.AnalysisProgress.route,
                    arguments = listOf(navArgument("imageUri") { type = NavType.StringType })
                ) { backStackEntry ->
                    val imageUri = backStackEntry.arguments?.getString("imageUri") ?: ""
                    AnalysisProgressScreen(
                        encodedImageUri = imageUri,
                        onAnalysisComplete = { scanId ->
                            navController.navigate(Screen.InscriptionResult.createRoute(scanId)) {
                                popUpTo(Screen.AnalysisProgress.route) { inclusive = true }
                            }
                        },
                        onRetryOrCancel = {
                            navController.popBackStack()
                        }
                    )
                }

                composable(
                    route = Screen.InscriptionResult.route,
                    arguments = listOf(navArgument("scanId") { type = NavType.StringType })
                ) { backStackEntry ->
                    val scanId = backStackEntry.arguments?.getString("scanId") ?: ""
                    InscriptionResultScreen(
                        scanId = scanId,
                        onBackClick = {
                            navController.popBackStack()
                        },
                        onAskAiClick = { sid ->
                            navController.navigate(Screen.AiAssistant.createRoute(sid))
                        },
                        onResearchNotesClick = { sid ->
                            navController.navigate(Screen.ResearchNotes.createRoute(sid))
                        }
                    )
                }

                // 4. Details and Sub-screens
                composable(
                    route = Screen.ExploreDetail.route,
                    arguments = listOf(navArgument("heritageId") { type = NavType.StringType })
                ) { backStackEntry ->
                    val heritageId = backStackEntry.arguments?.getString("heritageId") ?: ""
                    ExploreDetailScreen(
                        heritageId = heritageId,
                        onBackClick = { navController.popBackStack() }
                    )
                }

                composable(
                    route = Screen.LessonDetail.route,
                    arguments = listOf(navArgument("lessonId") { type = NavType.StringType })
                ) { backStackEntry ->
                    val lessonId = backStackEntry.arguments?.getString("lessonId") ?: ""
                    LessonDetailScreen(
                        lessonId = lessonId,
                        onBackClick = { navController.popBackStack() }
                    )
                }

                composable(Screen.Quiz.route) {
                    QuizScreen(onBackClick = { navController.popBackStack() })
                }

                composable(
                    route = Screen.ResearchNotes.route,
                    arguments = listOf(navArgument("scanId") { type = NavType.StringType })
                ) { backStackEntry ->
                    val scanId = backStackEntry.arguments?.getString("scanId") ?: ""
                    ResearchNotesScreen(
                        scanId = scanId,
                        onBackClick = { navController.popBackStack() }
                    )
                }

                // 5. Dedicated Full-Screen AI Assistant
                composable(
                    route = Screen.AiAssistant.route,
                    arguments = listOf(navArgument("scanId") {
                        type = NavType.StringType
                        nullable = true
                        defaultValue = null
                    })
                ) { backStackEntry ->
                    val scanId = backStackEntry.arguments?.getString("scanId")
                    AiAssistantScreen(
                        scanId = scanId,
                        onBackClick = { navController.popBackStack() }
                    )
                }

                // 6. Settings & About
                composable(Screen.Settings.route) {
                    SettingsScreen(
                        onBackClick = { navController.popBackStack() },
                        onAboutClick = { navController.navigate(Screen.About.route) },
                        onLogoutClick = {
                            navController.navigate(Screen.WelcomeAuth.route) {
                                popUpTo(0) { inclusive = true }
                            }
                        }
                    )
                }

                composable(Screen.About.route) {
                    AboutScreen(onBackClick = { navController.popBackStack() })
                }

                // 7. Future Stubs
                composable(Screen.FieldMode.route) {
                    FieldModeScreen(onBackClick = { navController.popBackStack() })
                }
                composable(Screen.CompareInscriptions.route) {
                    CompareInscriptionsScreen(onBackClick = { navController.popBackStack() })
                }
                composable(Screen.HeritageContribution.route) {
                    HeritageContributionScreen(onBackClick = { navController.popBackStack() })
                }
            }

            // Floating Assistant Button (Always accessible on main tabs, anchored bottom-right)
            if (isMainTab) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    contentAlignment = Alignment.BottomEnd
                ) {
                    AssistantFloatingButton(
                        onClick = {
                            navController.navigate(Screen.AiAssistant.createRoute())
                        }
                    )
                }
            }
        }
    }
}
