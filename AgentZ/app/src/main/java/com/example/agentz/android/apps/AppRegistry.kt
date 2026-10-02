package com.example.agentz.android.apps

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager

data class RegisteredApp(
    val name: String,
    val packageName: String,
    val category: String,
    val capabilities: List<String>
)

class AppRegistry(private val context: Context) {

    private val apps = mapOf(
        "rapido" to RegisteredApp(
            name = "Rapido",
            packageName = "com.rapido.passenger",
            category = "Ride",
            capabilities = listOf("ride_booking", "auto", "bike", "cab")
        ),
        "uber" to RegisteredApp(
            name = "Uber",
            packageName = "com.ubercab",
            category = "Ride",
            capabilities = listOf("ride_booking", "cab", "auto")
        ),
        "ola" to RegisteredApp(
            name = "Ola",
            packageName = "com.olacabs",
            category = "Ride",
            capabilities = listOf("ride_booking", "cab", "auto")
        ),
        "whatsapp" to RegisteredApp(
            name = "WhatsApp",
            packageName = "com.whatsapp",
            category = "Communication",
            capabilities = listOf("send_message", "draft_message")
        ),
        "maps" to RegisteredApp(
            name = "Google Maps",
            packageName = "com.google.android.apps.maps",
            category = "Navigation",
            capabilities = listOf("navigate", "search_places")
        )
    )

    fun isAppInstalled(packageName: String): Boolean {
        return try {
            context.packageManager.getPackageInfo(packageName, 0)
            true
        } catch (e: PackageManager.NameNotFoundException) {
            false
        }
    }

    fun getApp(key: String): RegisteredApp? = apps[key.lowercase()]

    fun launchApp(packageName: String): Boolean {
        val launchIntent = context.packageManager.getLaunchIntentForPackage(packageName) ?: return false
        launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        return try {
            context.startActivity(launchIntent)
            true
        } catch (e: Exception) {
            false
        }
    }
}
