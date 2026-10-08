package com.shilora.app.ui.screens.confirmation

import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
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
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraButton
import com.shilora.app.ui.components.ShiloraButtonVariant
import java.net.URLDecoder
import java.nio.charset.StandardCharsets

@Composable
fun ImageConfirmationScreen(
    encodedImageUri: String,
    onConfirmClick: (String) -> Unit,
    onRetakeClick: () -> Unit
) {
    val decodedUriString = try {
        URLDecoder.decode(encodedImageUri, StandardCharsets.UTF_8.toString())
    } catch (e: Exception) {
        encodedImageUri
    }

    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = "Confirm Inscription",
                onBackClick = onRetakeClick
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Guidance Header
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.Start
            ) {
                Text(
                    text = "Review Inscription Capture",
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontWeight = FontWeight.Bold,
                        color = NeutralBlack
                    )
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = "Ensure the stone surface is legible and the engraved characters are clearly framed before analysis.",
                    style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey)
                )
            }

            Spacer(Modifier.height(16.dp))

            // Image Preview Container
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(20.dp))
                    .background(ConcreteGreyLight)
                    .border(2.dp, StoneBorder, RoundedCornerShape(20.dp)),
                contentAlignment = Alignment.Center
            ) {
                AsyncImage(
                    model = ImageRequest.Builder(LocalContext.current)
                        .data(Uri.parse(decodedUriString))
                        .crossfade(true)
                        .build(),
                    contentDescription = "Captured Inscription Stone",
                    contentScale = ContentScale.Fit,
                    modifier = Modifier.fillMaxSize()
                )
            }

            Spacer(Modifier.height(20.dp))

            // Action Buttons: USE THIS IMAGE vs RETAKE
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                ShiloraButton(
                    text = "USE THIS IMAGE",
                    icon = Icons.Default.Check,
                    variant = ShiloraButtonVariant.PRIMARY,
                    onClick = { onConfirmClick(encodedImageUri) }
                )

                ShiloraButton(
                    text = "RETAKE PHOTO",
                    icon = Icons.Default.Refresh,
                    variant = ShiloraButtonVariant.SECONDARY,
                    onClick = onRetakeClick
                )
            }
        }
    }
}
