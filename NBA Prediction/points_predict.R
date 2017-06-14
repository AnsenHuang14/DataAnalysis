library(ggplot2)
library(GGally)
library(lars)
library(glmnet)
library(tree)
library(e1071)
library(RSNNS)
library(xgboost)

df<-read.csv('D:\\Users\\User\\Desktop\\Statistical Learning\\Final project\\crawler\\Feature\\Feature_2weekpast.csv')
dim(df)
train <- df[1:800,]
test <- df[801:1130,]

x.train <-as.matrix(train[,-c(127,128,129,130,131,132)])
y.train  <-train$point_range

x.test<-as.matrix(test[,-c(127,128,129,130,131,132)])
y.test<-test$point_range

summary(df)
colnames(df)
colnames(x.train)
head(df)
ggcorr(df[,-c(127,129,130,131,132)],legend.size = 0.1)
cor(df[,-c(127,129,130,131,132)],df$point_range)

#---------------pca------------------
pca <- prcomp(formula = ~ .,   
              data = df[,-c(127,128,129,130,131,132)],                           
              scale = TRUE)       
props <- pca$sdev^2 / sum(pca$sdev^2)    
cumulative.props <- cumsum(props)
plot(cumulative.props)

#--------------lm--------------
m<-lm(formula = train$point_range~.,data = train[,-c(127,128,129,130,131,132)],
       x = TRUE)
sqrt(sum(m$residuals^2)/length(train))
mean((predict(m,test[,-c(127,128,129,130,131,132)])-test$point_range)^2)

#-----------Elastic Net----------

# Fit models:
fit.lasso <- glmnet(x.train, y.train, family="gaussian", alpha=1)
fit.ridge <- glmnet(x.train, y.train, family="gaussian", alpha=0)
fit.elnet <- glmnet(x.train, y.train, family="gaussian", alpha=.5)


# 10-fold Cross validation for each alpha = 0, 0.1, ... , 0.9, 1.0
fit.lasso.cv <- cv.glmnet(x.train, y.train, type.measure="mse", alpha=1, 
                          family="gaussian")
fit.ridge.cv <- cv.glmnet(x.train, y.train, type.measure="mse", alpha=0,
                          family="gaussian")
fit.elnet.cv <- cv.glmnet(x.train, y.train, type.measure="mse", alpha=.5,
                          family="gaussian")

for (i in 0:10) {
  assign(paste("fit", i, sep=""), cv.glmnet(x.train, y.train, type.measure="mse", 
                                            alpha=i/10,family="gaussian"))
}
# Plot solution paths:
par(mfrow=c(3,2))
# For plotting options, type '?plot.glmnet' in R console
plot(fit.lasso, xvar="lambda")
plot(fit10, main="LASSO")

plot(fit.ridge, xvar="lambda")
plot(fit0, main="Ridge")

plot(fit.elnet, xvar="lambda")
plot(fit5, main="Elastic Net")

yhattrain <- predict(fit9, s=fit9$lambda.1se, newx=x.train)
msetrain <- mean((y.train - yhattrain)^2)
msetrain
yhat0 <- predict(fit0, s=fit0$lambda.1se, newx=x.test)
yhat1 <- predict(fit1, s=fit1$lambda.1se, newx=x.test)
yhat2 <- predict(fit2, s=fit2$lambda.1se, newx=x.test)
yhat3 <- predict(fit3, s=fit3$lambda.1se, newx=x.test)
yhat4 <- predict(fit4, s=fit4$lambda.1se, newx=x.test)
yhat5 <- predict(fit5, s=fit5$lambda.1se, newx=x.test)
yhat6 <- predict(fit6, s=fit6$lambda.1se, newx=x.test)
yhat7 <- predict(fit7, s=fit7$lambda.1se, newx=x.test)
yhat8 <- predict(fit8, s=fit8$lambda.1se, newx=x.test)
yhat9 <- predict(fit9, s=fit9$lambda.1se, newx=x.test)
yhat10 <- predict(fit10, s=fit10$lambda.1se, newx=x.test)

mse0 <- mean((y.test - yhat0)^2)
mse1 <- mean((y.test - yhat1)^2)
mse2 <- mean((y.test - yhat2)^2)
mse3 <- mean((y.test - yhat3)^2)
mse4 <- mean((y.test - yhat4)^2)
mse5 <- mean((y.test - yhat5)^2)
mse6 <- mean((y.test - yhat6)^2)
mse7 <- mean((y.test - yhat7)^2)
mse8 <- mean((y.test - yhat8)^2)
mse9 <- mean((y.test - yhat9)^2)
mse10 <- mean((y.test - yhat10)^2)

mse0
mse1
mse2
mse3
mse4
mse5
mse6
mse7
mse8
mse9#--best--
mse10

#----------------TREE-------------------
par(mfrow=c(1,1))
tmodel<-tree(y.train~.,as.data.frame(x.train))
plot(tmodel)
text(tmodel)

cv.tree(tmodel,K=10)
prune.tmodel <- prune.tree(tmodel,best=5)
plot(prune.tmodel)
text(prune.tmodel)

mean((predict(prune.tmodel,as.data.frame(x.train))-y.train)^2)
mean((predict(prune.tmodel,as.data.frame(x.test))-y.test)^2)
mean((predict(tmodel,as.data.frame(x.test))-y.test)^2)

#------------SVR--------------
model <- svm(y.train ~ . , x.train)
mean((predict(model,x.test)-y.test)^2)
summary(model)
#tuning
tuneResult <- tune(svm, y.train ~ .-y.train ,data=cbind(train[,-c(127,128,129,130,131,132)],y.train) ,
                   ranges = list(epsilon = seq(0,1,0.1), cost = seq(0.1,2,0.1))
)
print(tuneResult)
plot(tuneResult)
#cost 0.2,eps 0
model.tune <- svm(y.train ~ . , x.train,epsilon=tuneResult$best.parameters$epsilon,cost=tuneResult$best.parameters$cost)
mean((predict(model.tune,x.test)-y.test)^2)
mean((predict(model.tune,x.train)-y.train)^2)
summary(model.tune)

#-------------NN--------------
#tuning s c itr
for (s in c(1,3,5,10,15)){
  for (c in c(0.1,0.01,0.001,0.0001,0.00001)){
    for (itr in c(100,150,200,250)){
      model.mlp <- mlp(x.train, y.train, size=s, learnFuncParams=c(c), 
             maxit=itr,targetsTest = y.test,inputsTest = x.test,metric="RSME",linOut = TRUE)

      #model.mlp$fitted.values
      cat(s,c,itr,sum((model.mlp$fittedTestValues-y.test)^2)/length(y.test),sum((model.mlp$fitted.values-y.train)^2)/length(y.train),'\n')
      
    }
  }
}
#best 
s<-10
c<-0.00001
itr<-200
model.mlp <- mlp(x.train, y.train, size=s, learnFuncParams=c(c), 
                 maxit=itr,targetsTest = y.test,inputsTest = x.test,metric="RSME",linOut = TRUE)
plotIterativeError(model.mlp)
print(sum((model.mlp$fittedTestValues-y.test)^2)/length(y.test))
print(sum((model.mlp$fitted.values-y.train)^2)/length(y.train))

#------------XGboost-----------
rounds <- 2000
param <- list(objective="reg:linear",
              eval_metric = "rmse",
              eta = .05,
              gamma = 1,
              max_depth = 4,
              min_child_weight = 1,
              subsample = .7,
              colsample_bytree = .7)
dtrain <- xgb.DMatrix(data=x.train, label=y.train)
dtest <- xgb.DMatrix(data=x.test)

cat("XGB training")
xgb_model <- xgb.train(data = dtrain,
                       params = param,
                       watchlist = list(train = dtrain),
                       nrounds = rounds,
                       verbose = 1,
                       print.every.n = 5
)
# Feature importance
cat("Plotting feature importance")
names <- dimnames(x.train)[[2]]
importance_matrix <- xgb.importance(names,model=xgb_model)
xgb.plot.importance(importance_matrix[1:25,])

# Predict and output csv
cat("Predictions")
preds <- predict(xgb_model,dtest)
predstrain <- predict(xgb_model,dtrain)
mean((predstrain-y.train)^2)
mean((preds-y.test)^2)

predict(xgb_model,dtrain)

#------ensemble1------

predict.elastic <-yhat9
predict.tree <-predict(prune.tmodel,as.data.frame(x.test))
predict.svr <-predict(model.tune,x.test)
predict.mlp<-model.mlp$fittedTestValues
predict.xgb<-predict(xgb_model,dtest)

predict.train.elastic <-yhattrain
predict.train.tree <-predict(prune.tmodel,as.data.frame(x.train))
predict.train.svr <-predict(model.tune,x.train)
predict.train.mlp<-model.mlp$fitted.values
predict.train.xgb<-predict(xgb_model,dtrain)

predict.ensemble <- (predict.elastic+predict.tree+predict.svr+predict.mlp+predict.xgb)/5
predict.train.ensemble <- (predict.train.elastic+predict.train.tree+predict.train.svr+predict.train.mlp+predict.train.xgb)/5
mean((predict.ensemble-y.test)^2)
mean((predict.train.ensemble-y.train)^2)
qplot(predict.ensemble,y.test)

#------ensemble 2-----
#---not add xgboost---because xgboost mse of training set is almost 0
ensemble.train<-as.data.frame(cbind(y.train,predict.train.elastic,predict.train.tree,predict.train.svr,predict.train.mlp,predict.train.xgb))
ensemble.test<-as.data.frame(cbind(predict.elastic,predict.tree,predict.svr,predict.mlp,predict.xgb))
colnames(ensemble.train)
colnames(ensemble.test)<-colnames(ensemble.train)[2:6]
ensemble.m<-lm(formula = ensemble.train$y.train~.,data = as.data.frame( ensemble.train[,-c(1)]),
      x = TRUE)
mean(ensemble.m$residuals^2)
mean((predict(ensemble.m,ensemble.test)-y.test)^2)




