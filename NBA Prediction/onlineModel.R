library(ggplot2)
library(GGally)
library(lars)
library(glmnet)
library(tree)
library(e1071)
library(RSNNS)
library(xgboost)

df<-read.csv('D:\\Users\\User\\Desktop\\Statistical Learning\\Final project\\crawler\\Feature\\Feature_2weekpast.csv')

p.lm<-numeric()
p.elastic<-numeric()
p.tree<-numeric()
p.svr<-numeric()
p.mlp<-numeric()
p.xgb<-numeric()
train.index<-800

for (i in seq(0:300)){
  cat('------------------',train.index,'----------------')
  train.index<-train.index+1
  
  test.index<-train.index+1
  
  train <- df[1:train.index,]
  test <- df[test.index,]
  
  x.train <-as.matrix(train[,-c(127,128,129,130,131,132)])
  y.train  <-train$point_range
  
  x.test<-as.matrix(test[,-c(127,128,129,130,131,132)])
  y.test<-test$point_range
  
  #------lm-------
  m.lm<-lm(formula = y.train~.,data = as.data.frame(x.train),x = TRUE)
  p.lm<-append(p.lm,predict(m.lm,as.data.frame(x.test)))
  
  
  #------elnet------
  fit.elnet.cv <- cv.glmnet(x.train, y.train, type.measure="mse", alpha=.9,family="gaussian")
  p.elastic<-append(p.elastic,predict(fit.elnet.cv,x.test))
  
  #------tree-------
  tmodel<-tree(y.train~.,as.data.frame(x.train))
  prune.tmodel <- prune.tree(tmodel,best=5)
  p.tree<-append(p.tree,predict(prune.tmodel,as.data.frame(x.test)))
  
  #------svr--------
  model.tune <- svm(y.train ~ . , x.train,epsilon=0,cost=0.2)
  p.svr<-append(p.svr,predict(model.tune,x.test))
  
  #------nn-------
  s<-10
  c<-0.00001
  itr<-200
  model.mlp <- mlp(x.train, y.train, size=s, learnFuncParams=c(c), 
                   maxit=itr,targetsTest = y.test,inputsTest = x.test,metric="RSME",linOut = TRUE)
  p.mlp<-append(p.mlp,predict(model.mlp,x.test))
  
  #------xgboost----
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
  p.xgb <- append(p.xgb,predict(xgb_model,dtest))

}

predict.ensemble<-(p.lm+p.elastic+p.tree+p.mlp+p.svr+p.xgb)/6
mean((predict.ensemble-df[802:1102,]$point_range)^2)




