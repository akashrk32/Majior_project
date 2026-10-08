package com.shilora.app.ui.screens.auth

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shilora.app.di.ServiceLocator
import com.shilora.app.domain.model.AuthResult
import com.shilora.app.theme.*
import com.shilora.app.ui.components.ShiloraButton
import com.shilora.app.ui.components.ShiloraButtonVariant

@Composable
fun ForgotPasswordScreen(
    onBackToLogin: () -> Unit,
    onBackClick: () -> Unit
) {
    val context = LocalContext.current
    val authRepo = remember { ServiceLocator.getAuthRepository(context) }

    var email by remember { mutableStateOf("") }
    var isSubmitted by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    Scaffold(
        containerColor = SageGreenSurface,
        topBar = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBackClick) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = NeutralBlack
                    )
                }
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 28.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(20.dp))

            Text(
                text = "Reset Password",
                style = MaterialTheme.typography.headlineMedium.copy(
                    fontFamily = FontFamily.Serif,
                    fontWeight = FontWeight.Bold,
                    color = NeutralBlack
                )
            )

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = "Enter your registered email address to receive password reset instructions.",
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = NeutralDarkGrey,
                    lineHeight = 22.sp
                ),
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(32.dp))

            if (isSubmitted) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    color = SageGreenLight.copy(alpha = 0.5f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, SageGreenDark.copy(alpha = 0.3f))
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = null,
                            tint = SageGreenDark,
                            modifier = Modifier.size(40.dp)
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            text = "Reset Instructions Sent",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = NeutralBlack
                            )
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "If an account exists for $email, a verification link has been dispatched.",
                            style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey),
                            textAlign = TextAlign.Center
                        )
                    }
                }

                Spacer(modifier = Modifier.height(28.dp))

                ShiloraButton(
                    text = "BACK TO LOGIN",
                    onClick = onBackToLogin,
                    variant = ShiloraButtonVariant.PRIMARY
                )
            } else {
                if (errorMessage != null) {
                    Surface(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 16.dp),
                        shape = RoundedCornerShape(10.dp),
                        color = BurntAmber.copy(alpha = 0.12f),
                        border = androidx.compose.foundation.BorderStroke(1.dp, BurntAmber.copy(alpha = 0.4f))
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.Info,
                                contentDescription = null,
                                tint = BurntAmber,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Text(
                                text = errorMessage ?: "",
                                style = MaterialTheme.typography.bodySmall.copy(
                                    color = NeutralBlack,
                                    fontWeight = FontWeight.Medium
                                )
                            )
                        }
                    }
                }

                OutlinedTextField(
                    value = email,
                    onValueChange = {
                        email = it
                        errorMessage = null
                    },
                    label = { Text("Registered Email") },
                    leadingIcon = {
                        Icon(Icons.Default.Email, contentDescription = null, tint = NeutralDarkGrey)
                    },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = BurntAmber,
                        unfocusedBorderColor = ConcreteGreyDark,
                        focusedLabelColor = BurntAmber,
                        unfocusedLabelColor = NeutralDarkGrey,
                        focusedContainerColor = NeutralWhite,
                        unfocusedContainerColor = NeutralWhite
                    ),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(28.dp))

                ShiloraButton(
                    text = "SEND RESET LINK",
                    icon = Icons.Default.Send,
                    onClick = {
                        when (val res = authRepo.requestPasswordReset(email)) {
                            AuthResult.PendingVerification -> isSubmitted = true
                            is AuthResult.Error -> errorMessage = res.message
                            is AuthResult.Success -> isSubmitted = true
                        }
                    },
                    variant = ShiloraButtonVariant.PRIMARY
                )

                Spacer(modifier = Modifier.height(16.dp))

                TextButton(onClick = onBackToLogin) {
                    Text(
                        text = "Return to Login",
                        style = MaterialTheme.typography.labelLarge.copy(
                            fontWeight = FontWeight.SemiBold,
                            color = BurntAmber
                        )
                    )
                }
            }
        }
    }
}
