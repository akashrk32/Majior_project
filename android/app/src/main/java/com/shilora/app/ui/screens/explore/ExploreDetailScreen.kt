package com.shilora.app.ui.screens.explore

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Place
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.shilora.app.di.ServiceLocator
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ResultSection
import com.shilora.app.ui.components.ShiloraCard

@Composable
fun ExploreDetailScreen(
    heritageId: String,
    onBackClick: () -> Unit
) {
    val heritageRepository = remember { ServiceLocator.heritageRepository }
    val item = remember(heritageId) { heritageRepository.getInscriptionById(heritageId) }

    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = "Historical Inscription",
                onBackClick = onBackClick
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        if (item == null) {
            Box(Modifier.fillMaxSize().padding(innerPadding), contentAlignment = Alignment.Center) {
                Text("Inscription record not found.", color = NeutralDarkGrey)
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(top = 12.dp, bottom = 48.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Image and Main Metadata
                item {
                    ShiloraCard {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(220.dp)
                                .clip(RoundedCornerShape(12.dp))
                                .background(ConcreteGreyLight)
                        ) {
                            AsyncImage(
                                model = ImageRequest.Builder(LocalContext.current)
                                    .data(item.imageUrl)
                                    .crossfade(true)
                                    .build(),
                                contentDescription = item.title,
                                contentScale = ContentScale.Crop,
                                modifier = Modifier.fillMaxSize()
                            )
                        }

                        Spacer(Modifier.height(14.dp))

                        Text(
                            text = item.title,
                            style = MaterialTheme.typography.headlineSmall.copy(
                                fontWeight = FontWeight.Bold,
                                color = NeutralBlack
                            )
                        )

                        Spacer(Modifier.height(4.dp))

                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Place,
                                contentDescription = null,
                                tint = BurntAmber,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = "${item.siteLocation} • ${item.century}",
                                style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey)
                            )
                        }

                        Spacer(Modifier.height(8.dp))

                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = ConcreteGreyLight.copy(alpha = 0.5f)
                        ) {
                            Text(
                                text = "Dynasty: ${item.dynasty} | Type: ${item.inscriptionType}",
                                style = MaterialTheme.typography.labelMedium.copy(
                                    color = NeutralBlack,
                                    fontWeight = FontWeight.Medium
                                ),
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                            )
                        }
                    }
                }

                // Historical Summary
                item {
                    ResultSection(title = "Historical Summary") {
                        Text(
                            text = item.summary,
                            style = MaterialTheme.typography.bodyLarge.copy(
                                color = NeutralBlack,
                                lineHeight = 24.sp
                            )
                        )
                    }
                }

                // Transcription Preview
                item {
                    ResultSection(
                        title = "Old Kannada Text (Halegannada)",
                        badgeText = "Epigraphical"
                    ) {
                        Text(
                            text = item.transcriptionPreview,
                            style = MaterialTheme.typography.bodyLarge.copy(
                                color = NeutralBlack,
                                lineHeight = 24.sp
                            )
                        )
                    }
                }

                // Scholarly Translation
                item {
                    ResultSection(
                        title = "English Translation",
                        badgeText = "Scholarly Record"
                    ) {
                        Text(
                            text = item.englishTranslation,
                            style = MaterialTheme.typography.bodyLarge.copy(
                                color = NeutralBlack,
                                lineHeight = 24.sp
                            )
                        )
                    }
                }

                // Epigraphical Significance
                item {
                    ResultSection(
                        title = "Epigraphical & Linguistic Significance"
                    ) {
                        Text(
                            text = item.epigraphicalSignificance,
                            style = MaterialTheme.typography.bodyMedium.copy(
                                color = NeutralDarkGrey,
                                lineHeight = 22.sp
                            )
                        )
                    }
                }
            }
        }
    }
}
