library("rjson")

url <- "http://app.strava.com/api/v1/streams/16631415?streams[]=cadence,time"

d <- as.data.frame(fromJSON(paste(readLines(url))))

d$sample.time <- 0
d$sample.time[2:nrow(d)] <- d$time[2:nrow(d)]-d$time[1:(nrow(d)-1)]

hist(rep(x=d$cadence, times=d$sample.time),
     main="Histogram of Cadence", xlab="Cadence (RPM)",
     ylab="Time (presumably seconds)")

