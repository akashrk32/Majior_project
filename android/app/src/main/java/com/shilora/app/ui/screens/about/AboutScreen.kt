package com.shilora.app.ui.screens.about

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.HistoryEdu
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraCard

@Composable
fun AboutScreen(
    onBackClick: () -> Unit
) {
    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = "About SHILORA",
                onBackClick = onBackClick
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp),
            contentPadding = PaddingValues(top = 16.dp, bottom = 48.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            item {
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                        .background(StoneCardSurface)
                        .border(2.dp, StoneBorder, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.HistoryEdu,
                        contentDescription = null,
                        tint = BurntAmber,
                        modifier = Modifier.size(42.dp)
                    )
                }

                Spacer(Modifier.height(14.dp))

                Text(
                    text = "SHILORA",
                    style = MaterialTheme.typography.headlineMedium.copy(
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.Bold,
                        color = NeutralBlack,
                        letterSpacing = 2.sp
                    )
                )

                Text(
                    text = "Shila-Lekha Optical Recognition & Analysis",
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = NeutralDarkGrey,
                        fontWeight = FontWeight.Medium
                    )
                )

                Text(
                    text = "Version 1.0.0-PROD (Native Compose)",
                    style = MaterialTheme.typography.labelSmall.copy(color = NeutralMediumGrey)
                )
            }

            item {
                ShiloraCard {
                    Text(
                        text = "MISSION & PHILOSOPHY",
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Bold,
                            color = BurntAmberDark,
                            letterSpacing = 1.sp
                        )
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        text = "SHILORA bridges cutting-edge computer vision and Indian epigraphy. Designed to empower historians, students, and heritage enthusiasts to capture, transcribe, and understand Kannada stone inscriptions directly from the field.",
                        style = MaterialTheme.typography.bodyLarge.copy(color = NeutralBlack, lineHeight = 24.sp)
                    )
                }
            }

            item {
                ShiloraCard {
                    Text(
                        text = "SCHOLARLY TRUST MANIFESTO",
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Bold,
                            color = BurntAmberDark,
                            letterSpacing = 1.sp
                        )
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        text = "1. Zero Artificial Hallucinations: No fabricated translations or speculative dates.\n" +
                               "2. Transparent Confidence: Every scan visibly rates epigraphical uncertainty.\n" +
                               "3. Direct Pixel Analysis: Models evaluate physical carved relief strokes.\n" +
                               "4. Preserving Heritage: Dedicated to safeguarding Karnataka's epigraphical wealth.",
                        style = MaterialTheme.typography.bodyMedium.copy(color = NeutralBlack, lineHeight = 22.sp)
                    )
                }
            }
        }
    }
}
