library(kernlab)
library(Matrix)
library(ggplot2)
train <-as.matrix(read.csv('D:\\Users\\User\\Desktop\\KFLD\\orl_train.csv'))
test <- as.matrix(read.csv('D:\\Users\\User\\Desktop\\KFLD\\orl_test.csv'))
B <-  as.matrix(read.csv('D:\\Users\\User\\Desktop\\KFLD\\B.csv'))
testY <- test[,10305]
trainY <- train[,10305]
#train<-scale(train[,1:10304],scale = FALSE)
#test<-scale(test[,1:10304],scale = FALSE)

bestACC=0
for (d in 6:20){
  #for (s in 1:10){
    #for (o in seq(0,300,10) ){
      #kernelf <- polydot(degree = d, scale = 1,offset = 0)
      kernelf <- rbfdot(sigma = 10^-d)
      k<-kernelMatrix(kernel = kernelf,x = train[,1:10304])
      K_pre<-kernelMatrix(kernel = kernelf,test[,1:10304],train[,1:10304])
      
      k_inv <- solve(k)
      kk <- k%*%k
      kk_inv <- solve(kk)
      kbk <- k%*%B%*%k
      a <-eigen(kk_inv%*%kbk)$vectors[,c(1,3)]
      U <-svd(B)$u
      a2<-k_inv%*%U
      a<-a2
      
      project <- (Re(k%*%a)^2)^0.5
      #qplot(project[,1:1],project[,2:2], colour = as.factor(trainY), xlab="Discr 1", 
      #ylab="Discr 2")+geom_point(size=0.5)+geom_text(aes(label=as.factor(trainY)),hjust=0, vjust=0)
      
      
      predict<- (Re(K_pre%*%a)^2)^0.5
      #qplot(predict[,1:1],predict[,2:2], colour = as.factor(testY), xlab="Discr 1", 
      #ylab="Discr 2")+geom_point(size=0.5)+geom_point(size=0.5)+geom_text(aes(label=as.factor(testY)),hjust=0, vjust=0)
      
      
      p <- array(0,dim=c(280,1))
      
      
      for (i in 1:280){
        min = 1000000000000000000000000000000000
        for (j in 1:120){
          totalD = 0
          for (n in 1:120){
            totalD = totalD+ (predict[i,n:n]-project[j,n:n])**2
          }
          if (totalD<=min){
            min = totalD
            p[i]= trainY[j]
          }
        }
      }
      cat(d,mean(p==testY),'\n')
      if(mean(p==testY)>bestACC){
        bestACC = mean(p==testY)
        bestd = d
       # bests = s
       # besto = o
      }
      
    #}
  #}
}
cat(bestd,bests,besto,bestACC)

install.packages("plotly")
