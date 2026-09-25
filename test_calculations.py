from utils.calculations import safety_stock,reorder_point,eoq,coverage

def test_safety(): assert safety_stock(10,5,2)>0
def test_reorder(): assert reorder_point(10,5,5)==55
def test_eoq(): assert eoq(1000,10,2)>0
def test_coverage(): assert coverage(100,10)==10
