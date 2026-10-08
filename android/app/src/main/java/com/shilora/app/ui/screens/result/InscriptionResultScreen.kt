package com.shilora.app.ui.screens.result

import android.net.Uri
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.shilora.app.di.ServiceLocator
import com.shilora.app.domain.model.ConfidenceLevel
import com.shilora.app.domain.model.ScanResult
import com.shilora.app.theme.*
import com.shilora.app.ui.components.*
import java.text.SimpleDateFormat
import java.util.Locale

@Composable
fun InscriptionResultScreen(
    scanId: String,
    onBackClick: () -> Unit,
    onAskAiClick: (String) -> Unit,
    onResearchNotesClick: (String) -> Unit
) {
    val context = LocalContext.current
    val viewModel = remember {
        ResultViewModel(ServiceLocator.getScanRepository(context))
    }
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(scanId) {
        viewModel.loadScanResult(scanId)
    }

    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = "Analysis Result",
                onBackClick = onBackClick
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            when (val state = uiState) {
                is ResultUiState.Loading -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = BurntAmber)
                    }
                }
                is ResultUiState.Error -> {
                    ErrorState(
                        title = "Unable to Load Result",
                        errorMessage = state.message,
                        onRetryClick = { viewModel.loadScanResult(scanId) }
                    )
                }
                is ResultUiState.Success -> {
                    ResultDetailsContent(
                        scanResult = state.scanResult,
                        onAskAiClick = { onAskAiClick(state.scanResult.id) },
                        onResearchNotesClick = { onResearchNotesClick(state.scanResult.id) },
                        onBackClick = onBackClick
                    )
                }
            }
        }
    }
}

@Composable
private fun ResultDetailsContent(
    scanResult: ScanResult,
    onAskAiClick: () -> Unit,
    onResearchNotesClick: () -> Unit,
    onBackClick: () -> Unit
) {
    var isDetailsExpanded by remember { mutableStateOf(false) }
    val dateFormat = remember { SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault()) }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 40.dp)
    ) {
        // 1. Inscription Image Preview & Trust Header
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = StoneCardSurface),
                border = androidx.compose.foundation.BorderStroke(1.dp, StoneBorder)
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(ConcreteGreyLight)
                    ) {
                        AsyncImage(
                            model = ImageRequest.Builder(LocalContext.current)
                                .data(scanResult.localImagePath)
                                .crossfade(true)
                                .build(),
                            contentDescription = "Analyzed Inscription Stone",
                            contentScale = ContentScale.Crop,
                            modifier = Modifier.fillMaxSize()
                        )
                    }

                    Spacer(Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "KANNADA INSCRIPTION DETECTED",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = NeutralMediumGrey,
                                    letterSpacing = 1.sp
                                )
                            )
                            Text(
                                text = dateFormat.format(scanResult.scannedAt),
                                style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey)
                            )
                        }

                        ConfidenceBadge(level = scanResult.confidenceLevel)
                    }
                }
            }
        }

        // 2. OLD KANNADA TRANSCRIPTION (Line-by-Line) - "What does the inscription say?"
        item {
            ResultSection(
                title = "Old Kannada Transcription",
                badgeText = "${scanResult.lines.size} lines"
            ) {
                if (scanResult.lines.isNotEmpty()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        scanResult.lines.forEach { line ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(ConcreteGreyLight.copy(alpha = 0.4f))
                                    .padding(horizontal = 12.dp, vertical = 8.dp),
                                verticalAlignment = Alignment.Top
                            ) {
                                Text(
                                    text = "L${line.lineIndex}:",
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        color = BurntAmberDark,
                                        fontWeight = FontWeight.Bold
                                    ),
                                    modifier = Modifier.width(32.dp)
                                )
                                Text(
                                    text = line.transcription,
                                    style = MaterialTheme.typography.bodyMedium.copy(
                                        fontWeight = FontWeight.Medium,
                                        color = NeutralBlack
                                    )
                                )
                            }
                        }
                    }
                } else {
                    Text(
                        text = scanResult.normalizedOldKannada.ifBlank {
                            "No inscription lines could be isolated clearly."
                        },
                        style = MaterialTheme.typography.bodyMedium.copy(color = NeutralBlack)
                    )
                }
            }
        }

        // 3. MODERN KANNADA TRANSLATION - "What does it mean in modern Kannada?"
        item {
            ResultSection(
                title = "Modern Kannada (ಆಧುನಿಕ ಕನ್ನಡ)",
                badgeText = "ಅನುವಾದ"
            ) {
                Text(
                    text = scanResult.modernKannada.ifBlank {
                        "ಆಧುನಿಕ ಕನ್ನಡ ಅನುವಾದ ಲಭ್ಯವಿಲ್ಲ."
                    },
                    style = MaterialTheme.typography.bodyLarge.copy(
                        color = NeutralBlack,
                        lineHeight = 24.sp
                    )
                )
            }
        }

        // 4. ENGLISH TRANSLATION - "What does it mean in English?"
        item {
            ResultSection(
                title = "English Translation",
                badgeText = "Scholarly"
            ) {
                Text(
                    text = scanResult.englishTranslation.ifBlank {
                        "Translation could not be determined with sufficient epigraphical confidence."
                    },
                    style = MaterialTheme.typography.bodyLarge.copy(
                        color = NeutralBlack,
                        lineHeight = 24.sp
                    )
                )
            }
        }

        // 5. WHAT THIS STONE CONTAINS - "What does the inscription contain?"
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = StoneCardSurface),
                border = androidx.compose.foundation.BorderStroke(1.5.dp, SageGreenDark.copy(alpha = 0.5f))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.MenuBook,
                            contentDescription = null,
                            tint = BurntAmber,
                            modifier = Modifier.size(20.dp)
                        )
                        Text(
                            text = "WHAT THIS STONE CONTAINS",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = NeutralBlack
                            )
                        )
                    }

                    Spacer(Modifier.height(10.dp))

                    Text(
                        text = scanResult.inscriptionSummary.ifBlank {
                            "Insufficient evidence for a reliable historical summary."
                        },
                        style = MaterialTheme.typography.bodyLarge.copy(
                            color = NeutralBlack,
                            lineHeight = 24.sp
                        )
                    )
                }
            }
        }

        // 6. EVIDENCE & CONFIDENCE (Trust Model)
        item {
            ResultSection(
                title = "Evidence & Epigraphical Trust",
                badgeText = "Verification"
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "OCR Confidence Rating:",
                            style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey)
                        )
                        Text(
                            text = "${(scanResult.confidenceScore * 100).toInt()}%",
                            style = MaterialTheme.typography.bodyMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = NeutralBlack
                            )
                        )
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Interpretation Status:",
                            style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey)
                        )
                        Text(
                            text = scanResult.status.uppercase(),
                            style = MaterialTheme.typography.bodyMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = SageGreenDark
                            )
                        )
                    }

                    if (scanResult.uncertainTokens.isNotEmpty()) {
                        Spacer(Modifier.height(4.dp))
                        Text(
                            text = "Uncertain / Weathered Glyphs:",
                            style = MaterialTheme.typography.bodySmall.copy(
                                fontWeight = FontWeight.SemiBold,
                                color = BurntAmberDark
                            )
                        )
                        Text(
                            text = scanResult.uncertainTokens.joinToString(", "),
                            style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey)
                        )
                    }
                }
            }
        }

        // 7. PROCESSING DETAILS (Technical breakdown, collapsible)
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = StoneCardSurface),
                border = androidx.compose.foundation.BorderStroke(1.dp, StoneBorder)
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { isDetailsExpanded = !isDetailsExpanded },
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Technical Processing Metrics",
                            style = MaterialTheme.typography.titleSmall.copy(
                                fontWeight = FontWeight.SemiBold,
                                color = NeutralDarkGrey
                            )
                        )
                        Icon(
                            imageVector = if (isDetailsExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                            contentDescription = null,
                            tint = NeutralDarkGrey
                        )
                    }

                    AnimatedVisibility(visible = isDetailsExpanded) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 12.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            val stats = scanResult.binarizationStats
                            if (stats != null) {
                                Text("Binarization Pipeline: Direct Preprocessed Attention U-Net", style = MaterialTheme.typography.bodySmall)
                                Text("Foreground Ratio: ${(stats.foregroundRatio * 100).toInt()}%", style = MaterialTheme.typography.bodySmall)
                                Text("Connected Glyph Components: ${stats.totalConnectedComponents}", style = MaterialTheme.typography.bodySmall)
                                Text("Valid Character Candidates: ${stats.validCharacterCandidates}", style = MaterialTheme.typography.bodySmall)
                                Text("Adaptive Stroke Threshold: ${stats.thresholdApplied}", style = MaterialTheme.typography.bodySmall)
                            } else {
                                Text("Direct model metrics logged to orchestrator ledger.", style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                }
            }
        }

        // 8. Action Buttons
        item {
            Spacer(Modifier.height(8.dp))
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                ShiloraButton(
                    text = "Ask SHILORA AI About This Stone",
                    icon = Icons.Default.Chat,
                    variant = ShiloraButtonVariant.PRIMARY,
                    onClick = onAskAiClick
                )

                ShiloraButton(
                    text = "Attach Research Notes",
                    icon = Icons.Default.EditNote,
                    variant = ShiloraButtonVariant.SECONDARY,
                    onClick = onResearchNotesClick
                )

                ShiloraButton(
                    text = "Back to Home",
                    icon = Icons.Default.Home,
                    variant = ShiloraButtonVariant.SECONDARY,
                    onClick = onBackClick
                )
            }
        }
    }
}
