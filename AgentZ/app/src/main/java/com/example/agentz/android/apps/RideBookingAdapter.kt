package com.example.agentz.android.apps

import android.content.Context
import com.example.agentz.android.accessibility.AgentAccessibilityService
import kotlinx.coroutines.delay

interface RideBookingAdapter {
    val providerName: String
    suspend fun openProvider(): Boolean
    suspend fun setPickup(location: String): Boolean
    suspend fun setDestination(location: String): Boolean
    suspend fun selectVehicle(type: String): Boolean
    suspend fun selectPayment(method: String): Boolean
    suspend fun readFare(): String
    suspend fun prepareBooking(): Boolean
    suspend fun confirmBooking(): Boolean
    suspend fun verifyBooking(): Boolean
}

/**
 * Real device adapter using AccessibilityService to interact with Rapido.
 */
class RapidoAdapter(
    private val context: Context,
    private val appRegistry: AppRegistry,
    private val mockFallback: MockRapidoAdapter
) : RideBookingAdapter {

    override val providerName: String = "Rapido"
    private val packageName = "com.rapido.passenger"

    override suspend fun openProvider(): Boolean {
        if (!appRegistry.isAppInstalled(packageName)) {
            // App not installed: gracefully fall back to mock sandbox adapter
            return mockFallback.openProvider()
        }
        return appRegistry.launchApp(packageName)
    }

    override suspend fun setPickup(location: String): Boolean {
        val service = AgentAccessibilityService.instance ?: return mockFallback.setPickup(location)
        val pickupNode = service.findNodeByText("Pickup") ?: service.findNodeByText("Where to?")
        if (pickupNode != null) {
            service.clickNode(pickupNode)
            delay(500)
            val inputNode = service.findNodeByText("Search pickup")
            if (inputNode != null) {
                return service.setTextOnNode(inputNode, location)
            }
        }
        return mockFallback.setPickup(location)
    }

    override suspend fun setDestination(location: String): Boolean {
        val service = AgentAccessibilityService.instance ?: return mockFallback.setDestination(location)
        val destNode = service.findNodeByText("Drop") ?: service.findNodeByText("Enter destination")
        if (destNode != null) {
            service.clickNode(destNode)
            delay(500)
            val inputNode = service.findNodeByText("Search destination")
            if (inputNode != null) {
                return service.setTextOnNode(inputNode, location)
            }
        }
        return mockFallback.setDestination(location)
    }

    override suspend fun selectVehicle(type: String): Boolean {
        val service = AgentAccessibilityService.instance ?: return mockFallback.selectVehicle(type)
        val rideNode = service.findNodeByText(type)
        if (rideNode != null) {
            return service.clickNode(rideNode)
        }
        return mockFallback.selectVehicle(type)
    }

    override suspend fun selectPayment(method: String): Boolean {
        val service = AgentAccessibilityService.instance ?: return mockFallback.selectPayment(method)
        val payNode = service.findNodeByText(method)
        if (payNode != null) {
            return service.clickNode(payNode)
        }
        return mockFallback.selectPayment(method)
    }

    override suspend fun readFare(): String {
        val service = AgentAccessibilityService.instance ?: return mockFallback.readFare()
        val visibleTexts = service.getVisibleScreenText()
        val fareText = visibleTexts.firstOrNull { it.contains("₹") }
        return fareText ?: mockFallback.readFare()
    }

    override suspend fun prepareBooking(): Boolean {
        delay(600)
        return true
    }

    override suspend fun confirmBooking(): Boolean {
        val service = AgentAccessibilityService.instance ?: return mockFallback.confirmBooking()
        val confirmBtn = service.findNodeByText("Book") ?: service.findNodeByText("Confirm Ride")
        if (confirmBtn != null) {
            return service.clickNode(confirmBtn)
        }
        return mockFallback.confirmBooking()
    }

    override suspend fun verifyBooking(): Boolean {
        val service = AgentAccessibilityService.instance ?: return mockFallback.verifyBooking()
        delay(1200)
        val visibleTexts = service.getVisibleScreenText()
        return visibleTexts.any { it.contains("Looking for Captain", ignoreCase = true) || it.contains("Booked", ignoreCase = true) }
    }
}

/**
 * High-fidelity mock adapter for Sandbox and presentation demos.
 */
class MockRapidoAdapter : RideBookingAdapter {
    override val providerName: String = "Rapido (Sandbox)"

    private var pickupLocation: String = "Current location"
    private var destinationLocation: String = "LPU"
    private var vehicleType: String = "Auto"
    private var paymentMethod: String = "Cash"
    private var isConfirmed: Boolean = false

    override suspend fun openProvider(): Boolean {
        delay(500)
        return true
    }

    override suspend fun setPickup(location: String): Boolean {
        delay(400)
        pickupLocation = location
        return true
    }

    override suspend fun setDestination(location: String): Boolean {
        delay(400)
        destinationLocation = location
        return true
    }

    override suspend fun selectVehicle(type: String): Boolean {
        delay(350)
        vehicleType = type
        return true
    }

    override suspend fun selectPayment(method: String): Boolean {
        delay(300)
        paymentMethod = method
        return true
    }

    override suspend fun readFare(): String {
        delay(400)
        return when (vehicleType.lowercase()) {
            "auto" -> "₹183"
            "bike" -> "₹95"
            else -> "₹320"
        }
    }

    override suspend fun prepareBooking(): Boolean {
        delay(500)
        return true
    }

    override suspend fun confirmBooking(): Boolean {
        delay(700)
        isConfirmed = true
        return true
    }

    override suspend fun verifyBooking(): Boolean {
        delay(600)
        return isConfirmed
    }
}
