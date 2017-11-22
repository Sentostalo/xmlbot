from bs4 import BeautifulSoup
import remy
import aiohttp
import asyncio
import _pickle as pickle
import re
import datetime


def get_content(soup, tag, classname):
	return str(soup.find(tag, class_=classname).get_text()).strip()

async def get_html(client,url):
	async with client.get(url) as resp:
		assert resp.status == 200
		html = await resp.text()
	return html

def get_messages(html):  # get all the messages from a given forum page
	soup = BeautifulSoup(html, 'lxml')
	content = soup.find_all('div', {'class': 'row'})
	[s.extract() for s in soup('script')]
	page_data = {}
	for c in content:
		c = str(c)
		c = BeautifulSoup(c, 'lxml')
		try:
			post_data = {}
			post_id = c.find('td', class_='table-cadre-cellule-numero position-relative').get_text().split()  # get the post id
			post_data['name'] = get_content(c, 'span', 'element-bouton-profil')  # find the profile of the person who posted
			unix_timestamp = get_content(c, 'div', 'cadre-auteur-message-date')  # find the unix timestamp of the post
			post_data['timestamp'] = unix_timestamp
			post_data['date'] = datetime.datetime.utcfromtimestamp(int(unix_timestamp) / 1000.0)  # convert the timestamp to time
			post_data['text'] = get_content(c, 'div', 'cadre-message-contenu')  # find the date of the post
			page_data[post_id[0]] = post_data
		except AttributeError:  # when the row has no post-like content
			pass
	return page_data


def get_last_posts(html):
	soup = BeautifulSoup(html, 'lxml')
	content = soup.find_all('div', {'class': 'row'})
	[s.extract() for s in soup('script')]
	for c in content:
		topic_name = (c.find('td', 'table-cadre-cellule-principale').get_text())
		if 'official rotation' in topic_name.lower():
			count = (c.find_all('a', href=True))
			latest_post = ('https://atelier801.com/{}'.format(count[1]['href']))
			topic_category = (''.join(re.findall(' P.*? ', topic_name)).strip())
			last_posts[topic_category] = latest_post
	return last_posts


def get_mapcrew(html):  # get all the mapcrew names
	mapcrew = ['Barrydarsow', 'Mapcrewone', 'Mapcrewtwo', 'Mapcrew', 'Mapzilla']
	mapcrew_list = BeautifulSoup(html, 'lxml')
	mapcrew_list = mapcrew_list.find_all('td', class_='table-cadre-cellule-principale contenant-nom-utilisateur')
	for mapcrew_info in mapcrew_list:
		parsed_info = BeautifulSoup(''.join(str(mapcrew_info.contents)), 'lxml')
		name = (parsed_info.find('span'))
		mapcrew.append(str(name.contents[2]).strip())
	return mapcrew


def reviews_from(messages):
	reviews = []
	with open('mapcrew.txt', 'rb') as file:
		mapcrew_list = (pickle.load(file))
	for post_id, content in messages.items():
		if content['name'] in mapcrew_list:
			if 'left as is' in content['text'].lower():
				reviews.append('Post {} | {} [{}] {}\n'.format(post_id, content['date'], content['name'], content['text']))
	return reviews


async def get_reviews_via_redir(client):  # get the latest reviews from barrydarsow.com
	reviews = {}
	mapcategories = ['3', '4', '5', '6', '7', '8', '9', '10', '11', '17', '18', '19', '24']
	for category in mapcategories:
		link = 'http://www.barrydarsow.com/php/lastreviewlink.php?P={}'.format(category)
		async with client.get(link) as resp:
			assert resp.status == 200
			reviews['P{}'.format(category)] = str(resp.history[-1].url)
	return reviews
