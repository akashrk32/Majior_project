package com.shilora.app.ui.screens.home

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.domain.model.HeritageItem
import com.shilora.app.domain.model.Lesson
import com.shilora.app.domain.model.ScanResult
import com.shilora.app.theme.*
import com.shilora.app.ui.components.*

import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import com.shilora.app.di.ServiceLocator

@Composable
fun HomeScreen(
    onScanClick: () -> Unit,
    onExploreClick: () -> Unit,
    onLearnClick: () -> Unit,
    onMyScansClick: () -> Unit,
    onAssistantClick: (String?) -> Unit,
    onSettingsClick: () -> Unit,
    onScanResultClick: (String) -> Unit,
    onExploreDetailClick: (String) -> Unit = {},
    onLessonDetailClick: (String) -> Unit = {},
    viewModel: HomeViewModel? = null
) {
    val context = LocalContext.current
    val homeViewModel = viewModel ?: remember {
        HomeViewModel(
            scanRepository = ServiceLocator.getScanRepository(context),
            heritageRepository = ServiceLocator.heritageRepository,
            learningRepository = ServiceLocator.learningRepository
        )
    }
    val uiState by homeViewModel.uiState.collectAsState()

    Scaffold(
        containerColor = SageGreenSurface
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 20.dp),
            contentPadding = PaddingValues(top = 16.dp, bottom = 96.dp)
        ) {
            // Header Bar
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 18.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "SHILORA",
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontFamily = FontFamily.Serif,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 2.sp,
                                color = NeutralBlack
                            )
                        )
                        Text(
                            text = "Epigraphy & Heritage AI",
                            style = MaterialTheme.typography.labelSmall.copy(color = SageGreenDark)
                        )
                    }
                    IconButton(onClick = onSettingsClick) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Settings",
                            tint = NeutralDarkGrey
                        )
                    }
                }
            }

            // A. Hero / Value Proposition Section
            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 20.dp),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = SageGreen), // 60% Sage Green brand surface
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Box(modifier = Modifier.fillMaxWidth()) {
                        HeritageHeroBackground(
                            type = HeritageHeroTextureType.STONE_INSCRIPTION,
                            modifier = Modifier.matchParentSize()
                        )
                        Column(modifier = Modifier.padding(22.dp)) {
                            Text(
                                text = "Read the stories carved in stone.",
                                style = MaterialTheme.typography.headlineMedium.copy(
                                    fontFamily = FontFamily.Serif,
                                    fontWeight = FontWeight.Bold,
                                    color = NeutralWhite
                                ),
                                lineHeight = 32.sp
                            )
                            Spacer(Modifier.height(10.dp))
                            Text(
                                text = "Scan a Kannada stone inscription and uncover its palaeographic text, translation, and historical meaning.",
                                style = MaterialTheme.typography.bodyMedium.copy(color = NeutralWhite.copy(alpha = 0.9f)),
                                lineHeight = 20.sp
                            )
                            Spacer(Modifier.height(22.dp))

                            // B. THE ONE AND ONLY PRIMARY CAMERA SCAN CTA
                            ShiloraButton(
                                text = "SCAN INSCRIPTION",
                                icon = Icons.Default.CameraAlt,
                                onClick = onScanClick,
                                variant = ShiloraButtonVariant.PRIMARY // 10% Burnt Amber
                            )
                        }
                    }
                }
            }

            // C. "How SHILORA Works" Section
            item {
                ShiloraCard(
                    modifier = Modifier.padding(bottom = 22.dp),
                    backgroundColor = StoneCardSurface
                ) {
                    Text(
                        text = "How SHILORA Works",
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
                    )
                    Spacer(Modifier.height(14.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        WorkflowStep(number = "1", title = "Capture", desc = "Even lighting", icon = Icons.Default.PhotoCamera)
                        Icon(Icons.Default.ArrowForward, contentDescription = null, tint = ConcreteGreyDark, modifier = Modifier.align(Alignment.CenterVertically))
                        WorkflowStep(number = "2", title = "Read", desc = "Palaeographic AI", icon = Icons.Default.Visibility)
                        Icon(Icons.Default.ArrowForward, contentDescription = null, tint = ConcreteGreyDark, modifier = Modifier.align(Alignment.CenterVertically))
                        WorkflowStep(number = "3", title = "Understand", desc = "Grounded story", icon = Icons.Default.AutoStories)
                    }
                }
            }

            // D. Recent Scans (if any)
            if (uiState.recentScans.isNotEmpty()) {
                item {
                    ShiloraSectionHeader(
                        title = "Recent Scans",
                        actionText = "View All",
                        onActionClick = onMyScansClick
                    )
                }
                items(uiState.recentScans) { scan ->
                    RecentScanCard(scan = scan, onClick = { onScanResultClick(scan.id) })
                    Spacer(Modifier.height(8.dp))
                }
                item { Spacer(Modifier.height(14.dp)) }
            }

            // E. Featured Heritage Inscriptions
            item {
                ShiloraSectionHeader(
                    title = "Featured Heritage",
                    subtitle = "Discover landmark historical Kannada epigraphs",
                    actionText = "Explore More",
                    onActionClick = onExploreClick
                )
            }
            items(uiState.featuredHeritage) { item ->
                FeaturedHeritageCard(item = item, onClick = { onExploreDetailClick(item.id) })
                Spacer(Modifier.height(10.dp))
            }

            // F. Student Learning Hub Preview
            item {
                Spacer(Modifier.height(12.dp))
                ShiloraSectionHeader(
                    title = "Student Learning Hub",
                    subtitle = "Explore Halegannada epigraphy lessons",
                    actionText = "All Lessons",
                    onActionClick = onLearnClick
                )
            }
            items(uiState.quickLessons) { lesson ->
                QuickLessonCard(lesson = lesson, onClick = { onLessonDetailClick(lesson.id) })
                Spacer(Modifier.height(8.dp))
            }

            // G. AI Heritage Assistant Invitation Banner
            item {
                Spacer(Modifier.height(16.dp))
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onAssistantClick(null) },
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = SageGreenLight.copy(alpha = 0.35f)),
                    border = BorderStroke(1.dp, SageGreenDark.copy(alpha = 0.3f))
                ) {
                    Row(
                        modifier = Modifier.padding(18.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(44.dp)
                                .clip(CircleShape)
                                .background(BurntAmber),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = NeutralWhite)
                        }
                        Spacer(Modifier.width(14.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Have questions about an inscription?",
                                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
                            )
                            Spacer(Modifier.height(2.dp))
                            Text(
                                text = "Ask SHILORA AI about vocabulary, dynasties, and reading stones.",
                                style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey)
                            )
                        }
                        Icon(Icons.Default.ChevronRight, contentDescription = null, tint = SageGreenDark)
                    }
                }
            }
        }
    }
}

@Composable
private fun WorkflowStep(number: String, title: String, desc: String, icon: ImageVector) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            modifier = Modifier
                .size(38.dp)
                .clip(CircleShape)
                .background(SageGreenLight.copy(alpha = 0.4f)),
            contentAlignment = Alignment.Center
        ) {
            Icon(icon, contentDescription = null, tint = SageGreenDark, modifier = Modifier.size(20.dp))
        }
        Spacer(Modifier.height(6.dp))
        Text(text = title, style = MaterialTheme.typography.titleSmall.copy(fontSize = 13.sp, fontWeight = FontWeight.Bold, color = NeutralBlack))
        Text(text = desc, style = MaterialTheme.typography.bodySmall.copy(fontSize = 11.sp, color = NeutralMediumGrey))
    }
}

@Composable
private fun RecentScanCard(scan: ScanResult, onClick: () -> Unit) {
    ShiloraCard(onClick = onClick) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(46.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(ConcreteGreyLight),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Default.Image, contentDescription = null, tint = ConcreteGreyDark)
            }
            Spacer(Modifier.width(14.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = scan.inscriptionSummary.take(55) + if (scan.inscriptionSummary.length > 55) "..." else "",
                    style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
                )
                Spacer(Modifier.height(2.dp))
                Text(
                    text = "${scan.lines.size} lines detected",
                    style = MaterialTheme.typography.bodySmall.copy(color = NeutralMediumGrey)
                )
            }
            ConfidenceBadge(level = scan.confidenceLevel)
        }
    }
}

@Composable
private fun FeaturedHeritageCard(item: HeritageItem, onClick: () -> Unit) {
    ShiloraCard(onClick = onClick) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Surface(
                    shape = RoundedCornerShape(4.dp),
                    color = ConcreteGreyLight.copy(alpha = 0.5f)
                ) {
                    Text(
                        text = item.period,
                        style = MaterialTheme.typography.labelSmall.copy(color = NeutralDarkGrey, fontWeight = FontWeight.Bold),
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
                Spacer(Modifier.height(4.dp))
                Text(
                    text = item.title,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = item.summary.take(110) + "...",
                    style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey),
                    lineHeight = 18.sp
                )
            }
            Icon(Icons.Default.ChevronRight, contentDescription = null, tint = ConcreteGreyDark, modifier = Modifier.padding(top = 16.dp))
        }
    }
}

@Composable
private fun QuickLessonCard(lesson: Lesson, onClick: () -> Unit) {
    ShiloraCard(onClick = onClick) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(SageGreenLight.copy(alpha = 0.35f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Default.School, contentDescription = null, tint = SageGreenDark, modifier = Modifier.size(20.dp))
            }
            Spacer(Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = lesson.title,
                    style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
                )
                Text(
                    text = "${lesson.category} • ${lesson.estimatedMinutes} min read",
                    style = MaterialTheme.typography.bodySmall.copy(color = NeutralMediumGrey)
                )
            }
            Icon(Icons.Default.ChevronRight, contentDescription = null, tint = ConcreteGreyDark)
        }
    }
}
