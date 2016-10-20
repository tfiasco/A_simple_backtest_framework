class SlippageModel(object):
    
    def calculatePrice(self, order, price, quantity, bar):
        """Return Price"""
        raise NotImplementedError()  


class NoSlippage(SlippageModel):
    
    def calculatePrice(self, order, price, quantity, bar):
        return price


class VolumeShareSlippage(SlippageModel):

    def __init__(self, priceImpact=0.1):
        super(VolumeShareSlippage, self).__init__()
        self.__priceImpact = priceImpact
    
    def calculatePrice(self, order, price, quantity, bar):
        assert bar.volume, "0 Volume, VolumeShareSlippage Error"
        # TODO
        pass


class FixedTickSlippage(SlippageModel):
    
    def __init__(self, tickValue, tickSlip=1):
        super(FixedTickSlippage, self).__init__()
        self.__tickValue = tickValue
        self.__tickSlip = tickSlip
    
    def calculatePrice(self, order, price, quantity, bar):
        if order.isBuy():
            return price + self.__tickSlip * self.__tickValue
        elif order.isSell():
            return price - self.__tickSlip * self.__tickValue
        else:
            raise Exception('Invalid Order Direction')

