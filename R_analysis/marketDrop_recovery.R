#market drop
#this function analyses given a market drop how much a stock recovers to

#tickers <- c("GS", "UBS","TSLA","AAPL","CS","F","ITUB")
tickers <- c("GS")
collect_since <-  "2017-01-01"

marketData <- assembleData(tickers,collect_since = collect_since)


marketDrop_threshold <- 0.25


marketDrop_window <- c(7,30,250) #marketData indexes are in days


#par(new = TRUE)


#rolling_mean <- (rollapply(marketData$price, marketDrop_window[1], mean))
#plot(marketData$price)
#lines(rolling_mean)





