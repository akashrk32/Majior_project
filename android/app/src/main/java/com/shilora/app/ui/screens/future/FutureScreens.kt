package com.shilora.app.ui.screens.future

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Compare
import androidx.compose.material.icons.filled.Explore
import androidx.compose.material.icons.filled.VolunteerActivism
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.theme.*
import com.shilora.app.ui.components.EmptyState
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraCard

@Composable
fun FieldModeScreen(
    onBackClick: () -> Unit
) {
    Scaffold(
        topBar = { PrimaryTopBar(title = "Field Expedition Mode", onBackClick = onBackClick) },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ShiloraCard {
                Text(
                    text = "FIELD MODE ARCHITECTURE",
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = BurntAmberDark)
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "Field Expedition Mode enables offline spatial GPS georeferencing, stone weathering index logging, and local tablet surveying for archaeologists and university students.",
                    style = MaterialTheme.typography.bodyMedium.copy(color = NeutralBlack, lineHeight = 22.sp)
                )
            }

            EmptyState(
                title = "Field Logging Active",
                message = "GPS coordination and multi-angle photometric stereo logging ready for upcoming field expeditions.",
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

@Composable
fun CompareInscriptionsScreen(
    onBackClick: () -> Unit
) {
    Scaffold(
        topBar = { PrimaryTopBar(title = "Compare Inscriptions", onBackClick = onBackClick) },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ShiloraCard {
                Text(
                    text = "PALAELOGICAL COMPARISON ENGINE",
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = BurntAmberDark)
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "Compare two historical steles side-by-side to cross-examine character stroke evolution across centuries, patron dynasties, and regional scribal schools.",
                    style = MaterialTheme.typography.bodyMedium.copy(color = NeutralBlack, lineHeight = 22.sp)
                )
            }

            EmptyState(
                title = "Select Scans to Compare",
                message = "Select any two saved records from your scan library to begin palaeographical cross-examination.",
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

@Composable
fun HeritageContributionScreen(
    onBackClick: () -> Unit
) {
    Scaffold(
        topBar = { PrimaryTopBar(title = "Contribute Inscription", onBackClick = onBackClick) },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ShiloraCard {
                Text(
                    text = "SCHOLARLY PEER-REVIEWED SUBMISSION",
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = BurntAmberDark)
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "Submit newly discovered stone records, hero stones, or temple charters for academic verification and archival in the Karnataka Epigraphical Register.",
                    style = MaterialTheme.typography.bodyMedium.copy(color = NeutralBlack, lineHeight = 22.sp)
                )
            }

            EmptyState(
                title = "Epigraphical Moderation",
                message = "Submissions undergo expert verification by archaeological epigraphists before publication.",
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}
