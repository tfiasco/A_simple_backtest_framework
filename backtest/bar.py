import event

class Bar(object):
    
    __slots__ = (
        '_dateTime',
        '_open',
        '_close',
        '_high',
        '_low',
        '_volume',
        '_adjClose',
        '_freq',
        '_useAdj',
        '_remainVol',
        '_extra',
    )
    
    def __init__(self, dateTime, open_, high, low, close, volume, adjClose, freq, extra={}):
        self._dateTime = dateTime
        self._open = float(open_)
        self._close = float(close)
        self._high = float(high)
        self._low = float(low)
        self._volume = float(volume)
        self._adjClose = float(adjClose) if adjClose is not None else None
        self._freq = freq
        self._useAdj = False
        self._remainVol = float(volume)
        self._extra = extra
    
    @property
    def useAdj(self):
        return self._useAdj
    
    @useAdj.setter
    def useAdj(self, useAdj):
        self._useAdj = useAdj
    
    @property
    def dateTime(self):
        return self._dateTime
    
    @property
    def volume(self):
        return self._volume
    
    @property
    def freq(self):
        return self._freq
    
    @property
    def adjClose(self):
        return self._adjClose
    
    @property
    def price(self):
        if self.useAdj:
            self.__checkAdjCloseAvailable()
            return self._adjClose
        else:
            return self._close
    
    @property
    def open(self):
        if self.useAdj:
            self.__checkAdjCloseAvailable()
            return self.__getAdjValue(self._open)
        else:
            return self._open
    
    @property
    def high(self):
        if self.useAdj:
            self.__checkAdjCloseAvailable()
            return self.__getAdjValue(self._high)
        else:
            return self._high
    
    @property
    def low(self):
        if self.useAdj:
            self.__checkAdjCloseAvailable()
            return self.__getAdjValue(self._low)
        else:
            return self._low
    
    @property
    def close(self):
        if self.useAdj:
            self.__checkAdjCloseAvailable()
            return self.__getAdjValue(self._close)
        else:
            return self._close
    
    @property
    def remainVol(self):
        return self._remainVol
    
    @remainVol.setter
    def remainVol(self, newRemainVol):
        if newRemainVol < 0:
            print self.dateTime
            print '################################ bar remain volume must be positive ###################################'
        # assert newRemainVol >= 0, 'bar remain volume must be positive. {}'
        self._remainVol = newRemainVol
    
    def __checkAdjCloseAvailable(self):
        if self._adjClose is None:
            raise Exception('Adjusted close is not available')
    
    def __getAdjValue(self, value):
        return self._adjClose * value / float(self.__close)
    
    def getOpen(self, adj=False):
        if adj:
            self.__checkAdjCloseAvailable()
            return self.__getAdjValue(self.__open)
        else:
            return self._open
    
    def getHigh(self, adj=False):
        if adj:
            self.__checkAdjCloseAvailable()
            return self.__getAdjValue(self.__high)
        else:
            return self._high
        
    def getLow(self, adj=False):
        if adj:
            self.__checkAdjCloseAvailable()
            return self.__getAdjValue(self.__low)
        else:
            return self._low
    
    def getCLose(self, adj=False):
        if adj:
            self.__checkAdjCloseAvailable()
            return self._adjClose
        else:
            return self._close
            
    def getExtra(self, key):
        return self._extra[key]
    
    def setExtra(self, key, value):
        self._extra[key] = value
    
    
class Frequency(object):
    
    TICK = -1
    SECOND = 1
    MINUTE = 60
    HOUR = 60*60
    DAY = 24*60*60
    WEEK = 24*60*60*7
    MONTH = 24*60*60*31
    
    
class BarGroup(object):
    
    def __init__(self, barDict):
        self._updateEvent = event.Event()
        self._preBarEvent = event.Event()
        self.update(barDict)
    
    def __getitem__(self, instrument):
        return self.__barDict[instrument]
    
    def __contains__(self, instrument):
        return instrument in self.__barDict
    
    def items(self):
        return self.__barDict.items()
    
    def keys(self):
        return self.__barDict.keys()
    
    def iteritems(self):
        return self.__barDict.iteritems()
    
    @property
    def instruments(self):
        return self.keys()
    
    @property
    def dateTime(self):
        return self._dateTime
    
    @property
    def updateEvent(self):
        return self._updateEvent
    
    def update(self, barDict):
        self._preBarEvent.emit()
        
        firstDateTime = None
        for instrument, currentBar in barDict.iteritems():
            if firstDateTime is None:
                firstDateTime = currentBar.dateTime
            elif currentBar.dateTime != firstDateTime:
                raise Exception('Bar Group Time Error: %s - %s' % (currentBar.dateTime, firstDateTime))
        
        self.__barDict = barDict
        self._dateTime = firstDateTime
    
        self._updateEvent.emit(self)
        
    def getBar(self, instrument):
        return self.__barDict.get(instrument, None)
    
    def __str__(self):
        printStr = ''
        for instr, b in self.iteritems():
            printStr += '%s - Time: %s - Open: %s - High: %s - Low: %s - Close: %s - Volume: %s \n' \
                % (instr, b.dateTime, b.open, b.high, b.low, b.close, b.volume)
        printStr = printStr[:-2]
        return printStr
    

class HistBars(object):
    
    def __init__(self):
        self.__barSeriesDict = {}
    
    def __setitem__(self, key, value):
        self.__barSeriesDict[key] = value
    
    def __getitem__(self, key):
        return self.__barSeriesDict[key]
    
    def keys(self):
        return self.__barSeriesDict.keys()
    
    def values(self):
        return self.__barSeriesDict.values()
    
    def _onMktData(self, barGroup):
        for instr, b in barGroup.iteritems():
            try:
                self.__barSeriesDict[instr].append(b)
            except KeyError:
                self.__barSeriesDict[instr] = BarSeries()


class BarSeries(object):
    
    def __init__(self, maxLen=1024):
        self._open = ListDeque(maxLen)
        self._high = ListDeque(maxLen)
        self._low = ListDeque(maxLen)
        self._close = ListDeque(maxLen)
        self._volume = ListDeque(maxLen)
        self._dateTime = ListDeque(maxLen)
        self._adjClose = ListDeque(maxLen)
    
    def append(self, bar):
        self._open.append(bar.open)
        self._high.append(bar.high)
        self._low.append(bar.low)
        self._close.append(bar.close)
        self._volume.append(bar.volume)
        self._dateTime.append(bar.dateTime)
        self._adjClose.append(bar.adjClose)
    
    @property
    def open(self):
        return self._open
    
    @property
    def high(self):
        return self._high
    
    @property
    def low(self):
        return self._low
    
    @property
    def close(self):
        return self._close
    
    @property
    def volume(self):
        return self._volume
    
    @property
    def dateTime(self):
        return self._dateTime
    
    @property
    def adjClose(self):
        return self._adjClose
    

class ListDeque(object):
    def __init__(self, maxLen=1024):
        self._values = []
        self._maxLen = maxLen
    
    @property
    def maxLen(self):
        return self._maxLen
    
    @maxLen.setter
    def maxLen(self, newLen):
        self._maxLen = newLen
        self._values = self._values[-1*newLen]
    
    def __len__(self):
        return len(self._values)
    
    def __getitem__(self, key):
        return self._values[key]
    
    def append(self, value):
        self._values.append(value)
        