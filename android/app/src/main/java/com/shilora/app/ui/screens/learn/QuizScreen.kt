package com.shilora.app.ui.screens.learn

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.di.ServiceLocator
import com.shilora.app.domain.model.QuizQuestion
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraButton
import com.shilora.app.ui.components.ShiloraButtonVariant
import com.shilora.app.ui.components.ShiloraCard

@Composable
fun QuizScreen(
    onBackClick: () -> Unit
) {
    val learningRepository = remember { ServiceLocator.learningRepository }
    val questions = remember { learningRepository.getQuizQuestions() }

    var currentIndex by remember { mutableStateOf(0) }
    var selectedOptionIndex by remember { mutableStateOf<Int?>(null) }
    var hasAnswered by remember { mutableStateOf(false) }
    var score by remember { mutableStateOf(0) }
    var isQuizCompleted by remember { mutableStateOf(false) }

    val currentQuestion = questions.getOrNull(currentIndex)

    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = "Epigraphy Quiz",
                onBackClick = onBackClick
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(20.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            if (isQuizCompleted) {
                // Quiz Completed Summary Card
                ShiloraCard(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.fillMaxWidth().padding(12.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Quiz Completed",
                            style = MaterialTheme.typography.headlineSmall.copy(
                                fontWeight = FontWeight.Bold,
                                color = NeutralBlack
                            )
                        )
                        Spacer(Modifier.height(8.dp))
                        Text(
                            text = "Your Epigraphical Score:",
                            style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey)
                        )
                        Spacer(Modifier.height(12.dp))
                        Text(
                            text = "$score / ${questions.size}",
                            style = MaterialTheme.typography.displayMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = BurntAmber
                            )
                        )
                        Spacer(Modifier.height(20.dp))
                        ShiloraButton(
                            text = "Restart Quiz",
                            variant = ShiloraButtonVariant.PRIMARY,
                            onClick = {
                                currentIndex = 0
                                selectedOptionIndex = null
                                hasAnswered = false
                                score = 0
                                isQuizCompleted = false
                            }
                        )
                    }
                }
            } else if (currentQuestion != null) {
                LazyColumn(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Question Counter Header
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "QUESTION ${currentIndex + 1} OF ${questions.size}",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = NeutralMediumGrey,
                                    letterSpacing = 1.sp
                                )
                            )
                            Text(
                                text = "Score: $score",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = BurntAmberDark
                                )
                            )
                        }
                    }

                    // Question Card
                    item {
                        ShiloraCard {
                            if (currentQuestion.characterPrompt != null) {
                                Box(
                                    modifier = Modifier
                                        .size(64.dp)
                                        .align(Alignment.CenterHorizontally)
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(SageGreenLight)
                                        .border(1.5.dp, SageGreenDark, RoundedCornerShape(12.dp)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = currentQuestion.characterPrompt,
                                        style = MaterialTheme.typography.headlineLarge.copy(
                                            fontWeight = FontWeight.Bold,
                                            color = NeutralBlack
                                        )
                                    )
                                }
                                Spacer(Modifier.height(14.dp))
                            }

                            Text(
                                text = currentQuestion.questionText,
                                style = MaterialTheme.typography.titleMedium.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = NeutralBlack
                                )
                            )
                        }
                    }

                    // Options List
                    items(currentQuestion.options.size) { optionIndex ->
                        val optionText = currentQuestion.options[optionIndex]
                        val isSelected = selectedOptionIndex == optionIndex
                        val isCorrect = currentQuestion.correctIndex == optionIndex

                        val containerColor = when {
                            !hasAnswered -> if (isSelected) BurntAmber.copy(alpha = 0.15f) else StoneCardSurface
                            isCorrect -> SageGreenLight
                            isSelected -> ConcreteGrey.copy(alpha = 0.25f)
                            else -> StoneCardSurface
                        }

                        val borderColor = when {
                            !hasAnswered -> if (isSelected) BurntAmber else StoneBorder
                            isCorrect -> SageGreenDark
                            isSelected -> BurntAmber
                            else -> StoneBorder
                        }

                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable(enabled = !hasAnswered) {
                                    selectedOptionIndex = optionIndex
                                },
                            shape = RoundedCornerShape(12.dp),
                            colors = CardDefaults.cardColors(containerColor = containerColor),
                            border = androidx.compose.foundation.BorderStroke(1.5.dp, borderColor)
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(16.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = optionText,
                                    style = MaterialTheme.typography.bodyMedium.copy(
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        color = NeutralBlack
                                    )
                                )

                                if (hasAnswered) {
                                    if (isCorrect) {
                                        Icon(Icons.Default.CheckCircle, contentDescription = "Correct", tint = SageGreenDark)
                                    } else if (isSelected) {
                                        Icon(Icons.Default.Close, contentDescription = "Incorrect", tint = BurntAmber)
                                    }
                                }
                            }
                        }
                    }

                    // Explanation Card
                    if (hasAnswered) {
                        item {
                            ShiloraCard(backgroundColor = SageGreenLight.copy(alpha = 0.4f)) {
                                Text(
                                    text = "EXPLANATION",
                                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = SageGreenDark)
                                )
                                Spacer(Modifier.height(4.dp))
                                Text(
                                    text = currentQuestion.explanation,
                                    style = MaterialTheme.typography.bodyMedium.copy(color = NeutralBlack)
                                )
                            }
                        }
                    }
                }

                // Bottom Action
                Box(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
                    if (!hasAnswered) {
                        ShiloraButton(
                            text = "SUBMIT ANSWER",
                            variant = ShiloraButtonVariant.PRIMARY,
                            enabled = selectedOptionIndex != null,
                            onClick = {
                                hasAnswered = true
                                if (selectedOptionIndex == currentQuestion.correctIndex) {
                                    score += 1
                                }
                            }
                        )
                    } else {
                        ShiloraButton(
                            text = if (currentIndex + 1 < questions.size) "NEXT QUESTION" else "VIEW FINAL SCORE",
                            variant = ShiloraButtonVariant.PRIMARY,
                            onClick = {
                                if (currentIndex + 1 < questions.size) {
                                    currentIndex += 1
                                    selectedOptionIndex = null
                                    hasAnswered = false
                                } else {
                                    isQuizCompleted = true
                                }
                            }
                        )
                    }
                }
            }
        }
    }
}
