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
fun AddCustomerScreen(viewModel: GirviViewModel, padding: PaddingValues) {
    var name by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var address by remember { mutableStateOf("") }

    Column(modifier = Modifier.padding(padding).padding(16.dp)) {
        OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Customer Name") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = phone, onValueChange = { phone = it }, label = { Text("Phone") }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp))
        OutlinedTextField(value = email, onValueChange = { email = it }, label = { Text("Email") }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp))
        OutlinedTextField(value = address, onValueChange = { address = it }, label = { Text("Address") }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp))

        Button(
            onClick = {
                if (name.isNotBlank() && phone.isNotBlank()) {
                    viewModel.addCustomer(name, phone, email, address)
                    name = ""; phone = ""; email = ""; address = ""
                }
            },
            modifier = Modifier.padding(top = 12.dp)
        ) {
            Text("Save Customer")
        }
    }
}
