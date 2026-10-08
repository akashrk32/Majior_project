package com.shilora.app

import android.app.Application
import com.shilora.app.di.ServiceLocator

class ShiloraApp : Application() {

    override fun onCreate() {
        super.onCreate()
        // Initialize ServiceLocator and Room database
        ServiceLocator.initialize(this)
    }
}
