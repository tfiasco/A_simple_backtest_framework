from collections import deque
import pandas as pd
import matplotlib.pyplot as plt

class Account(object):
    
    def __init__(self, initCash, exchange):
        self._capital = deque()
        self._orders = deque()
        self._position = {}
        self._capital.append([0, 0])
        self._exchange = exchange
        self._exchange.orderInsertEvent.subscribe(self.__onOrderInsert)
        self._exchange.tradeEvent.subscribe(self.__onOrderTrade)
        self._exchange.mktDataEvent.subscribe(self.__onMktData)
    
    def __onOrderInsert(self, order):
        # print('Account on insert')
        self._orders.append(order)
    
    def __onOrderTrade(self, tradeInfo):
        # print('Account on trade')
        try:
            prevPos = self._position[tradeInfo.instrument][-1][1]
        except KeyError:
            self._position[tradeInfo.instrument] = deque([(0, 0)])
            prevPos = 0
        posChange = tradeInfo.direction.value * tradeInfo.quantity
        if self._position[tradeInfo.instrument][-1][0] == tradeInfo.dateTime:
            self._position[tradeInfo.instrument][-1][1] += posChange
        else:
            self._position[tradeInfo.instrument].append([tradeInfo.dateTime, prevPos + posChange])
        self._capital[-1][1] -= tradeInfo.commission
        # print('commission: %s' % tradeInfo.commission)
        # print('current capital: %s' % (self._capital[-1]))
        
    def __onMktData(self, barGroup):
        # print('Account on mkt data')
        for instr, b in barGroup.iteritems():
            try:
                prevCapital = self._capital[-1][1]
                curPos = self._position[instr][-1][1]
                previousClose = self._exchange._hist[instr].close[-1]
                valueChange = float(curPos) * (b.close - previousClose)
                self._capital.append([barGroup.dateTime, prevCapital + valueChange])
                # print('current close: %s - %s' % (b.dateTime, b.close))
                # print('previous close: %s - %s' % (self._exchange._hist[instr].dateTime[-1], previousClose))
                # print('current pos: %s,    value change: %s' % (curPos, valueChange))
                # print('current capital: %s' % (self._capital[-1]))
            except KeyError:
                pass
        
    def plot(self):
        plotDateTime = []
        for bs in self._exchange._hist.values():
            tempDateTime = bs.dateTime
            if len(tempDateTime) > len(plotDateTime):
                plotDateTime = tempDateTime
        
        def _getPlotData(aList):
            plotData = pd.DataFrame(aList)
            plotData.set_index(0, inplace=True)
            plotData = plotData.reindex(list(plotDateTime))
            if plotData.isnull()[1][0]:
                plotData[1][0] = 0
            return plotData.fillna(method='ffill')
        
        plotCount = len(self._position.values())
        plotCount += 1
        # ''' 
        # Capital
        capitalSeries = _getPlotData(list(self._capital)[1:])
        plt.subplot(plotCount, 1, 1)
        plt.plot(capitalSeries)
        plt.title('Capital')
        # '''
        # Position
        i = 2
        for instr, pos in self._position.iteritems():
            posSeries = _getPlotData(list(self._position[instr])[1:])
            plt.subplot(plotCount, 1, i)
            plt.plot(posSeries)
            plt.title('Position of %s' % instr)
            i += 1
        plt.show()