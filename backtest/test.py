import bar, commission, exchange, marketdata, order, slippage, strategy
import numpy as np


mkt = marketdata.CsvMktData('SS', 'D:\\Documents\\testdata.csv', bar.Frequency.DAY)
comm = commission.PercentCommission(0.03/100)
slip = slippage.FixedTickSlippage(1, 1)

newDF = mkt.df.copy()
newDF.columns = ['dateTime', 'open', 'high', 'low', 'close', 'volume', 'adjClose']
    
newIdx = list(newDF.index)
for i, idx in enumerate(list(newDF.index)):
    if i % 5 != 0:
        newIdx.remove(idx)
        newDF = newDF.reindex(newIdx)

mkt2 = marketdata.pdMktData('TEST', newDF, bar.Frequency.WEEK)

class SimpleStrategy(strategy.BaseStrategy):
        
    def _onMktData(self, barGroup):
        # super(SimpleStrategy, self).__onMktData()
        # print('SimpleStrategy on market data')
        print '###################.{}'.format(barGroup.dateTime)
        try:
            if len(list(self._hist['SS'].close[-10:])):
                if barGroup['SS'].close > np.max(list(self._hist['SS'].high[-10:])):
                    o1 = order.Order('limit', barGroup['SS'].close + 100, order.Order.Direction.BUY, 'SS', 300)
                    self._sendOrder(o1)
                elif barGroup['SS'].close < np.min(list(self._hist['SS'].low[-10:])):
                    o1 = order.Order('limit', barGroup['SS'].close - 100, order.Order.Direction.SELL, 'SS', 300)
                    self._sendOrder(o1)
        except KeyError:
            pass
            
strat = SimpleStrategy([mkt], comm, slip, 0)
strat.run()