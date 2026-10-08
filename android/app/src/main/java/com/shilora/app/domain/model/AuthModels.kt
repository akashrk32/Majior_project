package com.shilora.app.domain.model

data class UserProfile(
    val id: String,
    val name: String,
    val email: String,
    val isGuest: Boolean = false,
    val joinedDate: String = "October 2026",
    val savedScansCount: Int = 0,
    val researchNotesCount: Int = 0
)

sealed class AuthState {
    data object Unauthenticated : AuthState()
    data class Authenticated(val user: UserProfile) : AuthState()
    data class Guest(val user: UserProfile) : AuthState()
}

sealed class AuthResult {
    data class Success(val user: UserProfile) : AuthResult()
    data class Error(val message: String) : AuthResult()
    data object PendingVerification : AuthResult()
}
