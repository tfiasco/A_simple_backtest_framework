from enum import Enum
import event

class Order(object):
    
    class Direction(Enum):
        BUY = 1
        SELL = -1
    
    class State(Enum):
        INITIAL = 1
        SUBMITTED = 2
        ACCEPTED = 3
        CANCELLED = 4
        PART_TRADED = 5
        ALL_TRADED = 6
        PART_TRADED_PART_CANCELED = 7
        
    def __init__(self, type_, price, direction, instrument, quantity):
        assert quantity, 'Invalid quantity'
        
        self._id = None
        self._type = type_
        self._price = price
        self._direction = direction
        self._instrument = instrument
        self._quantity = int(quantity)
        self._state = Order.State.INITIAL
        self._submitDateTime = None
        self._commission = 0
        self._tradedVol = 0
        self._tradeInfo = None
        self._tradeEvent = event.Event()
        self._cancelEvent = event.Event()
        self._insertEvent = event.Event()
        self._tradeEvent.subscribe(self._onTradeEvent)
        self._cancelEvent.subscribe(self._onCancelEvent)
        self._insertEvent.subscribe(self._onInsertEvent)
        
    @property
    def id(self):
        return self._id
    
    @property
    def type(self):
        return self._type
    
    @property
    def price(self):
        return self._price
    
    @property
    def direction(self):
        return self._direction
    
    @property
    def quantity(self):
        return self._quantity
    
    @property
    def instrument(self):
        return self._instrument
    
    @property
    def state(self):
        return self._state
    
    @property
    def submitDateTime(self):
        return self._submitDateTime
    
    @property
    def commission(self):
        return self._commission
    
    @property
    def tradedVol(self):
        return self._tradedVol
    
    @property
    def remain(self):
        return int(self._quantity - self._tradedVol)
    
    @property
    def tradeInfo(self):
        return self._tradeInfo
    
    @property
    def tradeEvent(self):
        return self._tradeEvent
    
    @property
    def cancelEvent(self):
        return self._cancelEvent
    
    @property
    def insertEvent(self):
        return self._insertEvent
    
    @state.setter
    def state(self, newState):
        self._state = newState
    
    @id.setter
    def id(self, newID):
        self._id = newID
    
    @submitDateTime.setter
    def submitDateTime(self, dateTime):
        self._submitDateTime = dateTime
    
    def isBuy(self):
        return self._direction.value == 1
    
    def isSell(self):
        return self._direction.value == -1
    
    def addTradeInfo(self, tradeInfo):
        self._tradeInfo = tradeInfo
        self._tradedVol = int(self._tradedVol + tradeInfo.quantity)
        self._commission += tradeInfo.commission
        
        if self.remain == 0:
            self.state = Order.State.ALL_TRADED
        else:
            self.state = Order.State.PART_TRADED
    
    def send(self, exchange):
        self.state = Order.State.SUBMITTED
        exchange.insertOrder(self)
    
    def cancel(self, exchange):
        exchange.rmOrder(self)
    
    def _onInsertEvent(self):
        # print('order %s inserted - Price: %s - Dir: %s - Quantity: %s - Time: %s' 
        #     % (self._id, self._price, self._direction, self._quantity, self._submitDateTime))
        pass
    
    def _onTradeEvent(self, tradeInfo):
        self.addTradeInfo(tradeInfo)
        # print('order %s on trade , state: %s' % (self._id, self._state))
        # print(tradeInfo)
    
    def _onCancelEvent(self):
        if self.remain < self.quantity:
            self.state = Order.State.PART_TRADED_PART_CANCELED
        else:
            self.state = Order.State.CANCELLED        
        # print('order %s on cancel, state: %s' % (self._id, self._state))


class TradeInfo(object):
    
    def __init__(self, instrument, price, quantity, direction, commission, dateTime):
        self._instrument = instrument
        self._price = price
        self._quantity = quantity
        self._commission = commission
        self._dateTime = dateTime
        self._direction = direction
    
    def __str__(self):
        return "%s - Price: %s - Amount: %s - Fee: %s" % (self._dateTime, self._price, self._quantity, self._commission)
    
    @property
    def price(self):
        return self._price
    
    @property
    def instrument(self):
        return self._instrument
    
    @property
    def direction(self):
        return self._direction
    
    @property
    def quantity(self):
        return self._quantity
    
    @property
    def commission(self):
        return self._commission
    
    @property
    def dateTime(self):
        return self._dateTime


