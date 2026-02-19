package com.girvi.nativeapp

import com.girvi.nativeapp.data.LoanCalculator
import kotlin.test.Test
import kotlin.test.assertEquals

class LoanCalculatorTest {
    @Test
    fun simpleInterest_calculatesExpectedValue() {
        val interest = LoanCalculator.simpleInterest(10000.0, 3.0, 2)
        assertEquals(600.0, interest)
    }

    @Test
    fun totalPayable_addsPrincipalAndInterest() {
        val payable = LoanCalculator.totalPayable(2000.0, 2.0, 5)
        assertEquals(2200.0, payable)
    }
}
