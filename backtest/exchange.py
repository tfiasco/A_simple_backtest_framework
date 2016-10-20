from collections import deque
from order import Order, TradeInfo
import bar, event

class Exchange(object):
    
    def __init__(self, barGroup, slippageModel, commissionModel):
        self.__orderId = 0
        self.__orderDeque = {}
        for instr in barGroup.keys():
            self.__orderDeque[instr] = deque()
        self.__barGroup = barGroup
        self.__slippage = slippageModel
        self.__commission = commissionModel
        self.__barGroup.updateEvent.subscribe(self.__onMktData)
        
        self._hist = bar.HistBars()
        
        self._tradeEvent = event.Event()
        self._orderInsertEvent = event.Event()
        self._mktDataEvent = event.Event()
    
    @property
    def tradeEvent(self):
        return self._tradeEvent
    
    @property
    def orderInsertEvent(self):
        return self._orderInsertEvent
    
    @property
    def mktDataEvent(self):
        return self._mktDataEvent
    
    def insertOrder(self, order):
        order.id = self.__orderId
        self.__orderDeque[order.instrument].append(order)
        self.__orderId += 1
        order.state = Order.State.ACCEPTED
        order.submitDateTime = self.__barGroup.dateTime
        order.insertEvent.emit()
        self._orderInsertEvent.emit(order)
        
        self.__checkSendOrderTrade(order)
    
    def cancelOrder(self, order):
        self.rmOrder(order)
        order.cancelEvent.emit()
    
    def rmOrder(self, order):
        self.__orderDeque[order.instrument].remove(order)
        # print 'order {} removed, state: {}'.format(order.id, order.state)
    
    def __onMktData(self, barGroup):
        self._mktDataEvent.emit(barGroup)
        # print('exchange on market data')
        # print(barGroup)
        for instr, orderdeq in self.__orderDeque.iteritems():
            for order in list(orderdeq):
                self.__checkMktPriceTrade(order)
            
    def __checkSendOrderTrade(self, order):
        for instr, b in self.__barGroup.iteritems():
            if b.freq == bar.Frequency.TICK:
                print('TODO: Deal with tick data')
        
    def __checkMktPriceTrade(self, order):
        for instr, b in self.__barGroup.iteritems():
            if b.freq > bar.Frequency.TICK:
                if instr == order.instrument and b.volume > 0 and b.remainVol > 0:
                    tradePrice = self.__checkLimitOrder(order, b)
                    if tradePrice > 0:
                        tradeQuantity = order.quantity if order.quantity < b.remainVol else b.volume
                        tradePrice = self.__slippage.calculatePrice(order, tradePrice, tradeQuantity, b)
                        tradeCommission = self.__commission.calculate(order, tradePrice, tradeQuantity)
                        tradeInfo = TradeInfo(instr, tradePrice, tradeQuantity, order.direction, tradeCommission, b.dateTime)
                        order.tradeEvent.emit(tradeInfo)
                        self._tradeEvent.emit(tradeInfo)
                        b.remainVol -= tradeQuantity
                        if order.state == Order.State.ALL_TRADED:
                            self.rmOrder(order)
            else:
                print('TODO: Deal with tick data')
            
    def __checkLimitOrder(self, order, bar):
        if order.direction == Order.Direction.BUY:
            if order.price > bar.open:
                tradePrice = bar.open
            elif order.price > bar.low:
                tradePrice = order.price
            else:
                tradePrice = 0
        else:
            if bar.open < order.price < bar.high:
                tradePrice = order.price
            elif order.price <= bar.open:
                tradePrice = bar.open
            else:
                tradePrice = 0
        return tradePrice