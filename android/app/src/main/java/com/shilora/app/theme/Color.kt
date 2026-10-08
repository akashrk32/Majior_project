package com.shilora.app.theme

import androidx.compose.ui.graphics.Color

// ============================================================
// SHILORA BRAND COLOR SYSTEM — ABSOLUTELY LOCKED
// Strict 60 : 30 : 10 Brand Ratio
// ============================================================

// 1. SAGE GREEN (#9CAF88) — 60%
// Primary surfaces, screen background identity, hero sections
val SageGreen = Color(0xFF9CAF88)

// 2. CONCRETE GREY (#A7A7A7) — 30%
// Cards, panels, input areas, supporting surfaces
val ConcreteGrey = Color(0xFFA7A7A7)

// 3. BURNT AMBER (#CC5500) — 10%
// Primary CTA, scan action, active highlights, badges, progress
val BurntAmber = Color(0xFFCC5500)

// ============================================================
// ACCESSIBILITY NEUTRALS (Used ONLY for readable text contrast)
// ============================================================
val NeutralBlack = Color(0xFF1A1C19)
val NeutralWhite = Color(0xFFFFFFFF)

// ============================================================
// DERIVED BRAND HIERARCHY TOKENS (Composed strictly via alphas
// of the 3 locked brand colors and accessibility neutrals)
// ============================================================
val SageGreenSurface = SageGreen.copy(alpha = 0.15f)
val SageGreenLight = SageGreen.copy(alpha = 0.25f)
val SageGreenDark = SageGreen

val ConcreteGreyLight = ConcreteGrey.copy(alpha = 0.25f)
val ConcreteGreyDark = ConcreteGrey
val StoneCardSurface = ConcreteGrey.copy(alpha = 0.12f)
val StoneBorder = ConcreteGrey.copy(alpha = 0.35f)

val BurntAmberLight = BurntAmber
val BurntAmberDark = BurntAmber
val BurntAmberGlow = BurntAmber.copy(alpha = 0.20f)

val NeutralDarkGrey = NeutralBlack.copy(alpha = 0.75f)
val NeutralMediumGrey = NeutralBlack.copy(alpha = 0.60f)

// Epigraphical Trust Tokens (strictly mapped to Sage Green & Burnt Amber)
val ConfidenceHigh = SageGreen
val ConfidenceModerate = BurntAmber
val ConfidenceLow = BurntAmber
