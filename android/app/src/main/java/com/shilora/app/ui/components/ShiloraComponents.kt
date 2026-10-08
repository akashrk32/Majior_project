package com.shilora.app.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.domain.model.ConfidenceLevel
import com.shilora.app.theme.*

// ============================================================
// 1. SHILORA BUTTONS (Burnt Amber Primary CTA, Concrete Secondary)
// ============================================================

enum class ShiloraButtonVariant {
    PRIMARY,    // Burnt Amber (#CC5500) - For the 10% CTA / Scan
    SECONDARY,  // Concrete Grey (#A7A7A7) - Supporting actions
    OUTLINE     // Sage Green border
}

@Composable
fun ShiloraButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    variant: ShiloraButtonVariant = ShiloraButtonVariant.PRIMARY,
    enabled: Boolean = true
) {
    when (variant) {
        ShiloraButtonVariant.PRIMARY -> {
            Button(
                onClick = onClick,
                enabled = enabled,
                modifier = modifier
                    .height(52.dp)
                    .fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = BurntAmber,
                    contentColor = NeutralWhite,
                    disabledContainerColor = ConcreteGrey
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 2.dp)
            ) {
                if (icon != null) {
                    Icon(icon, contentDescription = null, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(8.dp))
                }
                Text(
                    text = text,
                    style = MaterialTheme.typography.labelLarge.copy(fontSize = 15.sp, fontWeight = FontWeight.Bold)
                )
            }
        }
        ShiloraButtonVariant.SECONDARY -> {
            Button(
                onClick = onClick,
                enabled = enabled,
                modifier = modifier
                    .height(48.dp)
                    .fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = ConcreteGreyLight,
                    contentColor = NeutralBlack
                )
            ) {
                if (icon != null) {
                    Icon(icon, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(8.dp))
                }
                Text(
                    text = text,
                    style = MaterialTheme.typography.labelLarge.copy(color = NeutralBlack, fontSize = 14.sp)
                )
            }
        }
        ShiloraButtonVariant.OUTLINE -> {
            OutlinedButton(
                onClick = onClick,
                enabled = enabled,
                modifier = modifier
                    .height(48.dp)
                    .fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.5.dp, SageGreenDark),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = SageGreenDark)
            ) {
                if (icon != null) {
                    Icon(icon, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(8.dp))
                }
                Text(
                    text = text,
                    style = MaterialTheme.typography.labelLarge.copy(color = SageGreenDark, fontSize = 14.sp)
                )
            }
        }
    }
}

// ============================================================
// 2. SHILORA CARD (Stone-inspired concrete grey 30% surface)
// ============================================================

@Composable
fun ShiloraCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    backgroundColor: Color = StoneCardSurface,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .then(if (onClick != null) Modifier.clickable { onClick() } else Modifier),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = backgroundColor),
        border = BorderStroke(1.dp, StoneBorder),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            content()
        }
    }
}

// ============================================================
// 3. SECTION HEADER
// ============================================================

@Composable
fun ShiloraSectionHeader(
    title: String,
    subtitle: String? = null,
    actionText: String? = null,
    onActionClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxWidth().padding(vertical = 8.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
            )
            if (actionText != null && onActionClick != null) {
                Text(
                    text = actionText,
                    style = MaterialTheme.typography.labelMedium.copy(color = BurntAmberDark, fontWeight = FontWeight.SemiBold),
                    modifier = Modifier.clickable { onActionClick() }
                )
            }
        }
        if (subtitle != null) {
            Spacer(Modifier.height(4.dp))
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodySmall.copy(color = NeutralMediumGrey)
            )
        }
    }
}

// ============================================================
// 4. CONFIDENCE BADGE (Trust model visual indicator)
// ============================================================

@Composable
fun ConfidenceBadge(
    level: ConfidenceLevel,
    modifier: Modifier = Modifier
) {
    val (badgeBg, badgeText) = when (level) {
        ConfidenceLevel.HIGH -> Pair(SageGreen.copy(alpha = 0.20f), SageGreen)
        ConfidenceLevel.MODERATE -> Pair(BurntAmber.copy(alpha = 0.15f), BurntAmber)
        ConfidenceLevel.LOW -> Pair(ConcreteGrey.copy(alpha = 0.25f), BurntAmber)
        ConfidenceLevel.UNCERTAIN -> Pair(ConcreteGrey.copy(alpha = 0.25f), ConcreteGrey)
    }

    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(8.dp),
        color = badgeBg,
        border = BorderStroke(1.dp, badgeText.copy(alpha = 0.4f))
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(6.dp)
                    .clip(CircleShape)
                    .background(badgeText)
            )
            Spacer(Modifier.width(6.dp))
            Text(
                text = level.label,
                style = MaterialTheme.typography.labelSmall.copy(
                    color = badgeText,
                    fontWeight = FontWeight.Bold
                )
            )
        }
    }
}

// ============================================================
// 5. RESULT SECTION (Collapsible or distinct heritage block)
// ============================================================

@Composable
fun ResultSection(
    title: String,
    badgeText: String? = null,
    defaultExpanded: Boolean = true,
    content: @Composable () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = StoneCardSurface),
        border = BorderStroke(1.dp, StoneBorder)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = NeutralBlack
                    )
                )
                if (badgeText != null) {
                    Surface(
                        shape = RoundedCornerShape(6.dp),
                        color = SageGreenLight.copy(alpha = 0.4f)
                    ) {
                        Text(
                            text = badgeText,
                            style = MaterialTheme.typography.labelSmall.copy(
                                color = SageGreenDark,
                                fontWeight = FontWeight.SemiBold
                            ),
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }
            }
            Spacer(Modifier.height(10.dp))
            content()
        }
    }
}

// ============================================================
// 6. TOP APP BAR
// ============================================================

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PrimaryTopBar(
    title: String,
    onBackClick: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {}
) {
    TopAppBar(
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge.copy(
                    fontFamily = androidx.compose.ui.text.font.FontFamily.Serif,
                    fontWeight = FontWeight.Bold,
                    color = NeutralBlack
                )
            )
        },
        navigationIcon = {
            if (onBackClick != null) {
                IconButton(onClick = onBackClick) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = NeutralBlack
                    )
                }
            }
        },
        actions = actions,
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = SageGreenSurface,
            titleContentColor = NeutralBlack
        )
    )
}

// ============================================================
// 7. EMPTY & ERROR STATES
// ============================================================

@Composable
fun EmptyState(
    title: String,
    message: String,
    actionButtonText: String? = null,
    onActionClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(64.dp)
                .clip(CircleShape)
                .background(ConcreteGreyLight.copy(alpha = 0.5f)),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Default.HistoryEdu,
                contentDescription = null,
                tint = ConcreteGreyDark,
                modifier = Modifier.size(32.dp)
            )
        }
        Spacer(Modifier.height(16.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
        )
        Spacer(Modifier.height(6.dp))
        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium.copy(color = NeutralMediumGrey),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
        if (actionButtonText != null && onActionClick != null) {
            Spacer(Modifier.height(20.dp))
            ShiloraButton(
                text = actionButtonText,
                onClick = onActionClick,
                variant = ShiloraButtonVariant.PRIMARY,
                modifier = Modifier.width(200.dp)
            )
        }
    }
}

@Composable
fun ErrorState(
    title: String,
    errorMessage: String,
    onRetryClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(28.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.ErrorOutline,
            contentDescription = null,
            tint = BurntAmber,
            modifier = Modifier.size(48.dp)
        )
        Spacer(Modifier.height(14.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
        )
        Spacer(Modifier.height(6.dp))
        Text(
            text = errorMessage,
            style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
        Spacer(Modifier.height(20.dp))
        ShiloraButton(
            text = "Try Again",
            onClick = onRetryClick,
            variant = ShiloraButtonVariant.PRIMARY,
            modifier = Modifier.width(180.dp)
        )
    }
}

// ============================================================
// 12. SUBTLE HERITAGE BACKGROUNDS (Subtle texture overlays)
// ============================================================

enum class HeritageHeroTextureType {
    STONE_INSCRIPTION,
    ARCHAEOLOGICAL_MOTIF,
    SCRIPT_WATERMARK,
    MONOLITH_SILHOUETTE
}

@Composable
fun HeritageHeroBackground(
    type: HeritageHeroTextureType,
    modifier: Modifier = Modifier
) {
    androidx.compose.foundation.Canvas(modifier = modifier.fillMaxSize()) {
        val width = size.width
        val height = size.height

        when (type) {
            HeritageHeroTextureType.STONE_INSCRIPTION -> {
                // Subtle horizontal chiseled line striations
                val strokeColor = BurntAmber.copy(alpha = 0.08f)
                val fractureColor = SageGreenDark.copy(alpha = 0.10f)

                for (i in 1..8) {
                    val y = height * (i / 9f)
                    drawLine(
                        color = strokeColor,
                        start = androidx.compose.ui.geometry.Offset(20f, y),
                        end = androidx.compose.ui.geometry.Offset(width - 20f, y),
                        strokeWidth = 1.5f
                    )
                }
                // Subtle carved stone contour
                drawCircle(
                    color = fractureColor,
                    radius = height * 0.45f,
                    center = androidx.compose.ui.geometry.Offset(width * 0.85f, height * 0.5f)
                )
            }
            HeritageHeroTextureType.ARCHAEOLOGICAL_MOTIF -> {
                val tint = ConcreteGreyDark.copy(alpha = 0.07f)
                // Lintel lines and arch
                drawRect(
                    color = tint,
                    topLeft = androidx.compose.ui.geometry.Offset(width * 0.1f, 15f),
                    size = androidx.compose.ui.geometry.Size(width * 0.8f, 12f)
                )
                drawCircle(
                    color = tint,
                    radius = width * 0.35f,
                    center = androidx.compose.ui.geometry.Offset(width * 0.5f, height * 0.9f)
                )
            }
            HeritageHeroTextureType.SCRIPT_WATERMARK -> {
                val markColor = BurntAmber.copy(alpha = 0.06f)
                // Ancient circular script glyph loops
                drawCircle(
                    color = markColor,
                    radius = 36f,
                    center = androidx.compose.ui.geometry.Offset(width * 0.82f, height * 0.35f)
                )
                drawCircle(
                    color = markColor,
                    radius = 28f,
                    center = androidx.compose.ui.geometry.Offset(width * 0.72f, height * 0.65f)
                )
            }
            HeritageHeroTextureType.MONOLITH_SILHOUETTE -> {
                val steleTint = SageGreenDark.copy(alpha = 0.08f)
                drawRoundRect(
                    color = steleTint,
                    topLeft = androidx.compose.ui.geometry.Offset(width * 0.6f, 10f),
                    size = androidx.compose.ui.geometry.Size(width * 0.35f, height - 20f),
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(24f, 24f)
                )
            }
        }
    }
}
