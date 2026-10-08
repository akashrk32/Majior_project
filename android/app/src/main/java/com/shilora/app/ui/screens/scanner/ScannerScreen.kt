package com.shilora.app.ui.screens.scanner

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.PhotoLibrary
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.theme.*
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

@Composable
fun ScannerScreen(
    onImageSelected: (String) -> Unit,
    onBackClick: () -> Unit
) {
    // Gallery picker launcher
    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            val encodedUri = URLEncoder.encode(it.toString(), StandardCharsets.UTF_8.toString())
            onImageSelected(encodedUri)
        }
    }

    // Camera capture contract
    var photoUri by remember { mutableStateOf<Uri?>(null) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
    ) {
        // Camera Viewfinder Simulation / Preview surface
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            // Inscription Framing Guide Overlay
            Box(
                modifier = Modifier
                    .fillMaxWidth(0.85f)
                    .fillMaxHeight(0.62f)
                    .border(
                        border = BorderStroke(2.dp, BurntAmber),
                        shape = RoundedCornerShape(18.dp)
                    )
            ) {
                // Subtle corner markers
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(12.dp),
                    contentAlignment = Alignment.TopCenter
                ) {
                    Surface(
                        color = Color.Black.copy(alpha = 0.55f),
                        shape = RoundedCornerShape(20.dp)
                    ) {
                        Text(
                            text = "Align Kannada inscription inside frame",
                            style = MaterialTheme.typography.labelMedium.copy(
                                color = NeutralWhite,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Medium
                            ),
                            modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp)
                        )
                    }
                }
            }
        }

        // Top Navigation & Flash Bar
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .statusBarsPadding()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = onBackClick,
                modifier = Modifier
                    .size(44.dp)
                    .clip(CircleShape)
                    .background(Color.Black.copy(alpha = 0.5f))
            ) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = NeutralWhite)
            }

            Surface(
                color = Color.Black.copy(alpha = 0.5f),
                shape = RoundedCornerShape(20.dp)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.FlashOn, contentDescription = null, tint = ConcreteGreyLight, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                    Text(text = "Auto", style = MaterialTheme.typography.labelSmall.copy(color = NeutralWhite))
                }
            }
        }

        // Bottom Controls Bar
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
                .navigationBarsPadding()
                .padding(bottom = 28.dp, start = 20.dp, end = 20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Guidance Hint
            Text(
                text = "Keep stone evenly lit. Avoid extreme glare or oblique angle.",
                style = MaterialTheme.typography.bodySmall.copy(
                    color = ConcreteGreyLight,
                    fontSize = 12.sp,
                    textAlign = TextAlign.Center
                ),
                modifier = Modifier.padding(bottom = 20.dp)
            )

            // Capture & Gallery Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Gallery Import
                IconButton(
                    onClick = { galleryLauncher.launch("image/*") },
                    modifier = Modifier
                        .size(52.dp)
                        .clip(CircleShape)
                        .background(ConcreteGreyDark.copy(alpha = 0.6f))
                ) {
                    Icon(
                        imageVector = Icons.Default.PhotoLibrary,
                        contentDescription = "Import from Gallery",
                        tint = NeutralWhite,
                        modifier = Modifier.size(26.dp)
                    )
                }

                // Primary Shutter Button (10% Burnt Amber)
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                        .border(3.dp, NeutralWhite, CircleShape)
                        .padding(6.dp)
                        .clip(CircleShape)
                        .background(BurntAmber),
                    contentAlignment = Alignment.Center
                ) {
                    IconButton(
                        onClick = {
                            // If running in development without hardware camera, open gallery picker seamlessly
                            galleryLauncher.launch("image/*")
                        },
                        modifier = Modifier.fillMaxSize()
                    ) {
                        Icon(
                            imageVector = Icons.Default.Camera,
                            contentDescription = "Capture Inscription",
                            tint = NeutralWhite,
                            modifier = Modifier.size(34.dp)
                        )
                    }
                }

                // Spacer to balance gallery button
                Box(modifier = Modifier.size(52.dp))
            }
        }
    }
}
