library(ggplot2)
library(GGally)

shot_log <-read.csv('D:\\Users\\User\\Desktop\\Statistical Learning\\Final project\\shot_logs.csv')
colnames(shot_log)
#correct data (touchtime and shotresult)
shot_log<-shot_log[shot_log$TOUCH_TIME>0,][,-c(14,21,16)]
summary(shot_log)

#get all defender names to evaulate defend performance
defender_list <- levels(shot_log$CLOSEST_DEFENDER)
attcker_list <- levels(shot_log$player_name)

#?‰¾?‡º??ƒå“¡?›¸???,?–®??“å‘½ä¸­ç?‡æ?€é«˜ç?ƒå“¡,å®¢å ´æ®ºæ??,ä¸»å ´æ®ºæ??,??œéµ??‚åˆ»æ®ºæ??
#??ƒå“¡?›¸???(?¸?‡º?‡º??‹æ•¸å¤ å?šå?Šé˜²å®ˆæ•¸å¤ å?šç?„ç?ƒå“¡,???10??ƒä»¥ä¸?)
player_versus <- data.frame(attacker = character(), defender = character(),FG_rate = numeric(),
                            avg_shot_dist=numeric(),avg_def_dist=numeric(),shot_number=numeric(),
                            dribbles = numeric(),touch_time = numeric())
for(player_name in attcker_list){
  for(defender in defender_list){
    if (length(shot_log[shot_log$player_name==player_name&shot_log$CLOSEST_DEFENDER==defender,'FGM']
        )>=10){
    FG_rate <- mean(shot_log[shot_log$player_name==player_name&shot_log$CLOSEST_DEFENDER==defender,'FGM'])
    avg_shot_dist <- mean(shot_log[shot_log$player_name==player_name&shot_log$CLOSEST_DEFENDER==defender,'SHOT_DIST'])
    avg_def_dist <- mean(shot_log[shot_log$player_name==player_name&shot_log$CLOSEST_DEFENDER==defender,'CLOSE_DEF_DIST'])
    shot_number <- length(shot_log[shot_log$player_name==player_name&shot_log$CLOSEST_DEFENDER==defender,'FGM'])
    dribbles <- mean(shot_log[shot_log$player_name==player_name&shot_log$CLOSEST_DEFENDER==defender,'DRIBBLES'])
    touch_time <- mean(shot_log[shot_log$player_name==player_name&shot_log$CLOSEST_DEFENDER==defender,'TOUCH_TIME'])
    
    print(data.frame(attacker=player_name,defender,FG_rate,avg_shot_dist,avg_def_dist,shot_number,dribbles,touch_time))
    player_versus<-rbind(player_versus,data.frame(attacker=player_name,defender,FG_rate,avg_shot_dist,avg_def_dist,shot_number,
                                                  dribbles,touch_time))
    }
  }
}
head(player_versus)
summary(player_versus)
ggpairs(player_versus[,-c(1,2)])
for (p in defender_list){
  if (length(player_versus[player_versus$defender==p,'FG_rate'])>0){
    s<-summary(player_versus[player_versus$defender==p,'FG_rate'])
    cat(p,'range',s[6]-s[1],'\t','mean',s[4],'\n')
  }
}

  

