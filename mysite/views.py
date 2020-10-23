import requests
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from konlpy.tag import Kkma

# from django.shortcuts import render

kkma = Kkma()

def get_soup(url) :
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
	res = requests.get(url, headers=headers)
	res.raise_for_status()
	soup = BeautifulSoup(res.text, 'lxml')
	return soup

def get_daum_age_news(today_date) :
	url = f'https://news.daum.net/ranking/age?regDate={today_date}'

	fin_news_data = []
	
	soup = get_soup(url)
	news_group_title = soup.find('ul', attrs={'class': 'tab_nav'}).find('li', attrs={'class': 'on'}).find('a').contents[4].strip()
	news_category_list = soup.find_all('div', attrs={'class': 'item_age'})
	for news_category in news_category_list :
		in_news_list = news_category.find_all('div', attrs={'class': re.compile('^rank_')})
		for in_news in in_news_list :
			news_category_title = in_news.find('strong', attrs={'class': 'txt_news'}).get_text().strip()
			age_news_list = in_news.find('ol', attrs={'class': 'list_age'}).find_all('li')
			data_news_list = []
			for age_news in age_news_list :
				subject = age_news.find('a', attrs={'class': 'link_txt'}).get_text().strip()
				link = age_news.find('a', attrs={'class': 'link_txt'})['href']
				writer = age_news.find('span', attrs={'class': 'info_news'}).get_text().strip()
				view_cnt = 0
				data_news_list.append({
					'subject' : subject,
					'link' : link,
					'writer' : writer,
					'view_cnt' : 0
				})
			data_news_group = {
				'news_group': news_group_title,
				'news_category': news_category_title,
				'news_list': data_news_list
			}
			fin_news_data.append(data_news_group)

	return fin_news_data

def get_daum_popular_news(today_date) :
	urls = [
		f'https://news.daum.net/ranking/popular/news?regDate={today_date}',
		f'https://news.daum.net/ranking/popular/entertain?regDate={today_date}',
		f'https://news.daum.net/ranking/popular/sports?regDate={today_date}'
	]
	
	# return data
	fin_news_data = []

	for url in urls :
		soup = get_soup(url)
		# 카테고리 추출 ex) 많이 본 뉴스
		news_group_title = soup.find('div', attrs={'class':'rank_news'}).find('h4', attrs={'class': 'screen_out'}).get_text().strip()
		news_category_title = soup.find('ul', attrs={'class': 'tab_sub'}).find('li', attrs={'class': 'on'}).find('a').contents[2].strip()

		# 뉴스 추출
		data_news_list = []
		popular_news = soup.find('ul', attrs={'class':'list_news2'})
		popular_news_list = popular_news.find_all('li', limit=5)
		for popular_news in popular_news_list :
			subject = popular_news.find('a', attrs={'class': 'link_txt'}).get_text().strip()
			link = popular_news.find('a', attrs={'class': 'link_txt'})['href']
			writer = popular_news.find('span', attrs={'class': 'info_news'}).get_text().strip()
			view_cnt = ""
			data_news_list.append({
				'subject' : subject,
				'link' : link,
				'writer' : writer,
				'view_cnt' : 0
			})
		data_news_group = {
			'news_group': news_group_title,
			'news_category': news_category_title,
			'news_list': data_news_list
		}

		fin_news_data.append(data_news_group)

	return fin_news_data

result_cnt = {}
def get_keyword_list(sentence) :
	noun_list = kkma.nouns(f'{sentence}')
	for noun in noun_list :
		try : 
			result_cnt[noun] += 1
		except : 
			result_cnt[noun] = 1
	return result_cnt
	
	

def get_news_list() : 
	today_date = datetime.today().strftime('%Y%m%d')	
	daum_popular_news = get_daum_popular_news(today_date)
	daum_age_news = get_daum_age_news(today_date)

	all_news_group = {
		'daum' : [daum_popular_news, daum_age_news],
		'naver' : []
	}

	for group in daum_age_news : 
		for news in group.get('news_list') :
			get_keyword_list(news.get('subject'))
	
	df = pd.Series(result_cnt)
	df = df.sort_values(ascending=False)
	print(df)

	

	return all_news_group


# PAGE 
# def news_list(request) : 
# 	context = {
# 		'result_group_list' : get_news_list(),
# 		'today_date' : datetime.today().strftime('%Y년  %m월  %d일')
		
# 	}
	
# 	return render(request, 'mysite/news_list.html', context)


if __name__ == '__main__' : 
	# get_keyword_list('(자바설치, 환경변수 설정, 파이썬과 자바 버전 상이 등 오류가 많이 나는 편 ㅠㅠ)')
	get_news_list()
