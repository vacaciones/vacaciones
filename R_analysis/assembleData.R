
assembleData <- function (tickers_equity = "none", collect_since = "none"){

library(corrplot)
library(xts)
  

if (tickers_equity == "none"){

tickers_equity <- c("GS", "UBS","TSLA","AAPL","CS","F","ITUB")

}
  
if (collect_since == "none"){
    
  collect_since <-  "2005-01-01"
    
}  

 


underlyings <- list()

underlyings_price <-list()
underlying_price <- list()
volumes   <-  list()
volume    <-  list()

for (cntr in seq(1,length(tickers_equity))){
  
  underlying_price <- fetchData(tickers_equity[cntr],"yahoo",collect_since)
  
  
  if (cntr == 1){
    
    underlyings_price <- underlying_price$Adjusted
    volumes  <- underlying_price$Volume
    
  } else {
    
    underlyings_price <- merge.xts(underlyings_price,underlying_price$Adjusted)
    volumes <- merge.xts(volumes,underlying_price$Volume)
  }
  
 
  
}

colnames(underlyings_price) <- tickers_equity
colnames(volumes) <- tickers_equity


underlyings_price <- na.locf(underlyings_price)
underlyings_price <- na.locf(underlyings_price, fromLast = TRUE)

volumes <- na.locf(volumes)
volumes <- na.locf(volumes, fromLast = TRUE)



logReturns <- diff(log(underlyings_price), lag=1 )


#correlation <- cor(logReturns, use = "complete")
#corrplot(correlation, method="color")

underlyings$price <- (underlyings_price)
underlyings$volume <- (volumes)
underlyings$logReturn <- (logReturns)

return (underlyings)

}



