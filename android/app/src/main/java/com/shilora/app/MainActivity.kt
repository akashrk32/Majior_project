package com.shilora.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.shilora.app.theme.SageGreenSurface
import com.shilora.app.theme.ShiloraTheme
import com.shilora.app.ui.navigation.ShiloraAppNavigation

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ShiloraTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = SageGreenSurface
                ) {
                    ShiloraAppNavigation()
                }
            }
        }
    }
}
