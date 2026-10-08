package com.shilora.app.data.api

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface ShiloraApiService {

    @POST("/api/shilora/analyze")
    suspend fun analyzeInscriptionJson(
        @Body request: ShiloraAnalyzeRequest
    ): Response<ShiloraAnalyzeResponse>

    @Multipart
    @POST("/api/shilora/analyze")
    suspend fun analyzeInscriptionMultipart(
        @Part image: MultipartBody.Part,
        @Part("inscription_name") name: RequestBody
    ): Response<ShiloraAnalyzeResponse>
}
