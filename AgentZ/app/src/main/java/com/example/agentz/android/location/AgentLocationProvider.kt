package com.example.agentz.android.location

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Geocoder
import android.location.Location
import android.location.LocationManager
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.Locale

class AgentLocationProvider(private val context: Context) {

    data class LocationResult(
        val latitude: Double,
        val longitude: Double,
        val addressName: String,
        val isMockOrFallback: Boolean
    )

    fun hasLocationPermission(): Boolean {
        val fine = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION)
        val coarse = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION)
        return fine == PackageManager.PERMISSION_GRANTED || coarse == PackageManager.PERMISSION_GRANTED
    }

    suspend fun getCurrentLocation(): LocationResult = withContext(Dispatchers.IO) {
        if (!hasLocationPermission()) {
            return@withContext LocationResult(
                latitude = 31.2536,
                longitude = 75.7037,
                addressName = "Current location (Phagwara, Punjab)",
                isMockOrFallback = true
            )
        }

        try {
            val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as? LocationManager
            var lastKnownLocation: Location? = null

            if (locationManager != null) {
                val providers = locationManager.getProviders(true)
                for (provider in providers) {
                    val loc = try { locationManager.getLastKnownLocation(provider) } catch (e: SecurityException) { null }
                    if (loc != null && (lastKnownLocation == null || loc.accuracy < lastKnownLocation.accuracy)) {
                        lastKnownLocation = loc
                    }
                }
            }

            if (lastKnownLocation != null) {
                val lat = lastKnownLocation.latitude
                val lon = lastKnownLocation.longitude
                val address = reverseGeocode(lat, lon)
                return@withContext LocationResult(lat, lon, address, false)
            }
        } catch (e: Exception) {
            // Log fallback
        }

        // Default location near LPU Campus
        LocationResult(
            latitude = 31.2536,
            longitude = 75.7037,
            addressName = "Current location (Near LPU Main Gate)",
            isMockOrFallback = true
        )
    }

    private fun reverseGeocode(latitude: Double, longitude: Double): String {
        return try {
            val geocoder = Geocoder(context, Locale.getDefault())
            val addresses = geocoder.getFromLocation(latitude, longitude, 1)
            if (!addresses.isNullOrEmpty()) {
                val addr = addresses[0]
                val feature = addr.featureName ?: addr.thoroughfare ?: addr.locality ?: "Current location"
                val city = addr.locality ?: addr.subAdminArea ?: ""
                if (city.isNotBlank() && !feature.contains(city)) "$feature, $city" else feature
            } else {
                "Current location ($latitude, $longitude)"
            }
        } catch (e: Exception) {
            "Current location"
        }
    }
}
