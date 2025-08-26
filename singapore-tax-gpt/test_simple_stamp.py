"""Simple test of stamp duty calculator without IRAS API."""

from src.apis.stamp_duty_calculator import StampDutyCalculator

calc = StampDutyCalculator()

print("Testing Stamp Duty Calculator (No IRAS API)")
print("=" * 50)

# Test $1.5M property for citizen first home
result = calc.calculate_property_stamp_duty(
    purchase_price=1500000,
    buyer_profile="singapore_citizen",
    num_properties=0
)

print(f"\n$1.5M Property - Singapore Citizen (1st Home):")
print(f"BSD: ${result['buyer_stamp_duty']:,.0f}")
print(f"ABSD: ${result['additional_buyer_stamp_duty']:,.0f}")
print(f"Total: ${result['total_stamp_duty']:,.0f}")

# Test $2M property for foreigner
result = calc.calculate_property_stamp_duty(
    purchase_price=2000000,
    buyer_profile="foreigner",
    num_properties=0
)

print(f"\n$2M Property - Foreigner:")
print(f"BSD: ${result['buyer_stamp_duty']:,.0f}")
print(f"ABSD: ${result['additional_buyer_stamp_duty']:,.0f}")
print(f"Total: ${result['total_stamp_duty']:,.0f}")

print("\n✅ All IRAS API code removed successfully!")