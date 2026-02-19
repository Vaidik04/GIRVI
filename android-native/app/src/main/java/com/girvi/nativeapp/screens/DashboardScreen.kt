package com.girvi.nativeapp.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.girvi.nativeapp.viewmodel.GirviViewModel

@Composable
fun DashboardScreen(viewModel: GirviViewModel, padding: PaddingValues) {
    val state by viewModel.dashboardState.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(padding)
            .padding(16.dp)
    ) {
        Text("Active Amount: ₹${"%.2f".format(state.totalActiveAmount)}", style = MaterialTheme.typography.titleMedium)
        Text("Recovered: ₹${"%.2f".format(state.totalRecovered)}", style = MaterialTheme.typography.titleMedium)
        Text("Total Customers: ${state.customers.size}")
        Text("Total Loans: ${state.loans.size}")

        LazyColumn(modifier = Modifier.padding(top = 12.dp)) {
            items(state.loans) { loan ->
                Card(modifier = Modifier.padding(vertical = 4.dp)) {
                    Column(modifier = Modifier.padding(10.dp)) {
                        Text("${loan.transactionNumber} • ${loan.status}")
                        Text("Amount: ₹${loan.amount}")
                        Text("Interest: ${loan.interestRate}% • ${loan.durationMonths} months")
                    }
                }
            }
        }
    }
}
