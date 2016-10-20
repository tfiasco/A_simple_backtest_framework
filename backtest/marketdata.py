import pandas as pd
import numpy as np
from bar import Bar


class pdMktData(object):
    
    def __init__(self, instrument, df, freq):
        self._dealingWithDataFrame(instrument, df, freq)

    def _dealingWithDataFrame(self, instrument, df, freq):
        df.dateTime = pd.to_datetime(df.dateTime)
        df.set_index('dateTime', inplace=True, drop=False)
        df.sort_index(inplace=True)
        df.columns = [[instrument] * 7, df.columns]
        
        self.df = df
        # self.mktDataGenerator = (df.iloc[i, :] for i in xrange(df.shape[0]))
        self.instrument = instrument
        self.freq = freq
        

class CsvMktData(pdMktData):
    
    def __init__(self, instrument, csvPath, freq):
        
        df = pd.read_csv(csvPath, names=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'adjClose'], header=0)
        self._dealingWithDataFrame(instrument, df, freq) 


def MergedBarDictGenerator(mktDataList):
    
    dfList = [mkt.df for mkt in mktDataList]
    # instrList = [mkt.instrument for mkt in mktDataList]
    fullDF = reduce(lambda x, y: pd.merge(x, y, how='outer', left_index=True, right_index=True), dfList)
    
    for dt in fullDF.index:
        row = fullDF.ix[dt]
        barDict = {}
        
        for mkt in mktDataList:
            newBar = from_mktdata_to_bar(row[mkt.instrument], mkt.freq)
            if newBar is not None:
                barDict[mkt.instrument] = newBar
        yield barDict
        

def from_mktdata_to_bar(mktData, freq):
    if (mktData.isnull().sum() == 0) or (mktData.isnull().sum() == 1 and np.isnan(mktData.adjClose)):
        return Bar(mktData.dateTime, mktData.open, mktData.high, mktData.low, mktData.close,
            mktData.volume, mktData.adjClose, freq)
    else:
        return None