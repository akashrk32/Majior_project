package com.shilora.app.ui.screens.myscans

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Collections
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
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
import com.shilora.app.domain.model.ScanResult
import com.shilora.app.theme.*
import com.shilora.app.ui.components.ConfidenceBadge
import com.shilora.app.ui.components.EmptyState
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraCard
import java.text.SimpleDateFormat
import java.util.Locale

@Composable
fun MyScansScreen(
    onScanClick: (String) -> Unit
) {
    val context = LocalContext.current
    val scanRepository = remember { ServiceLocator.getScanRepository(context) }
    val scans by scanRepository.getAllScans().collectAsState(initial = emptyList())

    val dateFormat = remember { SimpleDateFormat("dd MMM yyyy", Locale.getDefault()) }

    Scaffold(
        topBar = {
            PrimaryTopBar(title = "My Scan Library")
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        if (scans.isEmpty()) {
            EmptyState(
                title = "No Inscriptions Saved",
                message = "Your scanned stone records and epigraphical notes will appear here as your personal research archive.",
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
            )
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(top = 12.dp, bottom = 48.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(scans, key = { it.id }) { scan ->
                    ScanLibraryItemCard(
                        scan = scan,
                        dateFormat = dateFormat,
                        onClick = { onScanClick(scan.id) }
                    )
                }
            }
        }
    }
}

@Composable
private fun ScanLibraryItemCard(
    scan: ScanResult,
    dateFormat: SimpleDateFormat,
    onClick: () -> Unit
) {
    ShiloraCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Thumbnail
            Box(
                modifier = Modifier
                    .size(76.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(ConcreteGreyLight)
            ) {
                AsyncImage(
                    model = ImageRequest.Builder(LocalContext.current)
                        .data(scan.localImagePath)
                        .crossfade(true)
                        .build(),
                    contentDescription = null,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxSize()
                )
            }

            Spacer(Modifier.width(14.dp))

            // Details
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = if (!scan.siteName.isNullOrBlank()) scan.siteName else "Kannada Stone Inscription",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = NeutralBlack
                    ),
                    maxLines = 1,
                    overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
                )

                Spacer(Modifier.height(4.dp))

                Text(
                    text = "Scanned on ${dateFormat.format(scan.scannedAt)}",
                    style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey)
                )

                Spacer(Modifier.height(8.dp))

                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    ConfidenceBadge(level = scan.confidenceLevel)

                    Surface(
                        shape = RoundedCornerShape(6.dp),
                        color = ConcreteGreyLight.copy(alpha = 0.6f)
                    ) {
                        Text(
                            text = "${scan.lines.size} lines",
                            style = MaterialTheme.typography.labelSmall.copy(color = NeutralBlack),
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }
            }

            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = "View Inscription",
                tint = NeutralMediumGrey,
                modifier = Modifier.size(22.dp)
            )
        }
    }
}
