package com.girvi.nativeapp.data

import kotlinx.coroutines.flow.Flow

class GirviRepository(private val dao: GirviDao) {
    fun observeCustomers() = dao.observeCustomers()
    fun observeLoans() = dao.observeLoans()
    fun observeTotalActiveLoanAmount(): Flow<Double?> = dao.observeTotalActiveLoanAmount()
    fun observeTotalRecoveredAmount(): Flow<Double?> = dao.observeTotalRecoveredAmount()

    suspend fun addCustomer(name: String, phone: String, email: String, address: String): Long {
        return dao.insertCustomer(
            CustomerEntity(name = name, phone = phone, email = email, address = address)
        )
    }

    suspend fun addLoan(
        customerId: Long,
        amount: Double,
        interestRate: Double,
        durationMonths: Int
    ) {
        val loanCode = "TXN-${System.currentTimeMillis().toString().takeLast(6)}"
        dao.insertLoan(
            LoanEntity(
                transactionNumber = loanCode,
                customerId = customerId,
                amount = amount,
                interestRate = interestRate,
                durationMonths = durationMonths
            )
        )
    }

    suspend fun addPayment(loanId: Long, amount: Double, paymentType: String) {
        dao.insertPayment(PaymentEntity(loanId = loanId, amount = amount, paymentType = paymentType))
    }
}
