package com.shilora.app.ui.screens.onboarding

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.MenuBook
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.theme.*
import com.shilora.app.ui.components.HeritageHeroBackground
import com.shilora.app.ui.components.HeritageHeroTextureType
import com.shilora.app.ui.components.ShiloraButton
import kotlinx.coroutines.launch

data class OnboardingSlide(
    val title: String,
    val subtitle: String,
    val icon: ImageVector
)

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun OnboardingScreen(
    onFinished: () -> Unit
) {
    val slides = listOf(
        OnboardingSlide(
            title = "Discover inscriptions.",
            subtitle = "Capture ancient stone carvings across Karnataka with precision epigraphical guidance.",
            icon = Icons.Default.CameraAlt
        ),
        OnboardingSlide(
            title = "Understand Old Kannada.",
            subtitle = "Advanced AI analyzes weathered glyphs, reading Halegannada strokes and line baselines.",
            icon = Icons.Default.AutoAwesome
        ),
        OnboardingSlide(
            title = "Learn the story behind the stone.",
            subtitle = "Read grounded translations, understand historical royal grants, and learn epigraphy.",
            icon = Icons.Default.MenuBook
        )
    )

    val pagerState = rememberPagerState { slides.size }
    val scope = rememberCoroutineScope()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(SageGreenSurface)
    ) {
        HeritageHeroBackground(
            modifier = Modifier.fillMaxSize(),
            type = HeritageHeroTextureType.MONOLITH_SILHOUETTE
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Top Bar
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "SHILORA",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.Bold,
                        color = NeutralBlack
                    )
                )
                TextButton(onClick = onFinished) {
                    Text(
                        text = "Skip",
                        style = MaterialTheme.typography.labelMedium.copy(color = NeutralDarkGrey)
                    )
                }
            }

            // Pager Content
            HorizontalPager(
                state = pagerState,
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) { page ->
                val slide = slides[page]
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Box(
                        modifier = Modifier
                            .size(110.dp)
                            .clip(RoundedCornerShape(24.dp))
                            .background(SageGreenLight.copy(alpha = 0.5f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = slide.icon,
                            contentDescription = null,
                            tint = SageGreenDark,
                            modifier = Modifier.size(54.dp)
                        )
                    }
                    Spacer(Modifier.height(36.dp))
                    Text(
                        text = slide.title,
                        style = MaterialTheme.typography.headlineMedium.copy(
                            fontFamily = FontFamily.Serif,
                            fontWeight = FontWeight.Bold,
                            color = NeutralBlack
                        ),
                        textAlign = TextAlign.Center
                    )
                    Spacer(Modifier.height(14.dp))
                    Text(
                        text = slide.subtitle,
                        style = MaterialTheme.typography.bodyLarge.copy(color = NeutralDarkGrey),
                        textAlign = TextAlign.Center,
                        lineHeight = 24.sp
                    )
                }
            }

            // Bottom Indicators & Action
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Page Indicator Dots
                Row(
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(bottom = 28.dp)
                ) {
                    repeat(slides.size) { index ->
                        val isSelected = pagerState.currentPage == index
                        Box(
                            modifier = Modifier
                                .padding(horizontal = 4.dp)
                                .height(6.dp)
                                .width(if (isSelected) 24.dp else 6.dp)
                                .clip(CircleShape)
                                .background(if (isSelected) BurntAmber else ConcreteGrey)
                        )
                    }
                }

                if (pagerState.currentPage == slides.size - 1) {
                    ShiloraButton(
                        text = "GET STARTED",
                        onClick = onFinished,
                        modifier = Modifier.fillMaxWidth()
                    )
                } else {
                    ShiloraButton(
                        text = "Continue",
                        onClick = {
                            scope.launch {
                                pagerState.animateScrollToPage(pagerState.currentPage + 1)
                            }
                        },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }
    }
}
