import bar, exchange, marketdata, account


class BaseStrategy(object):
    
    def __init__(self, mktList, commModel, slipModel, initCash):
        self._mktList = mktList
        self._comm = commModel
        self._slip = slipModel
        
        # barDict = {}
        # for mkt in mktList:
        #     barDict[mkt.instrument] = marketdata.from_mktdata_to_bar(
        #         mkt.mktDataGenerator.next(), mkt.freq)
        
        self._barDictGenerator = marketdata.MergedBarDictGenerator(mktList)
        barDict = self._barDictGenerator.next()
        self._barGroup = bar.BarGroup(barDict)
        self._exchange = exchange.Exchange(self._barGroup, slipModel, commModel)
        self._account = account.Account(initCash, self._exchange)
        self._hist = self._exchange._hist
        self._barGroup.updateEvent.subscribe(self._onMktData)
        self._barGroup.updateEvent.subscribe(self._hist._onMktData)
        self._position = self._account._position
    
    def _sendOrder(self, order):
        order.tradeEvent.subscribe(self._onTradeEvent)
        order.send(self._exchange)
        
    def _cancelOrder(self, order):
        order.cancel(self._exchange)
        
    def _onMktData(self, barGroup):
        raise NotImplementedError()
    
    def _onTradeEvent(self, tradeInfo):
        pass
        
    def run(self):
        try:
            while True:            
                barDict = self._barDictGenerator.next()
                self._barGroup.update(barDict)
            
        except StopIteration:
            print('DONE')
            self._account.plot()
