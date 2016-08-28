library(randomForest)

f = read.csv(file="RustSurvey+EarthEngine.csv")

# Create training set that is 2010 severe yellow rust
#  and 2010 no rust (of any type)
f1 = f[f$ObsYear==2010 & f$YellowRust.Severity==3,]
f1 = rbind(f1, f[f$ObsYear==2010 & f$NoRust.Binary=="True",])

# Reorder in random order
#  and keep only first/random observation when dupped lat/long 
f1 = f1[sample(nrow(f1)),] 
f1 = f1[!duplicated(paste(f1$Latitude, f1$Longitude)),]

# Select out non-null remote sensing features
features = c(43:51, 53:56, 58:111, 121:156, 166:886)

# Train on 50% of data, test on remainder
train = sample(1:nrow(f1), nrow(f1)/2)
tr = na.roughfix(f1[train,features])
v = na.roughfix(f1[-train,features])
YellowRust = as.factor(f1$YellowRust.Binary=="True")

# fit model
m =  randomForest(tr, y=YellowRust[train],  xtest=v, ytest=YellowRust[-train], importance=T, do.trace=T)

# See model output, contengency table
m

# ROC curve, need external lib
#ROCPlot(m$test$votes[,2], YellowRust[-train]==TRUE)

# Variable importance
varImpPlot(m, type=1)

# Visualize TRMM IRprecipitation feature from Sept
plot(density(f1$TRMM_3B42_18_IRprecipitation[YellowRust==FALSE], na.rm=T), col=3
, main="2010 TRMM_3B42_18_IRprecipitation")
lines(density(f1$TRMM_3B42_18_IRprecipitation[YellowRust==TRUE], na.rm=T), col=2
)
legend("topright", c("Severe Yellow", "None"), col=2:3, lty=1)

