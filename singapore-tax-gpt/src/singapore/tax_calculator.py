"""Singapore Tax Calculator Module."""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaxCalculationResult:
    """Result of tax calculation."""
    gross_income: Decimal
    tax_reliefs: Decimal
    chargeable_income: Decimal
    tax_amount: Decimal
    effective_rate: Decimal
    marginal_rate: Decimal
    breakdown: List[Dict[str, Any]]
    reliefs_applied: List[Dict[str, Any]]
    year_of_assessment: str


class SingaporeTaxCalculator:
    """Calculator for Singapore tax computations."""
    
    def __init__(self, year_of_assessment: int = None):
        """
        Initialize tax calculator.
        
        Args:
            year_of_assessment: Tax year (defaults to current year)
        """
        self.year_of_assessment = year_of_assessment or datetime.now().year
        self._initialize_tax_rates()
        self._initialize_reliefs()
        self._initialize_cpf_rates()
    
    def _initialize_tax_rates(self):
        """Initialize tax rate tables."""
        # Tax rates for YA 2024 (residents)
        self.resident_tax_rates_2024 = [
            (20000, Decimal('0')),      # First $20,000 at 0%
            (10000, Decimal('0.02')),    # Next $10,000 at 2%
            (10000, Decimal('0.035')),   # Next $10,000 at 3.5%
            (40000, Decimal('0.07')),    # Next $40,000 at 7%
            (40000, Decimal('0.115')),   # Next $40,000 at 11.5%
            (40000, Decimal('0.15')),    # Next $40,000 at 15%
            (40000, Decimal('0.18')),    # Next $40,000 at 18%
            (40000, Decimal('0.19')),    # Next $40,000 at 19%
            (40000, Decimal('0.195')),   # Next $40,000 at 19.5%
            (40000, Decimal('0.20')),    # Next $40,000 at 20%
            (40000, Decimal('0.22')),    # Next $40,000 at 22%
            (float('inf'), Decimal('0.24'))  # Above $1,000,000 at 24%
        ]
        
        # Non-resident flat rate
        self.non_resident_rate = Decimal('0.15')  # Employment income
        self.non_resident_rate_other = Decimal('0.22')  # Director fees, etc.
        
        # Corporate tax rate
        self.corporate_tax_rate = Decimal('0.17')
        
        # GST rates
        self.gst_rates = {
            2023: Decimal('0.08'),
            2024: Decimal('0.09'),
            2025: Decimal('0.09')
        }
        
        # Property tax rates (owner-occupied)
        self.property_tax_owner_occupied = [
            (8000, Decimal('0')),        # First $8,000 at 0%
            (47000, Decimal('0.04')),    # Next $47,000 at 4%
            (15000, Decimal('0.05')),    # Next $15,000 at 5%
            (15000, Decimal('0.07')),    # Next $15,000 at 7%
            (15000, Decimal('0.10')),    # Next $15,000 at 10%
            (15000, Decimal('0.14')),    # Next $15,000 at 14%
            (15000, Decimal('0.18')),    # Next $15,000 at 18%
            (float('inf'), Decimal('0.23'))  # Above $130,000 at 23%
        ]
    
    def _initialize_reliefs(self):
        """Initialize tax relief amounts."""
        self.tax_reliefs = {
            'earned_income': {
                'below_55': 1000,
                '55_to_59': 6000,
                '60_and_above': 8000
            },
            'spouse': 2000,
            'qualifying_child': 4000,
            'handicapped_child': 7500,
            'working_mother_child': {
                'first': 0.15,  # 15% of earned income
                'second': 0.20,  # 20% of earned income
                'third_plus': 0.25  # 25% of earned income
            },
            'parent': 9000,
            'handicapped_parent': 14000,
            'grandparent_caregiver': 3000,
            'cpf_cash_top_up': 8000,  # Max for self + family
            'cpf_voluntary': 37740,  # Max for YA 2024
            'course_fees': 5500,
            'foreign_maid_levy': 7200,  # Twice the levy amount
            'life_insurance': 5000,  # Combined with CPF
            'srs': 15300,  # Max for YA 2024
            'nsr_self': 5000,
            'nsr_employer': 5000
        }
        
        # Personal relief cap
        self.personal_relief_cap = 80000
    
    def _initialize_cpf_rates(self):
        """Initialize CPF contribution rates."""
        # CPF rates for YA 2024 (employee + employer)
        self.cpf_rates = {
            'below_55': {
                'employee': Decimal('0.20'),
                'employer': Decimal('0.17'),
                'total': Decimal('0.37')
            },
            '55_to_60': {
                'employee': Decimal('0.155'),
                'employer': Decimal('0.15'),
                'total': Decimal('0.305')
            },
            '60_to_65': {
                'employee': Decimal('0.105'),
                'employer': Decimal('0.115'),
                'total': Decimal('0.22')
            },
            '65_to_70': {
                'employee': Decimal('0.075'),
                'employer': Decimal('0.085'),
                'total': Decimal('0.16')
            },
            'above_70': {
                'employee': Decimal('0.05'),
                'employer': Decimal('0.075'),
                'total': Decimal('0.125')
            }
        }
        
        # CPF salary ceiling
        self.cpf_ordinary_wage_ceiling = 6000  # Monthly
        self.cpf_additional_wage_ceiling = 102000  # Annual
    
    def calculate_income_tax(self,
                            gross_income: float,
                            reliefs: Dict[str, float] = None,
                            is_resident: bool = True,
                            age: int = 30) -> TaxCalculationResult:
        """
        Calculate income tax for an individual.
        
        Args:
            gross_income: Annual gross income
            reliefs: Dictionary of reliefs to apply
            is_resident: Whether taxpayer is Singapore tax resident
            age: Age of taxpayer (for earned income relief)
            
        Returns:
            TaxCalculationResult with detailed breakdown
        """
        gross_income_dec = Decimal(str(gross_income))
        
        # Apply reliefs
        total_reliefs, reliefs_applied = self._calculate_reliefs(
            gross_income_dec, reliefs or {}, age
        )
        
        # Calculate chargeable income
        chargeable_income = max(gross_income_dec - total_reliefs, Decimal('0'))
        
        # Calculate tax
        if is_resident:
            tax_amount, breakdown, marginal_rate = self._calculate_resident_tax(
                chargeable_income
            )
        else:
            tax_amount, breakdown, marginal_rate = self._calculate_non_resident_tax(
                chargeable_income
            )
        
        # Calculate effective rate
        if gross_income_dec > 0:
            effective_rate = (tax_amount / gross_income_dec * 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:
            effective_rate = Decimal('0')
        
        return TaxCalculationResult(
            gross_income=gross_income_dec,
            tax_reliefs=total_reliefs,
            chargeable_income=chargeable_income,
            tax_amount=tax_amount,
            effective_rate=effective_rate,
            marginal_rate=marginal_rate,
            breakdown=breakdown,
            reliefs_applied=reliefs_applied,
            year_of_assessment=str(self.year_of_assessment)
        )
    
    def _calculate_reliefs(self, 
                          gross_income: Decimal,
                          reliefs: Dict[str, float],
                          age: int) -> Tuple[Decimal, List[Dict[str, Any]]]:
        """Calculate total tax reliefs."""
        total_relief = Decimal('0')
        reliefs_applied = []
        
        # Earned income relief (automatic)
        if age < 55:
            earned_relief = self.tax_reliefs['earned_income']['below_55']
        elif age < 60:
            earned_relief = self.tax_reliefs['earned_income']['55_to_59']
        else:
            earned_relief = self.tax_reliefs['earned_income']['60_and_above']
        
        total_relief += Decimal(str(earned_relief))
        reliefs_applied.append({
            'type': 'Earned Income Relief',
            'amount': earned_relief,
            'automatic': True
        })
        
        # Apply other reliefs
        for relief_type, amount in reliefs.items():
            if relief_type in self.tax_reliefs:
                relief_amount = Decimal(str(amount))
                
                # Check if it's percentage-based (working mother)
                if relief_type == 'working_mother_child':
                    # Calculate based on earned income
                    relief_amount = min(
                        relief_amount,
                        gross_income * Decimal('0.25')  # Max 25%
                    )
                
                total_relief += relief_amount
                reliefs_applied.append({
                    'type': relief_type.replace('_', ' ').title(),
                    'amount': float(relief_amount),
                    'automatic': False
                })
        
        # Apply personal relief cap
        if total_relief > self.personal_relief_cap:
            total_relief = Decimal(str(self.personal_relief_cap))
            reliefs_applied.append({
                'type': 'Personal Relief Cap Applied',
                'amount': self.personal_relief_cap,
                'automatic': True
            })
        
        return total_relief, reliefs_applied
    
    def _calculate_resident_tax(self, 
                               chargeable_income: Decimal) -> Tuple[Decimal, List, Decimal]:
        """Calculate tax for resident."""
        tax_amount = Decimal('0')
        breakdown = []
        remaining_income = chargeable_income
        
        for bracket_amount, rate in self.resident_tax_rates_2024:
            if remaining_income <= 0:
                break
            
            if bracket_amount == float('inf'):
                # Final bracket
                taxable_in_bracket = remaining_income
            else:
                taxable_in_bracket = min(remaining_income, Decimal(str(bracket_amount)))
            
            bracket_tax = taxable_in_bracket * rate
            tax_amount += bracket_tax
            
            if bracket_tax > 0:
                breakdown.append({
                    'income_range': f"${taxable_in_bracket:,.0f}",
                    'rate': f"{rate * 100:.1f}%",
                    'tax': float(bracket_tax)
                })
            
            remaining_income -= taxable_in_bracket
            marginal_rate = rate
        
        # Round to nearest dollar
        tax_amount = tax_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        
        return tax_amount, breakdown, marginal_rate * 100
    
    def _calculate_non_resident_tax(self, 
                                   chargeable_income: Decimal) -> Tuple[Decimal, List, Decimal]:
        """Calculate tax for non-resident."""
        # Flat 15% on employment income or progressive rates, whichever is higher
        flat_tax = chargeable_income * self.non_resident_rate
        progressive_tax, _, _ = self._calculate_resident_tax(chargeable_income)
        
        if flat_tax > progressive_tax:
            tax_amount = flat_tax
            rate_used = self.non_resident_rate
            method = "Flat Rate"
        else:
            tax_amount = progressive_tax
            # Calculate effective rate
            rate_used = tax_amount / chargeable_income if chargeable_income > 0 else Decimal('0')
            method = "Progressive Rate"
        
        breakdown = [{
            'method': method,
            'income': float(chargeable_income),
            'rate': f"{rate_used * 100:.1f}%",
            'tax': float(tax_amount)
        }]
        
        return tax_amount, breakdown, rate_used * 100
    
    def calculate_gst(self, 
                     amount: float,
                     year: int = None,
                     is_inclusive: bool = False) -> Dict[str, float]:
        """
        Calculate GST amount.
        
        Args:
            amount: Base amount
            year: Year for GST rate (defaults to current)
            is_inclusive: Whether amount includes GST
            
        Returns:
            Dictionary with base amount, GST, and total
        """
        year = year or self.year_of_assessment
        gst_rate = self.gst_rates.get(year, Decimal('0.09'))
        
        amount_dec = Decimal(str(amount))
        
        if is_inclusive:
            # Amount includes GST, extract base amount
            base_amount = amount_dec / (1 + gst_rate)
            gst_amount = amount_dec - base_amount
            total = amount_dec
        else:
            # Amount excludes GST
            base_amount = amount_dec
            gst_amount = amount_dec * gst_rate
            total = base_amount + gst_amount
        
        return {
            'base_amount': float(base_amount.quantize(Decimal('0.01'))),
            'gst_amount': float(gst_amount.quantize(Decimal('0.01'))),
            'total': float(total.quantize(Decimal('0.01'))),
            'gst_rate': float(gst_rate * 100)
        }
    
    def calculate_property_tax(self, 
                              annual_value: float,
                              is_owner_occupied: bool = True) -> Dict[str, Any]:
        """
        Calculate property tax.
        
        Args:
            annual_value: Annual value of property
            is_owner_occupied: Whether owner-occupied
            
        Returns:
            Dictionary with tax calculation
        """
        av = Decimal(str(annual_value))
        tax_amount = Decimal('0')
        breakdown = []
        
        if is_owner_occupied:
            rates = self.property_tax_owner_occupied
        else:
            # Non-owner occupied flat rate of 10% for residential
            tax_amount = av * Decimal('0.10')
            return {
                'annual_value': float(av),
                'tax_amount': float(tax_amount),
                'rate': '10%',
                'type': 'Non-owner occupied'
            }
        
        remaining_av = av
        for bracket_amount, rate in rates:
            if remaining_av <= 0:
                break
            
            if bracket_amount == float('inf'):
                taxable_in_bracket = remaining_av
            else:
                taxable_in_bracket = min(remaining_av, Decimal(str(bracket_amount)))
            
            bracket_tax = taxable_in_bracket * rate
            tax_amount += bracket_tax
            
            if bracket_tax > 0:
                breakdown.append({
                    'av_range': f"${taxable_in_bracket:,.0f}",
                    'rate': f"{rate * 100:.1f}%",
                    'tax': float(bracket_tax)
                })
            
            remaining_av -= taxable_in_bracket
        
        return {
            'annual_value': float(av),
            'tax_amount': float(tax_amount),
            'breakdown': breakdown,
            'type': 'Owner-occupied'
        }
    
    def calculate_cpf(self,
                     monthly_salary: float,
                     age: int,
                     bonus: float = 0) -> Dict[str, Any]:
        """
        Calculate CPF contributions.
        
        Args:
            monthly_salary: Monthly ordinary wage
            age: Employee age
            bonus: Additional wage (bonus)
            
        Returns:
            Dictionary with CPF breakdown
        """
        # Determine age bracket
        if age < 55:
            rates = self.cpf_rates['below_55']
        elif age < 60:
            rates = self.cpf_rates['55_to_60']
        elif age < 65:
            rates = self.cpf_rates['60_to_65']
        elif age < 70:
            rates = self.cpf_rates['65_to_70']
        else:
            rates = self.cpf_rates['above_70']
        
        # Cap ordinary wage
        capped_salary = min(monthly_salary, self.cpf_ordinary_wage_ceiling)
        
        # Calculate monthly CPF
        employee_cpf = Decimal(str(capped_salary)) * rates['employee']
        employer_cpf = Decimal(str(capped_salary)) * rates['employer']
        
        # Annual calculations
        annual_employee = employee_cpf * 12
        annual_employer = employer_cpf * 12
        
        # Add bonus CPF (subject to additional wage ceiling)
        if bonus > 0:
            annual_ordinary = Decimal(str(capped_salary)) * 12
            remaining_ceiling = Decimal(str(self.cpf_additional_wage_ceiling)) - annual_ordinary
            capped_bonus = min(Decimal(str(bonus)), max(remaining_ceiling, Decimal('0')))
            
            bonus_employee = capped_bonus * rates['employee']
            bonus_employer = capped_bonus * rates['employer']
            
            annual_employee += bonus_employee
            annual_employer += bonus_employer
        
        return {
            'monthly': {
                'employee': float(employee_cpf.quantize(Decimal('0.01'))),
                'employer': float(employer_cpf.quantize(Decimal('0.01'))),
                'total': float((employee_cpf + employer_cpf).quantize(Decimal('0.01')))
            },
            'annual': {
                'employee': float(annual_employee.quantize(Decimal('0.01'))),
                'employer': float(annual_employer.quantize(Decimal('0.01'))),
                'total': float((annual_employee + annual_employer).quantize(Decimal('0.01')))
            },
            'rates': {
                'employee': f"{rates['employee'] * 100:.1f}%",
                'employer': f"{rates['employer'] * 100:.1f}%"
            },
            'age_bracket': f"{age} years old"
        }
    
    def calculate_take_home(self,
                          gross_income: float,
                          monthly_salary: float = None,
                          age: int = 30,
                          reliefs: Dict[str, float] = None,
                          is_resident: bool = True) -> Dict[str, Any]:
        """
        Calculate take-home pay after tax and CPF.
        
        Args:
            gross_income: Annual gross income
            monthly_salary: Monthly salary for CPF calculation
            age: Employee age
            reliefs: Tax reliefs to apply
            is_resident: Tax residency status
            
        Returns:
            Comprehensive take-home calculation
        """
        # If monthly salary not provided, estimate from annual
        if monthly_salary is None:
            monthly_salary = gross_income / 12
        
        # Calculate tax
        tax_result = self.calculate_income_tax(gross_income, reliefs, is_resident, age)
        
        # Calculate CPF
        cpf_result = self.calculate_cpf(monthly_salary, age)
        
        # Calculate take-home
        annual_cpf = cpf_result['annual']['employee']
        annual_take_home = Decimal(str(gross_income)) - tax_result.tax_amount - Decimal(str(annual_cpf))
        monthly_take_home = annual_take_home / 12
        
        return {
            'gross_income': gross_income,
            'tax': {
                'annual': float(tax_result.tax_amount),
                'monthly': float(tax_result.tax_amount / 12),
                'effective_rate': float(tax_result.effective_rate)
            },
            'cpf': {
                'annual': annual_cpf,
                'monthly': cpf_result['monthly']['employee']
            },
            'take_home': {
                'annual': float(annual_take_home.quantize(Decimal('0.01'))),
                'monthly': float(monthly_take_home.quantize(Decimal('0.01')))
            },
            'breakdown': {
                'gross_monthly': monthly_salary,
                'cpf_deduction': cpf_result['monthly']['employee'],
                'tax_deduction': float((tax_result.tax_amount / 12).quantize(Decimal('0.01'))),
                'net_monthly': float(monthly_take_home.quantize(Decimal('0.01')))
            }
        }