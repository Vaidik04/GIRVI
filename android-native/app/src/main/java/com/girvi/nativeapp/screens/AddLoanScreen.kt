package com.girvi.nativeapp.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.girvi.nativeapp.viewmodel.GirviViewModel

@Composable
fun AddLoanScreen(viewModel: GirviViewModel, padding: PaddingValues) {
    var customerId by remember { mutableStateOf("") }
    var amount by remember { mutableStateOf("") }
    var interestRate by remember { mutableStateOf("3") }
    var durationMonths by remember { mutableStateOf("3") }

    Column(modifier = Modifier.padding(padding).padding(16.dp)) {
        OutlinedTextField(value = customerId, onValueChange = { customerId = it }, label = { Text("Customer ID") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = amount, onValueChange = { amount = it }, label = { Text("Amount") }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp))
        OutlinedTextField(value = interestRate, onValueChange = { interestRate = it }, label = { Text("Interest %") }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp))
        OutlinedTextField(value = durationMonths, onValueChange = { durationMonths = it }, label = { Text("Duration (months)") }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp))

        Button(
            onClick = {
                val cid = customerId.toLongOrNull()
                val amt = amount.toDoubleOrNull()
                val rate = interestRate.toDoubleOrNull()
                val months = durationMonths.toIntOrNull()
                if (cid != null && amt != null && rate != null && months != null) {
                    viewModel.addLoan(cid, amt, rate, months)
                    amount = ""
                }
            },
            modifier = Modifier.padding(top = 12.dp)
        ) {
            Text("Create Loan")
        }
    }
}
