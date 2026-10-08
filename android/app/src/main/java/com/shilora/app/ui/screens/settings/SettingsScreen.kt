package com.shilora.app.ui.screens.settings

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraCard
import com.shilora.app.ui.components.ShiloraSectionHeader

@Composable
fun SettingsScreen(
    onBackClick: () -> Unit,
    onAboutClick: () -> Unit,
    onLogoutClick: () -> Unit = {}
) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val authRepo = remember { com.shilora.app.di.ServiceLocator.getAuthRepository(context) }
    val scanRepo = remember { com.shilora.app.di.ServiceLocator.getScanRepository(context) }
    val currentUser = remember { authRepo.getCurrentUser() }
    val allScans by scanRepo.getAllScans().collectAsState(initial = emptyList())

    var isKannadaPreferred by remember { mutableStateOf(false) }
    var isAutoSaveEnabled by remember { mutableStateOf(true) }
    var isFramingGridEnabled by remember { mutableStateOf(true) }
    var showLogoutDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            PrimaryTopBar(
                title = "Settings",
                onBackClick = onBackClick
            )
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp),
            contentPadding = PaddingValues(top = 12.dp, bottom = 48.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // User Profile Section
            item {
                ShiloraSectionHeader(title = "Researcher Profile")
                ShiloraCard {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            shape = androidx.compose.foundation.shape.CircleShape,
                            color = SageGreenLight,
                            modifier = Modifier.size(52.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    imageVector = if (currentUser?.isGuest == true) Icons.Default.PersonOutline else Icons.Default.Person,
                                    contentDescription = null,
                                    tint = BurntAmber,
                                    modifier = Modifier.size(28.dp)
                                )
                            }
                        }
                        Spacer(Modifier.width(16.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = currentUser?.name ?: "Guest Explorer",
                                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = NeutralBlack)
                            )
                            Text(
                                text = currentUser?.email ?: "guest@shilora.local",
                                style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey)
                            )
                            Spacer(Modifier.height(4.dp))
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Surface(
                                    shape = RoundedCornerShape(6.dp),
                                    color = SageGreen.copy(alpha = 0.2f)
                                ) {
                                    Text(
                                        text = "${allScans.size} Scans Saved",
                                        style = MaterialTheme.typography.labelSmall.copy(
                                            color = NeutralBlack,
                                            fontWeight = FontWeight.Medium
                                        ),
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                                    )
                                }
                                Surface(
                                    shape = RoundedCornerShape(6.dp),
                                    color = ConcreteGreyLight
                                ) {
                                    Text(
                                        text = if (currentUser?.isGuest == true) "Guest Session" else "Researcher",
                                        style = MaterialTheme.typography.labelSmall.copy(
                                            color = NeutralBlack,
                                            fontWeight = FontWeight.Medium
                                        ),
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // Language & Script Preferences
            item {
                ShiloraSectionHeader(title = "Language & Script")
                ShiloraCard {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Primary Interface Language", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold))
                            Text(if (isKannadaPreferred) "ಕನ್ನಡ (Kannada)" else "English", style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey))
                        }
                        Switch(
                            checked = isKannadaPreferred,
                            onCheckedChange = { isKannadaPreferred = it },
                            colors = SwitchDefaults.colors(checkedThumbColor = BurntAmber, checkedTrackColor = BurntAmber.copy(alpha = 0.4f))
                        )
                    }
                }
            }

            // Capture & Camera
            item {
                ShiloraSectionHeader(title = "Camera & Capture")
                ShiloraCard {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Framing Grid & Alignment Guide", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold))
                            Text("Shows inscription bounding overlay in scanner", style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey))
                        }
                        Switch(
                            checked = isFramingGridEnabled,
                            onCheckedChange = { isFramingGridEnabled = it },
                            colors = SwitchDefaults.colors(checkedThumbColor = BurntAmber, checkedTrackColor = BurntAmber.copy(alpha = 0.4f))
                        )
                    }
                }
            }

            // Analysis Backend Server Environment
            item {
                val context = androidx.compose.ui.platform.LocalContext.current
                var currentUrl by remember { mutableStateOf(com.shilora.app.di.ServiceLocator.backendBaseUrl) }
                var showUrlDialog by remember { mutableStateOf(false) }

                ShiloraSectionHeader(title = "Analysis Backend Environment")
                ShiloraCard(onClick = { showUrlDialog = true }) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Epigraphy Server Endpoint", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold))
                            Text(currentUrl, style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey))
                        }
                        Icon(Icons.Default.Edit, contentDescription = "Edit Endpoint", tint = BurntAmber, modifier = Modifier.size(20.dp))
                    }
                }

                if (showUrlDialog) {
                    var editUrl by remember { mutableStateOf(currentUrl) }
                    AlertDialog(
                        onDismissRequest = { showUrlDialog = false },
                        title = { Text("Configure Backend Server", fontWeight = FontWeight.Bold) },
                        text = {
                            Column {
                                Text("Enter the HTTP address of the SHILORA epigraphy engine:", style = MaterialTheme.typography.bodySmall)
                                Spacer(Modifier.height(8.dp))
                                OutlinedTextField(
                                    value = editUrl,
                                    onValueChange = { editUrl = it },
                                    singleLine = true,
                                    modifier = Modifier.fillMaxWidth()
                                )
                                Spacer(Modifier.height(6.dp))
                                Text("Default: http://10.0.2.2:5000/ (Android Emulator)", style = MaterialTheme.typography.labelSmall.copy(color = NeutralMediumGrey))
                            }
                        },
                        confirmButton = {
                            Button(
                                onClick = {
                                    com.shilora.app.di.ServiceLocator.setBackendUrl(editUrl, context)
                                    currentUrl = com.shilora.app.di.ServiceLocator.backendBaseUrl
                                    showUrlDialog = false
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = BurntAmber)
                            ) {
                                Text("Save Endpoint", color = NeutralWhite)
                            }
                        },
                        dismissButton = {
                            TextButton(onClick = { showUrlDialog = false }) {
                                Text("Cancel", color = NeutralBlack)
                            }
                        },
                        containerColor = StoneCardSurface
                    )
                }
            }

            // Storage & Scans
            item {
                ShiloraSectionHeader(title = "Local Archive")
                ShiloraCard {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Auto-Save Scanned Stones", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold))
                            Text("Keep scan and field notes in local Room DB", style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey))
                        }
                        Switch(
                            checked = isAutoSaveEnabled,
                            onCheckedChange = { isAutoSaveEnabled = it },
                            colors = SwitchDefaults.colors(checkedThumbColor = BurntAmber, checkedTrackColor = BurntAmber.copy(alpha = 0.4f))
                        )
                    }
                }
            }

            // About & Scholarly Ethics
            item {
                ShiloraSectionHeader(title = "System & Ethics")
                ShiloraCard(onClick = onAboutClick) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("About SHILORA", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold))
                            Text("Product mission, epigraphical ethics & version", style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey))
                        }
                        Icon(Icons.Default.ChevronRight, contentDescription = null, tint = NeutralMediumGrey)
                    }
                }
            }

            // Account Actions
            item {
                Spacer(Modifier.height(8.dp))
                ShiloraCard(
                    onClick = { showLogoutDialog = true },
                    backgroundColor = ConcreteGreyLight
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.ExitToApp,
                            contentDescription = "Log Out",
                            tint = BurntAmber,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = if (currentUser?.isGuest == true) "Exit Guest Session" else "Log Out of Account",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = BurntAmber
                            )
                        )
                    }
                }
            }
        }

        if (showLogoutDialog) {
            AlertDialog(
                onDismissRequest = { showLogoutDialog = false },
                title = { Text("Confirm Logout", fontWeight = FontWeight.Bold) },
                text = { Text("Are you sure you want to end your active session and return to the welcome screen?") },
                confirmButton = {
                    Button(
                        onClick = {
                            showLogoutDialog = false
                            authRepo.logout()
                            onLogoutClick()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = BurntAmber)
                    ) {
                        Text("Log Out", color = NeutralWhite)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showLogoutDialog = false }) {
                        Text("Cancel", color = NeutralBlack)
                    }
                },
                containerColor = StoneCardSurface
            )
        }
    }
}
