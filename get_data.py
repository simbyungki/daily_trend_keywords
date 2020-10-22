import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

def get_soup(url) :
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
	res = requests.get(url, headers=headers)
	res.raise_for_status()
	soup = BeautifulSoup(res.text, 'lxml')
	return soup

all_news_group = {}

def get_news_list() : 
	today_date = datetime.today().strftime('%Y%m%d')
	naver_news_url = f'https://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&date={today_date}'
	soup = get_soup(naver_news_url)
	popular_news_group = soup.find_all('div', attrs={'class':'ranking_section'})

	all_news_group = {
		'naver' : [],
		'daum' : []
	}
	data_news_list = []

	for idx, popular_news in enumerate(popular_news_group) :
		group_title = popular_news.find('h4', attrs={'class':re.compile('^tit')}).get_text().strip()
		group_news_list = popular_news.find('ol').find_all('li')
		
		# print('ㅡ'* 100)
		# print(group_title)
		
		for group_news in group_news_list :
			if group_news.find('dl') :
				group_news_subject = group_news.find('dt').find('a')['title'].strip()
				group_news_url = 'https://news.naver.com/' + group_news.find('dt').find('a')['href']
				if len(group_news.find('dt').find_all('span')) :
					group_news_writer = group_news.find('dt').find_all('span')[0].get_text().strip()
				else :
					group_news_writer = group_news.find('dd').find_all('span')[1].get_text().strip()
				group_news_view_cnt = group_news.find('i', attrs={'class': 'count_view'}).get_text().strip()
				
				data_news_list.append({
					'subject' : group_news_subject,
					'link' : group_news_url,
					'writer' : group_news_writer,
					'view_cnt' : group_news_view_cnt
				})

			# 포토뉴스는 일단 제외
			else :
				# group_news_subject = group_news.find('p').find('a').get_text().strip()
				pass

		
		all_news_group['naver'].append({
			'news_type' : '많이 본 뉴스',
			'news_group' : group_title,
			'news_list' : data_news_list
		})
		
		# data용 뉴스 묶음 초기화
		data_news_list = []	

		
	

	# 출력
	for all_news in all_news_group.get('naver') :
		print('ㅡ'* 100)
		print()
		print(f'[[[{all_news.get("news_type")}]]]')
		print(all_news.get('news_group'))
		for news in all_news.get('news_list') :
			print(news.get('subject'))
			print(f'{news.get("writer")} | {news.get("view_cnt")}')
		print()
		print('ㅡ'* 100)


if __name__ == '__main__' : 
	get_news_list()