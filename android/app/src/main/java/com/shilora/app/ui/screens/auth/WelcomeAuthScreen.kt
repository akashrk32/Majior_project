package com.shilora.app.ui.screens.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoStories
import androidx.compose.material.icons.filled.LockOpen
import androidx.compose.material.icons.filled.PersonAdd
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.theme.*
import com.shilora.app.ui.components.ShiloraButton
import com.shilora.app.ui.components.ShiloraButtonVariant

@Composable
fun WelcomeAuthScreen(
    onLoginClick: () -> Unit,
    onSignUpClick: () -> Unit,
    onGuestClick: () -> Unit
) {
    Scaffold(
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 28.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Spacer(modifier = Modifier.height(32.dp))

            // Branding Section
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Box(
                    modifier = Modifier
                        .size(92.dp)
                        .clip(CircleShape)
                        .background(SageGreenLight),
                    contentAlignment = Alignment.Center
                ) {
                    Box(
                        modifier = Modifier
                            .size(60.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(BurntAmber),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.AutoStories,
                            contentDescription = "SHILORA Emblem",
                            tint = NeutralWhite,
                            modifier = Modifier.size(36.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                Text(
                    text = "SHILORA",
                    style = MaterialTheme.typography.headlineLarge.copy(
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 4.sp,
                        color = NeutralBlack
                    )
                )

                Text(
                    text = "Shila-Lekha Optical Recognition & Analysis",
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = SageGreenDark,
                        fontWeight = FontWeight.Medium
                    ),
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(18.dp))

                Text(
                    text = "Read the stories carved in stone.",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.SemiBold,
                        color = NeutralBlack.copy(alpha = 0.85f)
                    ),
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = "Explore historical Kannada stone inscriptions, decipher ancient Halegannada epigraphs, and preserve cultural heritage.",
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = NeutralDarkGrey,
                        lineHeight = 22.sp
                    ),
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 12.dp)
                )
            }

            // Actions Section
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 36.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                ShiloraButton(
                    text = "LOGIN",
                    icon = Icons.Default.LockOpen,
                    onClick = onLoginClick,
                    variant = ShiloraButtonVariant.PRIMARY
                )

                ShiloraButton(
                    text = "CREATE ACCOUNT",
                    icon = Icons.Default.PersonAdd,
                    onClick = onSignUpClick,
                    variant = ShiloraButtonVariant.SECONDARY
                )

                TextButton(
                    onClick = onGuestClick,
                    modifier = Modifier.padding(top = 4.dp)
                ) {
                    Text(
                        text = "Continue as Guest",
                        style = MaterialTheme.typography.labelLarge.copy(
                            fontWeight = FontWeight.SemiBold,
                            color = NeutralDarkGrey
                        )
                    )
                }

                Text(
                    text = "Remote backend auth pending. Local research session enabled.",
                    style = MaterialTheme.typography.labelSmall.copy(
                        color = NeutralDarkGrey.copy(alpha = 0.6f)
                    ),
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}
