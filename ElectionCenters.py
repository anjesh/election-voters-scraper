# coding=utf-8
import requests
import os
from bs4 import BeautifulSoup
import json
from time import sleep
import unicodecsv

CACHE_DIR = 'cache'
VOTERS_CACHE_DIR = 'voterscache'

class CacheHandler:
	def __init__(self, cache_dir, type, id):
		self.id = id
		self.type = type
		self.filepath = os.path.join(cache_dir, '{}_{}.txt'.format(self.type, self.id))	

	def getFilePath(sef):
		self.filepath = os.path.join(cache_dir, '{}_{}.txt'.format(self.type, self.id))

	def isPresent(self):
		if os.path.isfile(self.filepath):
			return True
		return False

	def read(self):
		if self.isPresent():
			return open(self.filepath, 'r').read()
		return False

	def save(self, text):
		myFile = open(self.filepath, 'w')
		myFile.write(text.encode('UTF-8'))
		myFile.close()

class DistrictsCollection:
	def __init__(self):
		self.districts = {}
		self.districts_html = open('districts.html','r')
		self.scrape()

	def scrape(self):
		soup = BeautifulSoup(self.districts_html);
		for option in soup.find_all('option'):
			if option.get('value'):
				self.districts[option.get('value')] = option.text

class HttpRequester:
	def __init__(self, url, payload):
		self.url = url
		self.payload = payload

	def request(self):
		r = requests.post(self.url, data=self.payload)
		return r.text

def cleanStr(str):
	return str.strip().replace('\\\"',"").strip()

class District:
	def __init__(self, district_id, district_nep_name):
		self.district_id = district_id
		self.district_nep_name = district_nep_name
		self.cache = CacheHandler(CACHE_DIR, 'district', district_id)
		self.vdcs = {}
		self.prepare()

	def prepare(self):
		if self.cache.isPresent():
			self.district_html = self.cache.read()
			self.scrape()

	def scrape(self):
		vdcs = {}
		data = json.loads(self.district_html)
		soup = BeautifulSoup(data['result']);
		for option in soup.find_all('option'):
			if cleanStr(option.get('value')):
				self.vdcs[cleanStr(option.get('value'))] = option.text

	def makeHttpRequest(self):
		url = "http://202.166.205.141/bbvrs/index_process.php"
		payload = {'district': self.district_id, 'list_type':'vdc'}
		requester = HttpRequester(url, payload)
		self.district_html = requester.request()
		if self.district_html:
			self.cache.save(self.district_html)

class Vdc:
	def __init__(self, district_id, vdc_id, vdc_nep_name):
		self.vdc_id = vdc_id
		self.district_id = district_id
		self.cache = CacheHandler(CACHE_DIR, 'vdc', vdc_id)
		self.wards = {}
		self.prepare()

	def prepare(self):
		if self.cache.isPresent():
			self.vdc_html = self.cache.read()
			self.scrape()

	def scrape(self):
		vdcs = {}
		data = json.loads(self.vdc_html)
		soup = BeautifulSoup(data['result']);
		for option in soup.find_all('option'):
			if cleanStr(option.get('value')):
				self.wards[cleanStr(option.get('value'))] = option.text

	def makeHttpRequest(self):
		url = "http://202.166.205.141/bbvrs/index_process.php"
		payload = {'vdc': self.vdc_id, 'list_type':'ward'}
		requester = HttpRequester(url, payload)
		self.vdc_html = requester.request()
		if self.vdc_html:
			self.cache.save(self.vdc_html)

class Ward:
	def __init__(self, district_id, vdc_id, ward_id, ward_number):
		self.ward_id = ward_id
		self.vdc_id = vdc_id
		self.district_id = district_id
		self.cache = CacheHandler(CACHE_DIR, 'vdc_{}_ward'.format(vdc_id), ward_id)
		self.centers = {}
		self.prepare()

	def prepare(self):
		if self.cache.isPresent():
			self.ward_html = self.cache.read()
			self.scrape()

	def scrape(self):
		vdcs = {}
		data = json.loads(self.ward_html)
		soup = BeautifulSoup(data['result']);
		for option in soup.find_all('option'):
			if cleanStr(option.get('value')):
				self.centers[cleanStr(option.get('value'))] = option.text

	def makeHttpRequest(self):
		url = "http://202.166.205.141/bbvrs/index_process.php"
		payload = {'vdc': self.vdc_id, 'ward': self.ward_id, 'list_type':'reg_centre'}
		requester = HttpRequester(url, payload)
		self.ward_html = requester.request()
		if self.ward_html:
			self.cache.save(self.ward_html)

"""
TODO: Needs to be properly tested for municipality and vdc
"""
class Voters:
	def __init__(self, district_id, vdc_id, ward_id, center_id):
		self.center_id = center_id
		self.ward_id = ward_id
		self.vdc_id = vdc_id
		self.district_id = district_id
		self.cache = CacheHandler(VOTERS_CACHE_DIR, 'voters_{}_{}_{}'.format(district_id, vdc_id, ward_id), center_id)
		self.voters_list = []
		self.prepare()

	def prepare(self):
		if self.cache.isPresent():
			self.voters_html = self.cache.read()
			self.scrape()

	def scrape(self):	
		soup = BeautifulSoup(self.voters_html);
		s = soup.find('div', class_= 'div_bbvrs_data')
		for tr in s.find_all('tr'):
			count = 0
			voter = {}
			for td in tr.find_all('td'):
				voter[count] = td.text
				count += 1
			if voter.get(1):
				self.voters_list.append({'election_id': voter.get(1), 
							'name':voter.get(2),
							'gender': voter.get(3),
							'father_name': voter.get(4),
							'mother_name': voter.get(5),
							'center': voter.get(6)
							})

	def makeHttpRequest(self):
		url = "http://202.166.205.141/bbvrs/view_ward.php"
		wardObj = Ward(self.district_id, self.vdc_id, self.ward_id, "")
		vdcType = 'vdc'
		# if given ward has more than 1 centers, then we have to select centers in the election website, meaning it can be considered as municipality in that case
		if len(wardObj.centers) > 1:
			vdcType = 'mun'
		payload = {'district': self.district_id, 'vdc_mun':self.vdc_id, 'ward':self.ward_id, 'reg_centre':self.center_id, 'hidVdcType': vdcType}
		requester = HttpRequester(url, payload)
		self.voters_html = requester.request()
		if self.voters_html:
			self.cache.save(self.voters_html)

