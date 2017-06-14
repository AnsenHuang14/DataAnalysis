import pandas as pd 
import requests 
import ConfigParser
from bs4 import BeautifulSoup 
import io,json
import ast
from time import sleep


def schedule_crawl(year):
	api_key = "u8c9qef5z97skfay6h8ry45n"
	res = requests.get("https://api.sportradar.us//nba-t3/games/"+year+"/REG/schedule.json?api_key="+api_key)
	with io.open('.\\Schedule\\'+year+'_schedule'+'.json', 'w') as f:
		f.write(res.text)

def read_schedule_json_toDF(year):
	with io.open('.\\Schedule\\'+year+'_schedule.json') as f:
		table = json.loads(f.read())
		pd.DataFrame(table['games']).to_csv('.\\Schedule\\'+year+'_schedule.csv')

def get_processed_schedule(year):#get team_id,game_id
	table = pd.read_csv('.\\Schedule\\'+year+'_schedule.csv')
	table['home_id'] = table['home'].apply(lambda x: ast.literal_eval(x)['id'])
	table['away_id'] = table['away'].apply(lambda x: ast.literal_eval(x)['id'])
	table['date'] = table['scheduled'].apply(lambda x: x[0:10])
	table['home'] = table['home'].apply(lambda x: ast.literal_eval(x)['alias'])
	table['away'] = table['away'].apply(lambda x: ast.literal_eval(x)['alias'])
	table = table[['date','home','away','home_id','away_id','id']]
	table.to_csv('.\\Schedule\\'+year+'_processed_schedule.csv')

def get_game_summary_json(game_id,year,home,away):
	api_key = "u8c9qef5z97skfay6h8ry45n"
	api_key2 = "ks8w74x4hhc6p9vhayqpdhjr"
	api_key3 = "477j4vn83zp4vryqcrt6g58e"
	res = requests.get("https://api.sportradar.us/nba-t3/games/"+game_id+"/summary.json?api_key="+api_key3)
	with io.open('.\\GameSummary\\'+year+'_'+away+'@'+home+'_'+game_id+'.json', 'w') as f:
		f.write(res.text)

# not finished till 945 game id at 2016
def read_game_summary_json_toDF(year,game_id,away,home):
	with io.open('.\\GameSummary\\'+year+'_'+away+'@'+home+'_'+game_id+'.json') as f:
		table = json.loads(f.read())
		# print table['home'].keys()
		# print '------------------------------'
		# print table.keys()
		home_player = pd.DataFrame(table['home']['players'])
		away_player = pd.DataFrame(table['away']['players'])
		home_points, away_points = table['home']['points'], table['away']['points']
		home_stat = table['home']['statistics']
		away_stat = table['away']['statistics']
		home_scoring = table['home']['scoring']
		away_scoring = table['away']['scoring']
		
		# game player stat
		stat_key = home_player['statistics'][0].keys()
		for colname in stat_key:
			home_player[colname]=home_player['statistics'].apply(lambda x: x[colname])
			away_player[colname]=away_player['statistics'].apply(lambda x: x[colname])
		home_player = home_player.drop('statistics',1)
		away_player = away_player.drop('statistics',1)

		home_player['oppo_team']=home
		away_player['oppo_team']=away

		home_player['team']=away
		away_player['team']=home

		home_player['location']='H'
		away_player['location']='A'

		home_player['points']=home_points
		home_player['oppo_points']=away_points

		away_player['points']=away_points
		away_player['oppo_points']=home_points

		home_player['date']=table['scheduled'][0:10]
		away_player['date']=table['scheduled'][0:10]


		# team stat
		team_stat = pd.DataFrame([away_stat,home_stat])
		team_stat['points'] = [away_points,home_points]
		team_stat['date'] = table['scheduled'][0:10]
		team_stat['team'] = [home,away]
		team_stat['location'] = ['A','H']
		team_stat['lead_changes'] = table['lead_changes']
		team_stat['times_tied'] = table['times_tied']

		team_stat.to_csv('.\\GameCsv\\'+game_id+'_team.csv',index =False)
		home_player.to_csv('.\\GameCsv\\'+game_id+'_H_players.csv',index =False)
		away_player.to_csv('.\\GameCsv\\'+game_id+'_A_players.csv',index =False)
#265:lead changes
#558,943: home statistics
#2016 3 games no data reason game postponed		

def save_game_summary_csv(year):
	df = pd.read_csv('.\\Schedule\\'+year+'_processed_schedule.csv')
	for i in xrange(0,len(df)):
		print i
		if i!=265 and i!=558 and i!=943 :
			read_game_summary_json_toDF(year,df.loc[i,'id'],df.loc[i,'home'],df.loc[i,'away'])
		
def get_record_by_game_id_(year):
	df = pd.read_csv('.\\Schedule\\'+year+'_processed_schedule.csv')
	id_list = list()
	for i in xrange(0,len(df)):
		id_list.append((df.loc[i,'id']+'_A_players.csv',df.loc[i,'id']+'_H_players.csv',df.loc[i,'id']+'_team.csv'))
	return id_list


if __name__ == '__main__':
	save_game_summary_csv('2016')
	# print pd.read_csv('.\\GameCsv\\'+get_record_by_game_id_('2016')[0][0]).columns
	# print pd.read_csv('.\\GameCsv\\'+get_record_by_game_id_('2016')[0][1]).columns
	# print pd.read_csv('.\\GameCsv\\'+get_record_by_game_id_('2016')[0][2]).columns
	