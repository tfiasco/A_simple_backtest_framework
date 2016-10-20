class Commission(object):
    
    def calculate(self, order, price, quantity):
        raise NotImplementedError()
        

class NoCommission(Commission):
    
    def calculate(self, order, price, quantity):
        return 0


class FixedCommission(Commission):
    
    def __init__(self, value):
        super(FixedCommission, self).__init__()
        self.__value = value
    
    def calculate(self, order, price, quantity):
        return self.__value


class PercentCommission(Commission):
    
    def __init__(self, pct):
        super(PercentCommission, self).__init__()
        self.__pct = pct
    
    def calculate(self, order, price, quantity):
        return price * quantity * self.__pct