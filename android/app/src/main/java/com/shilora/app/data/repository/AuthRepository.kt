package com.shilora.app.data.repository

import android.content.Context
import android.content.SharedPreferences
import com.shilora.app.domain.model.AuthResult
import com.shilora.app.domain.model.AuthState
import com.shilora.app.domain.model.UserProfile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID

/**
 * AuthRepository manages authentication state, local user session, and guest mode.
 *
 * NOTE: Remote authentication endpoints (OAuth2/JWT/OTP) are pending backend implementation.
 * Local session state persists user profile and guest mode in SharedPreferences.
 */
class AuthRepository(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("shilora_auth_prefs", Context.MODE_PRIVATE)

    private val _authState = MutableStateFlow<AuthState>(AuthState.Unauthenticated)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    init {
        restoreSession()
    }

    private fun restoreSession() {
        val isLoggedIn = prefs.getBoolean(KEY_IS_LOGGED_IN, false)
        val isGuest = prefs.getBoolean(KEY_IS_GUEST, false)

        if (isLoggedIn) {
            val user = UserProfile(
                id = prefs.getString(KEY_USER_ID, UUID.randomUUID().toString()) ?: UUID.randomUUID().toString(),
                name = prefs.getString(KEY_USER_NAME, "Heritage Explorer") ?: "Heritage Explorer",
                email = prefs.getString(KEY_USER_EMAIL, "explorer@shilora.app") ?: "explorer@shilora.app",
                isGuest = false,
                joinedDate = prefs.getString(KEY_JOINED_DATE, "October 2026") ?: "October 2026"
            )
            _authState.value = AuthState.Authenticated(user)
        } else if (isGuest) {
            val guestUser = UserProfile(
                id = "guest_${UUID.randomUUID().toString().take(8)}",
                name = "Guest Explorer",
                email = "guest@shilora.local",
                isGuest = true,
                joinedDate = "Guest Session"
            )
            _authState.value = AuthState.Guest(guestUser)
        } else {
            _authState.value = AuthState.Unauthenticated
        }
    }

    fun login(email: String, password: String): AuthResult {
        if (email.isBlank() || !android.util.Patterns.EMAIL_ADDRESS.matcher(email.trim()).matches()) {
            return AuthResult.Error("Please enter a valid email address.")
        }
        if (password.length < 6) {
            return AuthResult.Error("Password must be at least 6 characters.")
        }

        val nameDerived = email.substringBefore("@")
            .replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }

        val user = UserProfile(
            id = UUID.randomUUID().toString(),
            name = nameDerived,
            email = email.trim(),
            isGuest = false,
            joinedDate = "October 2026"
        )

        prefs.edit()
            .putBoolean(KEY_IS_LOGGED_IN, true)
            .putBoolean(KEY_IS_GUEST, false)
            .putString(KEY_USER_ID, user.id)
            .putString(KEY_USER_NAME, user.name)
            .putString(KEY_USER_EMAIL, user.email)
            .putString(KEY_JOINED_DATE, user.joinedDate)
            .apply()

        _authState.value = AuthState.Authenticated(user)
        return AuthResult.Success(user)
    }

    fun signUp(name: String, email: String, password: String): AuthResult {
        if (name.isBlank()) {
            return AuthResult.Error("Please enter your full name.")
        }
        if (email.isBlank() || !android.util.Patterns.EMAIL_ADDRESS.matcher(email.trim()).matches()) {
            return AuthResult.Error("Please enter a valid email address.")
        }
        if (password.length < 6) {
            return AuthResult.Error("Password must be at least 6 characters.")
        }

        val user = UserProfile(
            id = UUID.randomUUID().toString(),
            name = name.trim(),
            email = email.trim(),
            isGuest = false,
            joinedDate = "October 2026"
        )

        prefs.edit()
            .putBoolean(KEY_IS_LOGGED_IN, true)
            .putBoolean(KEY_IS_GUEST, false)
            .putString(KEY_USER_ID, user.id)
            .putString(KEY_USER_NAME, user.name)
            .putString(KEY_USER_EMAIL, user.email)
            .putString(KEY_JOINED_DATE, user.joinedDate)
            .apply()

        _authState.value = AuthState.Authenticated(user)
        return AuthResult.Success(user)
    }

    fun continueAsGuest(): UserProfile {
        val guestUser = UserProfile(
            id = "guest_${UUID.randomUUID().toString().take(8)}",
            name = "Guest Explorer",
            email = "guest@shilora.local",
            isGuest = true,
            joinedDate = "Guest Session"
        )

        prefs.edit()
            .putBoolean(KEY_IS_LOGGED_IN, false)
            .putBoolean(KEY_IS_GUEST, true)
            .putString(KEY_USER_ID, guestUser.id)
            .putString(KEY_USER_NAME, guestUser.name)
            .putString(KEY_USER_EMAIL, guestUser.email)
            .putString(KEY_JOINED_DATE, guestUser.joinedDate)
            .apply()

        _authState.value = AuthState.Guest(guestUser)
        return guestUser
    }

    fun requestPasswordReset(email: String): AuthResult {
        if (email.isBlank() || !android.util.Patterns.EMAIL_ADDRESS.matcher(email.trim()).matches()) {
            return AuthResult.Error("Please enter a valid email address.")
        }
        return AuthResult.PendingVerification
    }

    fun logout() {
        prefs.edit().clear().apply()
        _authState.value = AuthState.Unauthenticated
    }

    fun getCurrentUser(): UserProfile? {
        return when (val state = _authState.value) {
            is AuthState.Authenticated -> state.user
            is AuthState.Guest -> state.user
            is AuthState.Unauthenticated -> null
        }
    }

    companion object {
        private const val KEY_IS_LOGGED_IN = "key_is_logged_in"
        private const val KEY_IS_GUEST = "key_is_guest"
        private const val KEY_USER_ID = "key_user_id"
        private const val KEY_USER_NAME = "key_user_name"
        private const val KEY_USER_EMAIL = "key_user_email"
        private const val KEY_JOINED_DATE = "key_joined_date"
    }
}
