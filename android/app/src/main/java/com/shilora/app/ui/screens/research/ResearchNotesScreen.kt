package com.shilora.app.ui.screens.research

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.di.ServiceLocator
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraButton
import com.shilora.app.ui.components.ShiloraButtonVariant
import com.shilora.app.ui.components.ShiloraCard
import kotlinx.coroutines.launch

@Composable
fun ResearchNotesScreen(
    scanId: String,
    onBackClick: () -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val scanRepository = remember { ServiceLocator.getScanRepository(context) }

    var siteName by remember { mutableStateOf("") }
    var villageName by remember { mutableStateOf("") }
    var templeName by remember { mutableStateOf("") }
    var notesText by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(true) }

    LaunchedEffect(scanId) {
        val scan = scanRepository.getScanById(scanId)
        if (scan != null) {
            siteName = scan.siteName ?: ""
            villageName = scan.villageName ?: ""
            templeName = scan.templeName ?: ""
            notesText = scan.researchNotes ?: ""
        }
        isLoading = false
    }

    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = "Field & Research Notes",
                onBackClick = onBackClick
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        if (isLoading) {
            Box(Modifier.fillMaxSize().padding(innerPadding), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = BurntAmber)
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
                        text = "Archaeological Field Documentation",
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = NeutralBlack
                        )
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = "Document the physical context, findspot, and structural setting of this inscription.",
                        style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey)
                    )
                }

                item {
                    ShiloraCard {
                        OutlinedTextField(
                            value = siteName,
                            onValueChange = { siteName = it },
                            label = { Text("Site / Archaeological Name") },
                            placeholder = { Text("e.g. Halmidi Stele Complex") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true,
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = BurntAmber,
                                unfocusedBorderColor = StoneBorder,
                                focusedTextColor = NeutralBlack,
                                unfocusedTextColor = NeutralBlack
                            )
                        )

                        Spacer(Modifier.height(12.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            OutlinedTextField(
                                value = villageName,
                                onValueChange = { villageName = it },
                                label = { Text("Village / Town") },
                                placeholder = { Text("e.g. Belur") },
                                modifier = Modifier.weight(1f),
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = BurntAmber,
                                    unfocusedBorderColor = StoneBorder,
                                    focusedTextColor = NeutralBlack,
                                    unfocusedTextColor = NeutralBlack
                                )
                            )

                            OutlinedTextField(
                                value = templeName,
                                onValueChange = { templeName = it },
                                label = { Text("Temple / Landmark") },
                                placeholder = { Text("e.g. Chennakeshava") },
                                modifier = Modifier.weight(1f),
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = BurntAmber,
                                    unfocusedBorderColor = StoneBorder,
                                    focusedTextColor = NeutralBlack,
                                    unfocusedTextColor = NeutralBlack
                                )
                            )
                        }

                        Spacer(Modifier.height(14.dp))

                        OutlinedTextField(
                            value = notesText,
                            onValueChange = { notesText = it },
                            label = { Text("Epigraphical Observations & Questions") },
                            placeholder = { Text("Enter observations on stone weathering, script style, patron names, or unresolved questions...") },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(160.dp),
                            maxLines = 8,
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = BurntAmber,
                                unfocusedBorderColor = StoneBorder,
                                focusedTextColor = NeutralBlack,
                                unfocusedTextColor = NeutralBlack
                            )
                        )
                    }
                }

                item {
                    ShiloraButton(
                        text = "SAVE RESEARCH NOTES",
                        icon = Icons.Default.Save,
                        variant = ShiloraButtonVariant.PRIMARY,
                        onClick = {
                            coroutineScope.launch {
                                scanRepository.updateResearchNotes(
                                    id = scanId,
                                    notes = notesText,
                                    site = siteName,
                                    village = villageName,
                                    temple = templeName
                                )
                                Toast.makeText(context, "Research notes updated successfully", Toast.LENGTH_SHORT).show()
                                onBackClick()
                            }
                        }
                    )
                }
            }
        }
    }
}
