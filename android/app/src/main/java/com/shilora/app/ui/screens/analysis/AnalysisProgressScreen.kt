package com.shilora.app.ui.screens.analysis

import android.net.Uri
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.HourglassTop
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.di.ServiceLocator
import com.shilora.app.theme.*
import com.shilora.app.ui.components.ErrorState
import com.shilora.app.ui.components.PrimaryTopBar
import java.net.URLDecoder
import java.nio.charset.StandardCharsets

@Composable
fun AnalysisProgressScreen(
    encodedImageUri: String,
    onAnalysisComplete: (String) -> Unit,
    onRetryOrCancel: () -> Unit
) {
    val context = LocalContext.current
    val viewModel = remember {
        AnalysisViewModel(ServiceLocator.getScanRepository(context))
    }
    val uiState by viewModel.uiState.collectAsState()

    val decodedUri = remember(encodedImageUri) {
        val uriString = try {
            URLDecoder.decode(encodedImageUri, StandardCharsets.UTF_8.toString())
        } catch (e: Exception) {
            encodedImageUri
        }
        Uri.parse(uriString)
    }

    LaunchedEffect(decodedUri) {
        viewModel.startAnalysis(context, decodedUri)
    }

    // Handle success transition
    LaunchedEffect(uiState) {
        if (uiState is AnalysisUiState.Success) {
            val scanId = (uiState as AnalysisUiState.Success).scanResult.id
            onAnalysisComplete(scanId)
        }
    }

    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = "Analyzing Stone",
                onBackClick = onRetryOrCancel
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(24.dp),
            contentAlignment = Alignment.Center
        ) {
            when (val state = uiState) {
                is AnalysisUiState.Progress -> {
                    AnalysisProgressContent(
                        currentStageIndex = state.stageIndex,
                        currentStageName = state.stageName
                    )
                }
                is AnalysisUiState.Error -> {
                    ErrorState(
                        title = "Analysis Incomplete",
                        errorMessage = state.message,
                        onRetryClick = {
                            viewModel.startAnalysis(context, decodedUri)
                        }
                    )
                }
                is AnalysisUiState.Success -> {
                    // Handled by LaunchedEffect
                    CircularProgressIndicator(color = BurntAmber)
                }
            }
        }
    }
}

@Composable
private fun AnalysisProgressContent(
    currentStageIndex: Int,
    currentStageName: String
) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(2800, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "rotation"
    )

    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Rotating Stone Icon Container
        Box(
            modifier = Modifier
                .size(100.dp)
                .clip(CircleShape)
                .background(StoneCardSurface)
                .border(2.dp, StoneBorder, CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Default.HourglassTop,
                contentDescription = null,
                tint = BurntAmber,
                modifier = Modifier
                    .size(44.dp)
                    .rotate(rotation)
            )
        }

        Spacer(Modifier.height(28.dp))

        Text(
            text = "Analyzing Inscription",
            style = MaterialTheme.typography.headlineSmall.copy(
                fontWeight = FontWeight.Bold,
                color = NeutralBlack
            )
        )

        Spacer(Modifier.height(8.dp))

        Text(
            text = "Please keep the app open while our epigraphical models process the inscription.",
            style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )

        Spacer(Modifier.height(32.dp))

        // Stage Stepper
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(18.dp),
            colors = CardDefaults.cardColors(containerColor = StoneCardSurface),
            border = androidx.compose.foundation.BorderStroke(1.dp, StoneBorder)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                AnalysisViewModel.STAGES.forEachIndexed { index, stageName ->
                    val isDone = index < currentStageIndex
                    val isCurrent = index == currentStageIndex

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(24.dp)
                                .clip(CircleShape)
                                .background(
                                    when {
                                        isDone -> SageGreenDark
                                        isCurrent -> BurntAmber
                                        else -> ConcreteGreyLight
                                    }
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            if (isDone) {
                                Icon(
                                    imageVector = Icons.Default.Check,
                                    contentDescription = null,
                                    tint = NeutralWhite,
                                    modifier = Modifier.size(14.dp)
                                )
                            } else {
                                Text(
                                    text = "${index + 1}",
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        color = if (isCurrent) NeutralWhite else NeutralMediumGrey,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 11.sp
                                    )
                                )
                            }
                        }

                        Spacer(Modifier.width(12.dp))

                        Text(
                            text = stageName,
                            style = MaterialTheme.typography.bodyMedium.copy(
                                fontWeight = if (isCurrent) FontWeight.Bold else FontWeight.Normal,
                                color = when {
                                    isDone -> SageGreenDark
                                    isCurrent -> BurntAmberDark
                                    else -> NeutralMediumGrey
                                }
                            )
                        )
                    }
                }
            }
        }
    }
}
