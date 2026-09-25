import math

def safety_stock(avg_daily, lead_time_days, demand_std=0, z=1.65):
    return max(0.0, z * demand_std * math.sqrt(max(lead_time_days,0)))

def reorder_point(avg_daily, lead_time_days, safety):
    return max(0.0, avg_daily*max(lead_time_days,0)+safety)

def eoq(annual_demand, order_cost, holding_cost):
    if annual_demand<=0 or order_cost<=0 or holding_cost<=0: return 0.0
    return math.sqrt((2*annual_demand*order_cost)/holding_cost)

def coverage(stock, avg_daily):
    return float("inf") if avg_daily<=0 else max(0,stock)/avg_daily

def rotation(annual_consumption, avg_inventory):
    return 0.0 if avg_inventory<=0 else annual_consumption/avg_inventory
