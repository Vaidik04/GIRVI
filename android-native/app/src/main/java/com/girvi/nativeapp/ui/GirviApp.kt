package com.girvi.nativeapp.ui

import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.girvi.nativeapp.screens.AddCustomerScreen
import com.girvi.nativeapp.screens.AddLoanScreen
import com.girvi.nativeapp.screens.DashboardScreen
import com.girvi.nativeapp.viewmodel.GirviViewModel

private data class BottomRoute(val route: String, val label: String)

@Composable
fun GirviApp(viewModel: GirviViewModel) {
    val routes = listOf(
        BottomRoute("dashboard", "Dashboard"),
        BottomRoute("customer", "Customer"),
        BottomRoute("loan", "Loan")
    )
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val destination = navBackStackEntry?.destination
                routes.forEach { screen ->
                    NavigationBarItem(
                        selected = destination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Text(screen.label.take(1)) },
                        label = { Text(screen.label) }
                    )
                }
            }
        }
    ) { padding ->
        NavHost(navController = navController, startDestination = "dashboard") {
            composable("dashboard") { DashboardScreen(viewModel, padding) }
            composable("customer") { AddCustomerScreen(viewModel, padding) }
            composable("loan") { AddLoanScreen(viewModel, padding) }
        }
    }
}
