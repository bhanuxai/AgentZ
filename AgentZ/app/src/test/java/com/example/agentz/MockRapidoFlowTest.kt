package com.example.agentz

import com.example.agentz.android.apps.MockRapidoAdapter
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

class MockRapidoFlowTest {

    private lateinit var mockRapido: MockRapidoAdapter

    @Before
    fun setUp() {
        mockRapido = MockRapidoAdapter()
    }

    @Test
    fun testEndToEndRideBookingFlow() = runBlocking {
        // 1. Open Provider
        assertTrue("Provider should open", mockRapido.openProvider())

        // 2. Set Pickup
        assertTrue("Pickup set", mockRapido.setPickup("Current location (Phagwara)"))

        // 3. Set Destination
        assertTrue("Destination set", mockRapido.setDestination("Lovely Professional University (LPU)"))

        // 4. Select Vehicle Auto
        assertTrue("Vehicle selected", mockRapido.selectVehicle("Auto"))

        // 5. Select Payment Cash
        assertTrue("Payment selected", mockRapido.selectPayment("Cash"))

        // 6. Read Fare
        val fare = mockRapido.readFare()
        assertEquals("₹183", fare)

        // 7. Prepare Booking
        assertTrue("Booking prepared", mockRapido.prepareBooking())

        // 8. Confirm Booking (Final consequential action)
        assertTrue("Booking confirmed", mockRapido.confirmBooking())

        // 9. Verify Booking
        assertTrue("Booking verified", mockRapido.verifyBooking())
    }

    @Test
    fun testFareCalculationPerVehicleType() = runBlocking {
        mockRapido.selectVehicle("Bike")
        assertEquals("₹95", mockRapido.readFare())

        mockRapido.selectVehicle("Auto")
        assertEquals("₹183", mockRapido.readFare())

        mockRapido.selectVehicle("Cab")
        assertEquals("₹320", mockRapido.readFare())
    }
}
