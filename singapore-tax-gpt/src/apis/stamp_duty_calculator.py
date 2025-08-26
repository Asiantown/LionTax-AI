"""Singapore Stamp Duty Calculator (Local Implementation)."""

from typing import Dict, Any


class StampDutyCalculator:
    """Calculate stamp duty for property purchases in Singapore."""
    
    @staticmethod
    def calculate_bsd(consideration: float) -> float:
        """
        Calculate Buyer's Stamp Duty (BSD).
        
        Current rates (as of 2024):
        - First $180,000: 1%
        - Next $180,000: 2%
        - Next $640,000: 3%
        - Next $500,000: 4%
        - Next $1,500,000: 5%
        - Above $3,000,000: 6%
        """
        bsd = 0
        
        if consideration <= 180000:
            bsd = consideration * 0.01
        elif consideration <= 360000:
            bsd = 1800 + (consideration - 180000) * 0.02
        elif consideration <= 1000000:
            bsd = 5400 + (consideration - 360000) * 0.03
        elif consideration <= 1500000:
            bsd = 24600 + (consideration - 1000000) * 0.04
        elif consideration <= 3000000:
            bsd = 44600 + (consideration - 1500000) * 0.05
        else:
            bsd = 119600 + (consideration - 3000000) * 0.06
        
        return bsd
    
    @staticmethod
    def calculate_absd(consideration: float, 
                      buyer_profile: str,
                      num_properties: int) -> float:
        """
        Calculate Additional Buyer's Stamp Duty (ABSD).
        
        Current rates (as of 2024):
        Singapore Citizens:
        - 1st property: 0%
        - 2nd property: 20%
        - 3rd+ property: 30%
        
        Singapore PR:
        - 1st property: 5%
        - 2nd property: 30%
        - 3rd+ property: 35%
        
        Foreigners: 60%
        Entities: 65%
        """
        absd_rate = 0
        
        if buyer_profile == "singapore_citizen":
            if num_properties == 0:
                absd_rate = 0
            elif num_properties == 1:
                absd_rate = 0.20
            else:
                absd_rate = 0.30
        elif buyer_profile == "pr":
            if num_properties == 0:
                absd_rate = 0.05
            elif num_properties == 1:
                absd_rate = 0.30
            else:
                absd_rate = 0.35
        elif buyer_profile == "foreigner":
            absd_rate = 0.60
        elif buyer_profile == "entity":
            absd_rate = 0.65
        
        return consideration * absd_rate
    
    @staticmethod
    def calculate_lease_duty(avg_annual_rent: float, lease_period: float) -> float:
        """
        Calculate lease stamp duty.
        
        Rate: 0.4% of total rent for the period of lease
        """
        # Calculate based on lease period
        if lease_period <= 1:
            # Less than 1 year: 0.4% of total rent
            duty = avg_annual_rent * lease_period * 0.004
        elif lease_period <= 4:
            # 1-4 years: 0.4% of AAR
            duty = avg_annual_rent * 0.004
        else:
            # More than 4 years: 0.4% of 4 x AAR
            duty = avg_annual_rent * 4 * 0.004
        
        return duty
    
    def calculate_property_stamp_duty(self,
                                     purchase_price: float,
                                     market_value: float = None,
                                     buyer_profile: str = "singapore_citizen",
                                     num_properties: int = 0,
                                     property_type: str = "residential") -> Dict[str, Any]:
        """
        Calculate total stamp duty for property purchase.
        
        Args:
            purchase_price: Purchase price of property
            market_value: Market value (if different from purchase price)
            buyer_profile: Type of buyer (singapore_citizen, pr, foreigner, entity)
            num_properties: Number of properties already owned
            property_type: Type of property (residential, non_residential)
            
        Returns:
            Stamp duty calculation results
        """
        # Use higher of purchase price or market value
        consideration = max(purchase_price, market_value or purchase_price)
        
        # Calculate BSD and ABSD
        bsd = self.calculate_bsd(consideration)
        absd = self.calculate_absd(consideration, buyer_profile, num_properties)
        
        return {
            "success": True,
            "consideration": consideration,
            "buyer_stamp_duty": bsd,
            "additional_buyer_stamp_duty": absd,
            "total_stamp_duty": bsd + absd,
            "breakdown": {
                "bsd_rate": f"{(bsd/consideration*100):.2f}%" if consideration > 0 else "0%",
                "absd_rate": f"{(absd/consideration*100):.2f}%" if consideration > 0 else "0%",
            },
            "buyer_profile": buyer_profile,
            "num_properties": num_properties,
            "property_type": property_type
        }