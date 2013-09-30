import requests
import os
from bs4 import BeautifulSoup
import json

CACHE_DIR = 'cache'

def getCacheFilePath(type, id):
	return os.path.join(CACHE_DIR, '{}_{}.txt'.format(type, id))

def saveCache(text, type, id):
	myFile = open(getCacheFilePath(type, id), 'w')
	myFile.write(text)
	myFile.close()

def readCache(type, id):
	return open(getCacheFilePath(type, id), 'r').read()

def isCachePresent(type, id):
	if os.path.isfile(getCacheFilePath(type, id)):
		return True
	return False

def cleanStr(str):
	return str.strip().replace('\\\"',"").strip()

def getDistricts(data):
	districts = {}
	soup = BeautifulSoup(data);
	for option in soup.find_all('option'):
		if option.get('value'):
			districts[option.get('value')] = option.text
	return districts

def getDistrictHtml(district_id):
	if(isCachePresent('district', district_id)):
		return readCache('district', district_id)
	else:
		url = "http://202.166.205.141/bbvrs/index_process.php"
		payload = {'district':district_id, 'list_type':'vdc'}
		r = requests.post(url, data=payload)
		saveCache(r.text, 'district', district_id)
		return r.text

def getVDCs(html):
	vdcs = {}
	data = json.loads(html)
	soup = BeautifulSoup(data['result']);
	for option in soup.find_all('option'):
		if cleanStr(option.get('value')):
			vdcs[cleanStr(option.get('value'))] = option.text
	return vdcs

def getVDCHtml(vdc_id):
	if(isCachePresent('vdc', vdc_id)):
		return readCache('vdc', vdc_id)
	else:
		url = "http://202.166.205.141/bbvrs/index_process.php"
		payload = {'vdc':vdc_id, 'list_type':'ward'}
		r = requests.post(url, data=payload)
		saveCache(r.text, 'vdc', vdc_id)
		return r.text

def getWards(html):
	wards = {}
	data = json.loads(html)
	soup = BeautifulSoup(data['result']);
	for option in soup.find_all('option'):
		if cleanStr(option.get('value')):
			wards[cleanStr(option.get('value'))] = option.text
	return wards

def getWardHtml(vdc_id, ward_id):
	if(isCachePresent('vdc_{}_ward'.format(vdc_id), ward_id)):
		return readCache('vdc_{}_ward'.format(vdc_id), ward_id)
	else:
		url = "http://202.166.205.141/bbvrs/index_process.php"
		payload = {'vdc':vdc_id, 'ward':ward_id, 'list_type':'reg_centre'}
		r = requests.post(url, data=payload)
		saveCache(r.text, 'vdc_{}_ward'.format(vdc_id), ward_id)
		return r.text

def getElectionCenter(html):
	centers = {}
	data = json.loads(html)
	soup = BeautifulSoup(data['result']);
	for option in soup.find_all('option'):
		if cleanStr(option.get('value')):
			centers[cleanStr(option.get('value'))] = option.text
	return centers

def getVotersHtml(district_id, vdc_id, ward_id, center_id):
	if(isCachePresent('voters_{}_{}_{}_list'.format(district_id, vdc_id, ward_id), center_id)):
		return readCache('voters_{}_{}_{}_list'.format(district_id, vdc_id, ward_id), center_id)
	else:
		url = "http://202.166.205.141/bbvrs/view_ward.php"
		payload = {'district': district_id, 'vdc_mun':vdc_id, 'ward':ward_id, 'hidVdcType':'vdc'}
		r = requests.post(url, data=payload)
		saveCache(r.text, 'voters_list', center_id)
		return r.text

# def getVoters(html):	
# 	soup = BeautifulSoup(html);
# 	s = soup.find('div', class_= 'div_bbvrs_data')
# 	voters = []
# 	for tr in s.find_all('tr'):
# 		count = 0
# 		voter = {}
# 		for td in tr.find_all('td'):
# 			voter[count] = td.text
# 			count += 1
# 		if voter.get(1):
# 			voters.append({'election_id': voter.get(1), 
# 						'name':voter.get(2),
# 						'gender': voter.get(3),
# 						'father_name': voter.get(4),
# 						'mother_name': voter.get(5),
# 						'center': voter.get(6)
# 						})
# 	print voters
	


# text = getVotersHtml(30, 1085, 1, 7764)
# getVoters(text)

districts = getDistricts(open('districts.html','r'))
count = 0
for district_id in districts:
	if district_id:
		print "Reading district html ", district_id, districts[district_id]
		vdc_html = getDistrictHtml(district_id)
		vdcs = getVDCs(vdc_html)
		print "Total VDCs: ", len(vdcs)
		for vdc_id in vdcs:
			print "Reading VDC html " , vdc_id, vdcs[vdc_id]
			ward_html = getVDCHtml(vdc_id)
			wards = getWards(ward_html)
			print "Total Wards: ", len(wards)
			for ward_id in wards:
				print "Reading Ward html " , ward_id
				center_html = getWardHtml(vdc_id, ward_id)
				centers = getElectionCenter(center_html)
				print "Total Centers: ", len(centers)

