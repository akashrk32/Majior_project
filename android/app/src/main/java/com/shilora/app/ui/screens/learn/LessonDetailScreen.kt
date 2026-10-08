package com.shilora.app.ui.screens.learn

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.di.ServiceLocator
import com.shilora.app.domain.model.ArchaicCharacter
import com.shilora.app.domain.model.LessonSection
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraCard

@Composable
fun LessonDetailScreen(
    lessonId: String,
    onBackClick: () -> Unit
) {
    val learningRepository = remember { ServiceLocator.learningRepository }
    val lesson = remember(lessonId) { learningRepository.getLessonById(lessonId) }

    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = lesson?.category ?: "Lesson",
                onBackClick = onBackClick
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        if (lesson == null) {
            Box(Modifier.fillMaxSize().padding(innerPadding), contentAlignment = Alignment.Center) {
                Text("Lesson not found", color = NeutralDarkGrey)
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(top = 12.dp, bottom = 48.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    Text(
                        text = lesson.title,
                        style = MaterialTheme.typography.headlineSmall.copy(
                            fontWeight = FontWeight.Bold,
                            color = NeutralBlack
                        )
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        text = lesson.summary,
                        style = MaterialTheme.typography.bodyLarge.copy(color = NeutralDarkGrey)
                    )
                }

                items(lesson.contentSections) { section ->
                    SectionCard(section = section)
                }
            }
        }
    }
}

@Composable
private fun SectionCard(section: LessonSection) {
    ShiloraCard {
        Text(
            text = section.heading,
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold,
                color = BurntAmberDark
            )
        )

        Spacer(Modifier.height(8.dp))

        Text(
            text = section.body,
            style = MaterialTheme.typography.bodyLarge.copy(
                color = NeutralBlack,
                lineHeight = 24.sp
            )
        )

        if (!section.archaicCharacters.isNullOrEmpty()) {
            Spacer(Modifier.height(14.dp))
            Text(
                text = "EPIGRAPHICAL GLYPH COMPARISON",
                style = MaterialTheme.typography.labelSmall.copy(
                    fontWeight = FontWeight.Bold,
                    color = NeutralMediumGrey,
                    letterSpacing = 1.sp
                )
            )
            Spacer(Modifier.height(8.dp))

            section.archaicCharacters.forEach { char ->
                ArchaicCharacterCard(character = char)
            }
        }
    }
}

@Composable
private fun ArchaicCharacterCard(character: ArchaicCharacter) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(ConcreteGreyLight.copy(alpha = 0.5f))
            .border(1.dp, StoneBorder, RoundedCornerShape(12.dp))
            .padding(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Large archaic glyph block
            Box(
                modifier = Modifier
                    .size(54.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(SageGreenLight)
                    .border(1.5.dp, SageGreenDark, RoundedCornerShape(10.dp)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = character.halegannadaGlyph,
                    style = MaterialTheme.typography.headlineMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = NeutralBlack
                    )
                )
            }

            Spacer(Modifier.width(14.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "Modern equivalent: ${character.modernKannadaGlyph}  •  IAST: [${character.phoneticIast}]",
                    style = MaterialTheme.typography.labelMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = NeutralBlack
                    )
                )
                Spacer(Modifier.height(2.dp))
                Text(
                    text = character.description,
                    style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey)
                )
            }
        }
    }
}
