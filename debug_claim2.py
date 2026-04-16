from scenarios.claim_marketplace_buyer import ClaimMarketplaceBuyerScenario

s = ClaimMarketplaceBuyerScenario()
s.process_answer("")

print("After start:")
print(f"  data: {s.data}")
print(f"  current_step: {s.get_current_step()}")

s.process_answer("1")  # recipient_type = marketplace

print("\nAfter answer '1':")
print(f"  data: {s.data}")
print(f"  current_step: {s.get_current_step()}")

s.process_answer("1")  # platform = Ozon

print("\nAfter answer '1' for platform:")
print(f"  data: {s.data}")
print(f"  current_step: {s.get_current_step()}")