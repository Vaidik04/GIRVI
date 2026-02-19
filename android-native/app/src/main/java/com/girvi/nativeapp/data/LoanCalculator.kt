package com.girvi.nativeapp.data

import kotlin.math.round

object LoanCalculator {
    fun simpleInterest(principal: Double, monthlyRatePercent: Double, months: Int): Double {
        val interest = principal * (monthlyRatePercent / 100.0) * months
        return round(interest * 100) / 100
    }

    fun totalPayable(principal: Double, monthlyRatePercent: Double, months: Int): Double {
        return round((principal + simpleInterest(principal, monthlyRatePercent, months)) * 100) / 100
    }
}
