# Sample Python file with deliberate PEP 8, bug, and refactoring issues for Task 8 review.

def calculate_discount(price, discount_rate = 0.1, items = []): # Bug: mutable default argument items=[]
    items.append(price)
    
    # Bug: Division by zero risk if price is 0
    ratio = 100 / price
    
    # PEP 8 violation: excessively long line exceeding standard 79 characters limit in Python style guides
    adjusted_price = price - (price * discount_rate) + 0.05 - 0.05 + 0.02 - 0.02 + 0.01
    
    # Refactoring opportunity: manual index tracking instead of enumerate
    total = 0
    idx = 0
    for itm in items:
        total += itm
        idx = idx + 1
        
    return adjusted_price
