package com.shilora.app.di

import android.content.Context
import androidx.room.Room
import com.google.gson.GsonBuilder
import com.shilora.app.data.api.ShiloraApiService
import com.shilora.app.data.local.ShiloraDatabase
import com.shilora.app.data.repository.AssistantRepository
import com.shilora.app.data.repository.HeritageRepository
import com.shilora.app.data.repository.LearningRepository
import com.shilora.app.data.repository.ScanRepository
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ServiceLocator {

    // Default backend address: 10.0.2.2 points to host machine from Android Emulator
    // Or local development IP for physical devices
    var backendBaseUrl = "http://10.0.2.2:5000/"

    private var database: ShiloraDatabase? = null
    private var apiService: ShiloraApiService? = null

    val heritageRepository by lazy { HeritageRepository() }
    val learningRepository by lazy { LearningRepository() }
    val assistantRepository by lazy { AssistantRepository() }

    private var _authRepository: com.shilora.app.data.repository.AuthRepository? = null
    val authRepository: com.shilora.app.data.repository.AuthRepository
        get() = _authRepository ?: throw IllegalStateException("ServiceLocator not initialized with Context")

    fun getAuthRepository(context: Context): com.shilora.app.data.repository.AuthRepository {
        initialize(context)
        return authRepository
    }

    private var _scanRepository: ScanRepository? = null
    val scanRepository: ScanRepository
        get() = _scanRepository ?: throw IllegalStateException("ServiceLocator not initialized with Context")

    fun getScanRepository(context: Context): ScanRepository {
        initialize(context)
        return scanRepository
    }

    fun setBackendUrl(newUrl: String, context: Context? = null) {
        val sanitizedUrl = if (newUrl.endsWith("/")) newUrl else "$newUrl/"
        backendBaseUrl = sanitizedUrl
        apiService = null
        _scanRepository = null
        if (context != null) {
            val prefs = context.getSharedPreferences("shilora_env_prefs", Context.MODE_PRIVATE)
            prefs.edit().putString("custom_backend_url", sanitizedUrl).apply()
            initialize(context)
        }
    }

    fun initialize(context: Context) {
        if (database == null) {
            database = Room.databaseBuilder(
                context.applicationContext,
                ShiloraDatabase::class.java,
                "shilora_epigraphy.db"
            ).build()
        }

        // Restore custom backend URL if set
        val prefs = context.getSharedPreferences("shilora_env_prefs", Context.MODE_PRIVATE)
        val savedUrl = prefs.getString("custom_backend_url", null)
        if (!savedUrl.isNullOrBlank()) {
            backendBaseUrl = savedUrl
        }

        if (apiService == null) {
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }

            val okHttpClient = OkHttpClient.Builder()
                .connectTimeout(90, TimeUnit.SECONDS)
                .readTimeout(180, TimeUnit.SECONDS)
                .writeTimeout(90, TimeUnit.SECONDS)
                .addInterceptor(loggingInterceptor)
                .build()

            val gson = GsonBuilder().setLenient().create()

            val retrofit = Retrofit.Builder()
                .baseUrl(backendBaseUrl)
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .build()

            apiService = retrofit.create(ShiloraApiService::class.java)
        }

        if (_authRepository == null) {
            _authRepository = com.shilora.app.data.repository.AuthRepository(context.applicationContext)
        }

        if (_scanRepository == null) {
            _scanRepository = ScanRepository(
                apiService = apiService!!,
                scanDao = database!!.scanDao()
            )
        }
    }
}
