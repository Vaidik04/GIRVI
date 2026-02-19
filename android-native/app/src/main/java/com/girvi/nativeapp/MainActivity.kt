package com.girvi.nativeapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import com.girvi.nativeapp.data.GirviDatabase
import com.girvi.nativeapp.data.GirviRepository
import com.girvi.nativeapp.ui.GirviApp
import com.girvi.nativeapp.viewmodel.GirviViewModel
import com.girvi.nativeapp.viewmodel.GirviViewModelFactory

class MainActivity : ComponentActivity() {
    private val viewModel: GirviViewModel by viewModels {
        GirviViewModelFactory(GirviRepository(GirviDatabase.get(applicationContext).girviDao()))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            Surface(color = MaterialTheme.colorScheme.background) {
                GirviApp(viewModel)
            }
        }
    }
}
