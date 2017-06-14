 # -*- coding: utf-8 -*-. 
import pandas as pd 
import io
def get_game_id(year):
	df = pd.read_csv('.\\Schedule\\'+year+'_processed_schedule.csv')
	id_list = list()
	for i in xrange(0,len(df)):
		id_list.append((df.loc[i,'id']+'_A_players.csv',df.loc[i,'id']+'_H_players.csv',df.loc[i,'id']+'_team.csv'))
	return id_list

def get_data(year='2016',n=0,type=0):
	return pd.read_csv('.\\GameCsv\\'+get_game_id(year)[n][type])

def write_colName():
	with io.open('.\\GameCsv\\ColumnName.txt', 'w') as f:
		f.write(u'Player stat column name:'+'\n')
		for col in get_data().columns:
			f.write(unicode(col)+'\n')
		f.write(u'--------------------------------------------'+'\n')
		f.write(u'Team stat column name:'+'\n')
		for col in get_data(type=2).columns:
			f.write(unicode(col)+'\n')

def process_meta_data():
	df = pd.read_csv('.\\Schedule\\2016_processed_schedule.csv')
	for i in xrange(0,len(df)):
		print i
		if i!=265 and i!=558 and i!=943 :
			if i == 0:
				# print get_data(n=i,type=0).columns
				# print get_data(n=i,type=1).columns
				away_player = get_data(n=i,type=0)
				away_player['game_id'] = df.loc[i,'id']
				home_player = get_data(n=i,type=1)
				home_player['game_id'] = df.loc[i,'id']
				meta_df=away_player
				meta_df=pd.concat([meta_df,home_player])
			else :
				# print get_data(n=i,type=0).columns
				# print get_data(n=i,type=1).columns
				away_player = get_data(n=i,type=0)
				away_player['game_id'] = df.loc[i,'id']
				home_player = get_data(n=i,type=1)
				home_player['game_id'] = df.loc[i,'id']
				meta_df=pd.concat([meta_df,away_player])
				meta_df=pd.concat([meta_df,home_player])

	meta_df.index = range(len(meta_df))
	meta_df.to_csv('.\\PlayerMeta-Data\\AllPlayer.csv',index=False)

def save_team_playerID_csv():
	df = pd.read_csv('.\\PlayerMeta-Data\\AllPlayer.csv')
	team_list = df['team'].unique()
	d = {}
	for team in team_list:
		d[team] = df[df['team']==team]['id'].unique()
	team_player_id = pd.DataFrame.from_dict(d,orient = 'index').T.drop('WEST',1).drop('EAST',1)
	team_player_id.to_csv('.\\PlayerMeta-Data\\team_player_id.csv',index=False)

def get_team_playerID(Team):
	df = pd.read_csv('.\\PlayerMeta-Data\\team_player_id.csv')
	return df[Team].dropna()

#產出的資料根據近兩週
def cal_average_player_stat(game_start_played_date,game_played_date):
	game_date = pd.to_datetime(game_played_date)
	game_start_date = pd.to_datetime(game_start_played_date)
	df = pd.read_csv('.\\PlayerMeta-Data\\AllPlayer.csv')
	df['date'] =  pd.to_datetime( df['date'])
	df['minutes'] = df['minutes'] .apply(lambda x: x[:-3]).replace('1:00','60').astype(int)
 	
	# team_played = df[(df['date']<game_date)]['team'].unique()
	player_id = df[(df['date']>game_start_date)&(df['date']<game_date)]['id'].unique()

	t = 0 
	for i in player_id:
		if t == 0:
			player_stat = pd.DataFrame(df[(df['date']>game_start_date)&(df['date']<game_date)&(df['id']==i)].mean()).T.drop('jersey_number',1)
			player_stat['id'] = i
			# player_stat['primary_position'] = df[(df['date']<game_date)&(df['id']==i)]['primary_position'].dropna().unique()
			player_stat['before_date'] = game_date
			save = player_stat
		else:
			player_stat = pd.DataFrame(df[(df['date']>game_start_date)&(df['date']<game_date)&(df['id']==i)].mean()).T.drop('jersey_number',1)
			player_stat['id'] = i
			# player_stat['primary_position'] = df[(df['date']<game_date)&(df['id']==i)]['primary_position'].dropna().unique()
			player_stat['before_date'] = game_date
			save = pd.concat([save,player_stat])
		t+=1
	save.to_csv('.\\Player_stat\\'+game_played_date+'.csv',index=False)
#產出的每天資料根據近兩週記錄算平均
def generate_all_date_average():
	date = get_dateList_gameList()[0]
	for i in xrange(14,len(get_dateList_gameList()[0])):
		print date[i],date[i-13],'-----',i,'------',len(get_dateList_gameList()[0]),'-----'
		cal_average_player_stat(date[i-13],date[i])
	
def get_dateList_gameList():
	df = pd.read_csv('.\\Schedule\\2016_processed_schedule.csv')
	game_date_list = df['date'].unique()
	game_id_list = list()
	for d in game_date_list:
		game_id_list.append(df[df['date']==d]['id'])
	return game_date_list,game_id_list,len(game_date_list)

def get_playerID_of_game(date,game_id):
	df = pd.read_csv('.\\PlayerMeta-Data\\AllPlayer.csv')
	H = df[(df['game_id']==game_id)&(df['location']=='H')&(df['date']==date)].sort_values('id').drop_duplicates('id')[['id','primary_position','team','points']]
	A = df[(df['game_id']==game_id)&(df['location']=='A')&(df['date']==date)].sort_values('id').drop_duplicates('id')[['id','primary_position','team','points']]
	
	return H,A

#Home_player_id,Away_player_id,Home_pos,Away_pos,Home_points,Away_points comes from game to be predicted
#feature date is last date of game
def feature_extraction(feature_date,Home_player_id,Away_player_id,Home_pos,Away_pos):
	df = pd.read_csv('.\\Player_stat\\'+feature_date+'.csv')

	home_feature_player_id = df[df['id'].isin(Home_player_id)].sort_values('id')['id'].tolist()
	away_feature_player_id = df[df['id'].isin(Away_player_id)].sort_values('id')['id'].tolist()
 	
 	homepos = list()
 	awaypos = list()
 	for i in xrange(len(Home_player_id)):
 		if Home_player_id.tolist()[i] in home_feature_player_id :
 			homepos.append(Home_pos.tolist()[i])
 	
 	for i in xrange(len(Away_player_id)):
 		if Away_player_id.tolist()[i] in away_feature_player_id:
 			awaypos.append(Away_pos.tolist()[i])
 	# print len(away_feature_player_id),len(awaypos)
 	# print len(Away_player_id),len(Away_pos)
 	# print away_feature_player_id
 	# print Away_player_id

 	home_data = df[df['id'].isin(Home_player_id)].sort_values('id').drop('assists_turnover_ratio',1).drop('field_goals_pct',1)\
 				.drop('free_throws_pct',1).drop('oppo_points',1).drop('points',1)\
 				.drop('three_points_pct',1).drop('two_points_pct',1).drop('id',1)\
 				.drop('before_date',1)

 	home_data['primary_position'] = homepos

 	away_data = df[df['id'].isin(Away_player_id)].sort_values('id').drop('assists_turnover_ratio',1).drop('field_goals_pct',1)\
 				.drop('free_throws_pct',1).drop('oppo_points',1).drop('points',1)\
 				.drop('three_points_pct',1).drop('two_points_pct',1).drop('id',1)\
 				.drop('before_date',1)
 	away_data['primary_position'] = awaypos
 	
 	home_data = home_data.sort_values('minutes',ascending=False)
 	home_data.index = range(len(home_data))
 	home_data = home_data.sort_values('primary_position')
 	home_data.index = range(len(home_data))

 	away_data = away_data.sort_values('minutes',ascending=False)
 	away_data.index = range(len(away_data))
 	away_data = away_data.sort_values('primary_position')
 	away_data.index = range(len(away_data))

 	# print home_data,away_data
 	# print home_data
 	if len(home_data[home_data['primary_position']=='PG'].drop('primary_position',1))>0:
 		home_PG = home_data[home_data['primary_position']=='PG'].drop('primary_position',1).iloc[0]
 	else:home_PG = home_SG
 	if len(home_data[home_data['primary_position']=='SG'].drop('primary_position',1))>0:
	 	home_SG = home_data[home_data['primary_position']=='SG'].drop('primary_position',1).iloc[0]
	else:home_SG = home_SF
	if len(home_data[home_data['primary_position']=='SF'].drop('primary_position',1))>0:
	 	home_SF = home_data[home_data['primary_position']=='SF'].drop('primary_position',1).iloc[0]
	else:home_SF = home_SG
	if len(home_data[home_data['primary_position']=='PF'].drop('primary_position',1))>0:
	 	home_PF = home_data[home_data['primary_position']=='PF'].drop('primary_position',1).iloc[0]
	else:home_PF = home_C
	if len(home_data[home_data['primary_position']=='C'].drop('primary_position',1))>0:
	 	home_C = home_data[home_data['primary_position']=='C'].drop('primary_position',1).iloc[0]
 	else:home_C = home_PF
 	home_total = home_data.drop('primary_position',1).mean()
 	
 	if len(away_data[away_data['primary_position']=='PG'].drop('primary_position',1))>0:
 		away_PG = away_data[away_data['primary_position']=='PG'].drop('primary_position',1).iloc[0]
 	else:away_PG = away_SG
 	if len(away_data[away_data['primary_position']=='SG'].drop('primary_position',1))>0:
	 	away_SG = away_data[away_data['primary_position']=='SG'].drop('primary_position',1).iloc[0]
	else:away_SG = away_SF
	if len(away_data[away_data['primary_position']=='SF'].drop('primary_position',1))>0:
	 	away_SF = away_data[away_data['primary_position']=='SF'].drop('primary_position',1).iloc[0]
	else:away_SF = away_SG
	if len(away_data[away_data['primary_position']=='PF'].drop('primary_position',1))>0:
	 	away_PF = away_data[away_data['primary_position']=='PF'].drop('primary_position',1).iloc[0]
	else:away_PF = away_C
	if len(away_data[away_data['primary_position']=='C'].drop('primary_position',1))>0:
	 	away_C = away_data[away_data['primary_position']=='C'].drop('primary_position',1).iloc[0]
 	else:away_C = away_PF
 	away_total = away_data.drop('primary_position',1).mean()
 	# print away_PG,away_SG,home_SF-away_SF,away_PF,away_C

 	PG = pd.DataFrame(home_PG-away_PG).T
 	PG.columns = 'PG_'+PG.columns
 	PG.index = [0]
 	SG = pd.DataFrame(home_SG-away_SG).T
 	SG.columns = 'SG_'+SG.columns
 	SG.index = [0]
 	SF = pd.DataFrame(home_SF-away_SF).T
 	SF.columns = 'SF_'+SF.columns
 	SF.index = [0]
 	PF = pd.DataFrame(home_PF-away_PF).T
 	PF.columns = 'PF_'+PF.columns
 	PF.index = [0]
 	C = pd.DataFrame(home_C-away_C).T
 	C.columns = 'C_'+C.columns
 	C.index = [0]
 	all_team_avg = pd.DataFrame(home_total-away_total).T
 	all_team_avg.columns = 'all_'+all_team_avg.columns
 	all_team_avg.index = [0]

 	feature = pd.concat([PG, SG, SF, PF, C, all_team_avg], axis=1, ignore_index=False)
 	feature['feature_date']=feature_date
 	

 	return feature
 	
def generate_all_feature():
	game_date_and_id = get_dateList_gameList()
	feature = pd.DataFrame()
	# date start at 4 
	for i in xrange(15,game_date_and_id[2]):
		# game
		for g in game_date_and_id[1][i]:   
			if g!='f7f75604-08bf-4e5b-9705-8001f5961b09' and g!='0d26193c-9148-4c14-a55b-c36bef14fe45' and g!='93799eea-008f-4dba-98ee-01c92d7a1bb5' :
				# get game to be predicted players information
				H,A=get_playerID_of_game(game_date_and_id[0][i],g)
				# get feature by last day
				f = feature_extraction(game_date_and_id[0][i-1],H['id'],A['id'],H['primary_position'],A['primary_position'])
				f['point_range'] = H['points'].unique()-A['points'].unique()
				f['H_team'] = H['team'].unique()
				f['A_team'] = A['team'].unique()
				f['predict_game_id'] = g
				f['predict_date'] = game_date_and_id[0][i]
				f['feature_date'] = game_date_and_id[0][i-1]
				feature = pd.concat([feature,f])
				print '----',i,'----',len(feature),'----'
				# print feature.columns
			
	feature.index = range(len(feature))
	feature.to_csv('.\\Feature\\Feature_2weekpast.csv',index=False)

if __name__ == '__main__':
	
	generate_all_date_average()	
	generate_all_feature()


	#根據該場比賽的ID抓該場比賽有哪些球員對陣以及勝分差(H-A)
 	#feature為該場比賽球員上一個日期的平均數據相減(H-A)