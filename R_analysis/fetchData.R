fetchData <- function (ticker = "GS", dataSource = "yahoo", collect_since = "2001-01-01"){
# load some data from quantmod
library(quantmod)
library(xts)



getSymbols(ticker, src = dataSource, from = collect_since)

price_data <- eval(parse(text = ticker))

colnames(price_data) <- c("Open", "High", "Low" ,"Close", "Volume","Adjusted")

chartSeries(price_data)


return (price_data)


}