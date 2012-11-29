a <- read.csv("/Users/dbr/Documents/Dropbox/strava_python/to_r.csv")
a$startDate <- as.POSIXct(a$startDate, origin="1970-01-01")

a <- subset(a, averageSpeed > 0)

summary(a)

f_hr <- subset(a, heartrateMin > -1)

res <- lm(f_hr$heartrateMin ~ f_hr$startDate)
plot(f_hr$startDate, f_hr$heartrateMin, type="l", xlab = "date", ylab = "HR min")
title("HR min over time")
abline(res)


res <- lm(f_hr$heartrateMax ~ f_hr$startDate)
plot(f_hr$startDate, f_hr$heartrateMax, type="l", xlab = "date", ylab = "HR max")
title("HR max over time")
abline(res)

res <- lm(f_hr$heartrateAvg ~ f_hr$startDate)
plot(f_hr$startDate, f_hr$heartrateAvg, type="l", xlab = "date", ylab = "HR avg")
title("HR avg over time")
abline(res)


res <- lm(a$averageSpeed ~ a$startDate)
plot(a$startDate, a$averageSpeed, type='l')
title("Avg speed over time")
abline(res)

smoothed <- smooth.spline(x=a$startDate, y=a$averageSpeed)
smoothed$x <- as.POSIXct(smoothed$x, origin="1970-01-01")
a$averageSpeedSmoothed <- smoothed$y
plot(a$startDate, a$averageSpeed, type='l')
lines(smoothed$x, a$averageSpeedSmoothed)
title("Avg speed (smoothed) over time")

f_watts <- subset(a, averageWatts> -1)
res <- lm(f_watts$averageWatts ~ f_watts$startDate)
plot(f_watts$startDate, f_watts$averageWatts, type='l')
title("Avg power (W) over time")
abline(res)
scatter.smooth(x = f_watts$startDate, y=f_watts$averageWatts)


f_avgtemp <- subset(a, temperatureAvg> -1)
plot(f_avgtemp$startDate, f_avgtemp$temperatureAvg, type='l')
title("Avg temperature over time")


f_cadence <- subset(a, cadenceAvg> -1)
plot(f_cadence$startDate, f_cadence$cadenceAvg, type='l')
title("Avg cadence over time")

f_cadence <- subset(a, cadenceAvg> -1)
plot(f_cadence$startDate, f_cadence$cadenceAvgNonZero, type='l')
title("Non-zero Avg cadence over time")


plot(a$distance, a$averageSpeed)
title("Distance vs average speed")