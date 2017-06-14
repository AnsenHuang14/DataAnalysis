library(ggplot2)
library(GGally)

player_stat <-read.csv('D:\\Users\\User\\Desktop\\Statistical Learning\\Final project\\players_stats.csv')
free_throw <-read.csv('D:\\Users\\User\\Desktop\\Statistical Learning\\Final project\\free_throws.csv')


#select stars player
player_stat<-player_stat[player_stat$MIN>=2000,]

summary(player_stat)
colnames(player_stat)
head(player_stat)

#drop Name,Birth_Place,Birthdate,Collage
player_stat[,-c(1,26,27,28)]

#pairs plot of  Games.Played,Min,PTS,FG.,X3P.,FT.,AST,Pos,Age,AST.TOV,EFF
ggpairs(player_stat[,c(2,3,4,7,9,13,17,23,25,31,22)])

#implement PCA to evaluate a player performance
pca <- prcomp(formula = ~ MIN+PTS+FG.+X3P.+FT.+FTA+AST+STL+EFF,   
              data = player_stat,                           
              scale = TRUE)       
props <- pca$sdev^2 / sum(pca$sdev^2)    
cumulative.props <- cumsum(props)
plot(cumulative.props)
plot(pca$rotation[,1])
qplot(pca$x[,1],pca$x[,2])+geom_text(aes(label=player_stat$Name))

