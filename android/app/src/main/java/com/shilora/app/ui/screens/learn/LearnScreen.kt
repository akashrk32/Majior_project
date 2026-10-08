package com.shilora.app.ui.screens.learn

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Quiz
import androidx.compose.material.icons.filled.School
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.di.ServiceLocator
import com.shilora.app.domain.model.Lesson
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraCard
import com.shilora.app.ui.components.ShiloraSectionHeader

@Composable
fun LearnScreen(
    onLessonSelected: (String) -> Unit,
    onQuizSelected: () -> Unit
) {
    val learningRepository = remember { ServiceLocator.learningRepository }
    val lessons by learningRepository.getLessons().collectAsState(initial = emptyList())

    Scaffold(
        topBar = {
            PrimaryTopBar(title = "Epigraphy Learning Hub")
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp),
            contentPadding = PaddingValues(top = 12.dp, bottom = 48.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header Hero Banner
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = StoneCardSurface),
                    border = androidx.compose.foundation.BorderStroke(1.dp, StoneBorder)
                ) {
                    Box(modifier = Modifier.fillMaxWidth()) {
                        com.shilora.app.ui.components.HeritageHeroBackground(
                            type = com.shilora.app.ui.components.HeritageHeroTextureType.SCRIPT_WATERMARK,
                            modifier = Modifier.matchParentSize()
                        )
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    imageVector = Icons.Default.School,
                                    contentDescription = null,
                                    tint = BurntAmber,
                                    modifier = Modifier.size(24.dp)
                                )
                                Spacer(Modifier.width(8.dp))
                                Text(
                                    text = "STUDENT & RESEARCH HUB",
                                    style = MaterialTheme.typography.labelMedium.copy(
                                        fontWeight = FontWeight.Bold,
                                        color = NeutralMediumGrey,
                                        letterSpacing = 1.sp
                                    )
                                )
                            }

                            Spacer(Modifier.height(8.dp))

                            Text(
                                text = "Learn Halegannada & Epigraphy",
                                style = MaterialTheme.typography.titleLarge.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = NeutralBlack
                                )
                            )

                            Spacer(Modifier.height(4.dp))

                            Text(
                                text = "Master the scripts, dating methodologies, and linguistic evolution of ancient stone inscriptions of Karnataka.",
                                style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey)
                            )
                        }
                    }
                }
            }

            // Interactive Quiz Card CTA
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = BurntAmber.copy(alpha = 0.12f)),
                    border = androidx.compose.foundation.BorderStroke(1.5.dp, BurntAmber.copy(alpha = 0.6f)),
                    onClick = onQuizSelected
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.Quiz, contentDescription = null, tint = BurntAmber, modifier = Modifier.size(20.dp))
                                Spacer(Modifier.width(6.dp))
                                Text(
                                    text = "QUIZ CHALLENGE",
                                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = BurntAmberDark)
                                )
                            }
                            Spacer(Modifier.height(4.dp))
                            Text(
                                text = "Test Your Knowledge",
                                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
                            )
                            Text(
                                text = "Short epigraphy & character recognition questions.",
                                style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey)
                            )
                        }
                        Icon(
                            imageVector = Icons.Default.ChevronRight,
                            contentDescription = "Start Quiz",
                            tint = BurntAmber,
                            modifier = Modifier.size(28.dp)
                        )
                    }
                }
            }

            // Structured Lessons List
            item {
                ShiloraSectionHeader(
                    title = "Curated Lessons",
                    subtitle = "Foundational modules designed for students and researchers"
                )
            }

            items(lessons, key = { it.id }) { lesson ->
                LessonCard(
                    lesson = lesson,
                    onClick = { onLessonSelected(lesson.id) }
                )
            }
        }
    }
}

@Composable
private fun LessonCard(
    lesson: Lesson,
    onClick: () -> Unit
) {
    ShiloraCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                shape = RoundedCornerShape(6.dp),
                color = SageGreenDark.copy(alpha = 0.15f)
            ) {
                Text(
                    text = lesson.category,
                    style = MaterialTheme.typography.labelSmall.copy(
                        color = SageGreenDark,
                        fontWeight = FontWeight.Bold
                    ),
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Timer,
                    contentDescription = null,
                    tint = NeutralMediumGrey,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(Modifier.width(4.dp))
                Text(
                    text = "${lesson.estimatedMinutes} min",
                    style = MaterialTheme.typography.labelSmall.copy(color = NeutralMediumGrey)
                )
            }
        }

        Spacer(Modifier.height(10.dp))

        Text(
            text = lesson.title,
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold,
                color = NeutralBlack
            )
        )

        Spacer(Modifier.height(6.dp))

        Text(
            text = lesson.summary,
            style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey)
        )
    }
}
