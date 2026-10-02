package com.example.agentz

import com.example.agentz.agent.planner.AgentPlanner
import com.example.agentz.data.models.RiskLevel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

class AgentPlannerTest {

    private lateinit var planner: AgentPlanner

    @Before
    fun setUp() {
        planner = AgentPlanner()
    }

    @Test
    fun testInitialRequestDetectsMissingVehicleAndPayment() {
        val result = planner.plan("Book me a Rapido from my current location to LPU.")

        assertEquals("BOOK_RIDE", result.intent)
        assertEquals("Current location", result.entities["pickup"])
        assertTrue(result.entities["destination"]!!.contains("LPU"))
        assertTrue("Should detect vehicle is missing", result.missingParameters.contains("vehicle"))
        assertNotNull(result.questionToUser)
        assertTrue(result.questionToUser!!.contains("Which ride do you want?"))
        assertEquals(listOf("Auto", "Bike", "Cab"), result.suggestedOptions)
    }

    @Test
    fun testMultiTurnClarificationFlow() {
        // Turn 1: Initial request
        val turn1 = planner.plan("Book me a Rapido from my current location to LPU.")
        assertTrue(turn1.missingParameters.contains("vehicle"))

        // Turn 2: User specifies "Auto"
        val turn2 = planner.plan("Auto.")
        assertEquals("Auto", turn2.entities["vehicle"])
        assertTrue("Should now ask for payment method", turn2.missingParameters.contains("payment"))
        assertNotNull(turn2.questionToUser)
        assertTrue(turn2.questionToUser!!.contains("preferred payment method"))
        assertEquals(listOf("Cash", "UPI"), turn2.suggestedOptions)

        // Turn 3: User specifies "Cash"
        val turn3 = planner.plan("Cash.")
        assertEquals("Cash", turn3.entities["payment"])
        assertTrue("No missing parameters should remain", turn3.missingParameters.isEmpty())
        assertTrue("Steps should be generated", turn3.steps.isNotEmpty())

        // Verify steps structure
        assertEquals(8, turn3.steps.size)
        assertEquals("Understanding request", turn3.steps[0].title)
        assertEquals("Current location obtained", turn3.steps[1].title)
        assertEquals("Opening Rapido", turn3.steps[2].title)
        assertEquals("Entering pickup location", turn3.steps[3].title)
        assertEquals("Entering destination", turn3.steps[4].title)
        assertEquals("Selecting Auto", turn3.steps[5].title)
        assertEquals("Checking fare", turn3.steps[6].title)
        assertEquals("Confirming booking", turn3.steps[7].title)

        // Verify high-risk step classification
        assertEquals(RiskLevel.HIGH, turn3.steps[7].riskLevel)

        // Verify Confirmation Card
        val conf = turn3.confirmationCard
        assertNotNull(conf)
        assertEquals("Rapido", conf!!.provider)
        assertEquals("Auto", conf.vehicle)
        assertEquals("₹183", conf.fare)
        assertEquals("Cash", conf.paymentMethod)
        assertEquals(RiskLevel.HIGH, conf.riskLevel)
    }

    @Test
    fun testMemoryPreferenceBypassesRedundantQuestions() {
        val memories = mapOf(
            "Preferred ride" to "Auto",
            "Preferred payment" to "Cash"
        )
        val result = planner.plan("Book me a Rapido from my current location to LPU.", memories)

        // Since vehicle and payment are in memory, no questions should be needed!
        assertTrue(result.missingParameters.isEmpty())
        assertEquals("Auto", result.entities["vehicle"])
        assertEquals("Cash", result.entities["payment"])
        assertTrue(result.steps.isNotEmpty())
    }

    @Test
    fun testSendMessageIntent() {
        val result = planner.plan("Send Rahul a message saying I'll reach in 20 minutes.")
        assertEquals("SEND_MESSAGE", result.intent)
        assertEquals("Rahul", result.entities["recipient"])
        assertTrue(result.steps.isNotEmpty())
        assertEquals(RiskLevel.HIGH, result.steps.last().riskLevel)
    }

    @Test
    fun testNavigationIntent() {
        val result = planner.plan("Navigate me to Vijayawada airport.")
        assertEquals("NAVIGATE", result.intent)
        assertTrue(result.entities["destination"]!!.contains("Vijayawada"))
        assertTrue(result.steps.isNotEmpty())
    }
}
