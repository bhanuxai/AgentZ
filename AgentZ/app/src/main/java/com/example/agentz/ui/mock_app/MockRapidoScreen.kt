package com.example.agentz.ui.mock_app

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.ElectricRickshaw
import androidx.compose.material.icons.filled.LocalTaxi
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.TwoWheeler
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.RadioButton
import androidx.compose.material3.RadioButtonDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.agentz.theme.NeonGreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MockRapidoScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var pickup by remember { mutableStateOf("Current location") }
    var destination by remember { mutableStateOf("Lovely Professional University (LPU)") }
    var selectedVehicle by remember { mutableStateOf("Auto") }
    var selectedPayment by remember { mutableStateOf("Cash") }
    var bookingConfirmed by remember { mutableStateOf(false) }

    val rapidoYellow = Color(0xFFF9A825)
    val rapidoDark = Color(0xFF1E2022)

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Rapido", fontWeight = FontWeight.Black, color = rapidoDark)
                        Spacer(modifier = Modifier.width(8.dp))
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = rapidoDark
                        ) {
                            Text(
                                "SANDBOX ENVIRONMENT",
                                color = rapidoYellow,
                                fontWeight = FontWeight.Bold,
                                fontSize = 9.sp,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = rapidoDark)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = rapidoYellow)
            )
        }
    ) { innerPadding ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            if (!bookingConfirmed) {
                // Simulated Map Graphic Banner
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f)),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(100.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Map, contentDescription = null, tint = rapidoYellow, modifier = Modifier.size(28.dp))
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(
                                    text = "Simulated Route Map",
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = "Live Accessibility target nodes mapped",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.outline
                                )
                            }
                        }
                    }
                }

                // Location inputs
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        OutlinedTextField(
                            value = pickup,
                            onValueChange = { pickup = it },
                            label = { Text("Pickup Location") },
                            modifier = Modifier.fillMaxWidth(),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = rapidoYellow,
                                focusedLabelColor = rapidoYellow
                            )
                        )
                        OutlinedTextField(
                            value = destination,
                            onValueChange = { destination = it },
                            label = { Text("Destination") },
                            modifier = Modifier.fillMaxWidth(),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = rapidoYellow,
                                focusedLabelColor = rapidoYellow
                            )
                        )
                    }
                }

                Text(
                    text = "SELECT RIDE CATEGORY",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color = rapidoYellow,
                    letterSpacing = 0.8.sp
                )

                // Ride options
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    RideTypeCard(
                        title = "Auto",
                        price = "₹183",
                        eta = "3 min away",
                        icon = Icons.Default.ElectricRickshaw,
                        selected = selectedVehicle == "Auto",
                        accentColor = rapidoYellow,
                        onSelect = { selectedVehicle = "Auto" },
                        modifier = Modifier.weight(1f)
                    )
                    RideTypeCard(
                        title = "Bike",
                        price = "₹95",
                        eta = "2 min away",
                        icon = Icons.Default.TwoWheeler,
                        selected = selectedVehicle == "Bike",
                        accentColor = rapidoYellow,
                        onSelect = { selectedVehicle = "Bike" },
                        modifier = Modifier.weight(1f)
                    )
                    RideTypeCard(
                        title = "Cab",
                        price = "₹320",
                        eta = "5 min away",
                        icon = Icons.Default.LocalTaxi,
                        selected = selectedVehicle == "Cab",
                        accentColor = rapidoYellow,
                        onSelect = { selectedVehicle = "Cab" },
                        modifier = Modifier.weight(1f)
                    )
                }

                // Payment method
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text("Payment Channel", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            RadioButton(
                                selected = selectedPayment == "Cash",
                                onClick = { selectedPayment = "Cash" },
                                colors = RadioButtonDefaults.colors(selectedColor = rapidoYellow)
                            )
                            Text("Cash on Delivery")
                            Spacer(modifier = Modifier.width(20.dp))
                            RadioButton(
                                selected = selectedPayment == "UPI",
                                onClick = { selectedPayment = "UPI" },
                                colors = RadioButtonDefaults.colors(selectedColor = rapidoYellow)
                            )
                            Text("UPI / Online")
                        }
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Bottom booking action
                Button(
                    onClick = { bookingConfirmed = true },
                    shape = RoundedCornerShape(14.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = rapidoYellow),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(52.dp)
                ) {
                    Text(
                        text = "Book $selectedVehicle • ${if (selectedVehicle == "Auto") "₹183" else if (selectedVehicle == "Bike") "₹95" else "₹320"}",
                        color = rapidoDark,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 16.sp
                    )
                }
            } else {
                // Booking Success screen
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .background(NeonGreen.copy(alpha = 0.15f), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = "Success",
                            tint = NeonGreen,
                            modifier = Modifier.size(48.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "Rapido $selectedVehicle Booked!",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Surface(
                        shape = RoundedCornerShape(16.dp),
                        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
                        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.Person, contentDescription = null, tint = rapidoYellow, modifier = Modifier.size(20.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Captain: Vikram Singh (Rating: 4.8 ★)", fontWeight = FontWeight.Bold)
                            }
                            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.3f))
                            Text("📍 Pickup: $pickup", style = MaterialTheme.typography.bodySmall)
                            Text("🏁 Drop: $destination", style = MaterialTheme.typography.bodySmall)
                            Text("💵 Fare: ${if (selectedVehicle == "Auto") "₹183" else "₹95"} ($selectedPayment)", fontWeight = FontWeight.Bold, color = NeonGreen)
                            Text("⏱️ ETA: Arriving at pickup in 3 mins", style = MaterialTheme.typography.bodySmall, color = rapidoYellow)
                        }
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = { bookingConfirmed = false },
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = rapidoYellow, contentColor = rapidoDark)
                    ) {
                        Text("Reset Mock Sandbox", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun RideTypeCard(
    title: String,
    price: String,
    eta: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    selected: Boolean,
    accentColor: Color,
    onSelect: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        shape = RoundedCornerShape(14.dp),
        color = if (selected) accentColor.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.35f),
        border = androidx.compose.foundation.BorderStroke(
            if (selected) 2.dp else 1.dp,
            if (selected) accentColor else MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f)
        ),
        modifier = modifier
            .clip(RoundedCornerShape(14.dp))
            .clickable { onSelect() }
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                icon,
                contentDescription = null,
                tint = if (selected) accentColor else MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Text(price, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = if (selected) accentColor else MaterialTheme.colorScheme.onSurface)
            Text(eta, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.outline, fontSize = 9.sp)
        }
    }
}
