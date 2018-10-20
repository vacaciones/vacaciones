from datetime import date, timedelta
import quandl
import pandas as pd
from yahoo_finance import Share
import pandas-datareader as web

since = (date.today() - timedelta(days = 365 * 2)).isoformat()
upTo  = date.today().isoformat()

print since, upTo
VOWShare = Share('GOOG')

print VOWShare.get_price()

VOWPrices = VOWShare.get_historical(since, upTo)

