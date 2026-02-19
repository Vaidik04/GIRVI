package com.girvi.nativeapp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.girvi.nativeapp.data.CustomerEntity
import com.girvi.nativeapp.data.GirviRepository
import com.girvi.nativeapp.data.LoanEntity
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

data class DashboardState(
    val customers: List<CustomerEntity> = emptyList(),
    val loans: List<LoanEntity> = emptyList(),
    val totalActiveAmount: Double = 0.0,
    val totalRecovered: Double = 0.0
)

class GirviViewModel(private val repository: GirviRepository) : ViewModel() {
    val dashboardState: StateFlow<DashboardState> = combine(
        repository.observeCustomers(),
        repository.observeLoans(),
        repository.observeTotalActiveLoanAmount(),
        repository.observeTotalRecoveredAmount()
    ) { customers, loans, activeTotal, recoveredTotal ->
        DashboardState(
            customers = customers,
            loans = loans,
            totalActiveAmount = activeTotal ?: 0.0,
            totalRecovered = recoveredTotal ?: 0.0
        )
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), DashboardState())

    fun addCustomer(name: String, phone: String, email: String, address: String) {
        viewModelScope.launch {
            repository.addCustomer(name, phone, email, address)
        }
    }

    fun addLoan(customerId: Long, amount: Double, interestRate: Double, durationMonths: Int) {
        viewModelScope.launch {
            repository.addLoan(customerId, amount, interestRate, durationMonths)
        }
    }

    fun addPayment(loanId: Long, amount: Double, paymentType: String) {
        viewModelScope.launch {
            repository.addPayment(loanId, amount, paymentType)
        }
    }
}

class GirviViewModelFactory(private val repository: GirviRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(GirviViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return GirviViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
