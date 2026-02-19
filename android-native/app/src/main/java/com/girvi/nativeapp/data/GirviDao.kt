package com.girvi.nativeapp.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface GirviDao {
    @Insert
    suspend fun insertCustomer(customer: CustomerEntity): Long

    @Insert
    suspend fun insertLoan(loan: LoanEntity): Long

    @Insert
    suspend fun insertPayment(payment: PaymentEntity)

    @Query("SELECT * FROM customers ORDER BY id DESC")
    fun observeCustomers(): Flow<List<CustomerEntity>>

    @Query("SELECT * FROM loans ORDER BY id DESC")
    fun observeLoans(): Flow<List<LoanEntity>>

    @Query("SELECT SUM(amount) FROM loans WHERE status = 'active'")
    fun observeTotalActiveLoanAmount(): Flow<Double?>

    @Query("SELECT SUM(amount) FROM payments")
    fun observeTotalRecoveredAmount(): Flow<Double?>
}
