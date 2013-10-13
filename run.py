# coding=utf-8
from ElectionCenters import *

"""
Scrapes all the districts/vdcs/wards/centers
It maintains all the cache and doesn't scrape the pages that have already been pulled
"""
def scrapeCenters():
	districtsCollection = DistrictsCollection()
	for district_id in districtsCollection.districts:
		districtObj = District(district_id, districtsCollection.districts[district_id])
		if not districtObj.cache.isPresent():
			print "Scraping district: ", districtsCollection.districts[district_id]
			districtObj.makeHttpRequest()
			districtObj.prepare()
		print "Reading district: ", districtsCollection.districts[district_id]
		for vdc_id in districtObj.vdcs:
			vdcObj = Vdc(district_id, vdc_id, districtObj.vdcs[vdc_id])
			if not vdcObj.cache.isPresent():
				print "Scraping vdc ", districtObj.vdcs[vdc_id], " of ", districtsCollection.districts[district_id]
				vdcObj.makeHttpRequest()
				vdcObj.prepare()
			for ward_id in vdcObj.wards:
				wardObj = Ward(district_id, vdc_id, ward_id, vdcObj.wards[ward_id])
				if not wardObj.cache.isPresent():
					print "Scraping ward ", vdcObj.wards[ward_id], " of ", districtObj.vdcs[vdc_id],", ", districtsCollection.districts[district_id]
					wardObj.makeHttpRequest()
					wardObj.prepare()

"""
prepares CSV file for the given district
"""
def prepareDistrictWiseCSV(filepath, district_id, district_nep_name, district_eng_name):
	ofile  = open(filepath, "wb")
	writer = unicodecsv.writer(ofile, encoding='utf-8')
	writer.writerow(["District Code", "DistrictEng", "DistrictNep", "VDC/Municipality Code", "VDC/Municipality", "Ward No", "Center Code", "Center"])
	district = District(district_id, district_nep_name)
	for vdc_id in district.vdcs:
		vdc = Vdc(district_id, vdc_id, district.vdcs[vdc_id])
		for ward_id in vdc.wards:
			ward = Ward(district_id, vdc_id, ward_id, vdc.wards[ward_id])
			centersCollection = ward.centers
			for center_id in ward.centers:
				row = [district_id, district_eng_name, district_nep_name, \
					vdc_id, district.vdcs[vdc_id], \
					vdc.wards[ward_id], \
					center_id, ward.centers[center_id]];
				writer.writerow(row)
	ofile.close()

"""
Calls prepareDistrictWiseCSV() to prepare csv for all the districts
alldistricts.csv
"""
def prepareAllDistrictsCSV():
	ifile  = open(os.path.join("districts", "alldistricts.csv"), "rb")
	reader = unicodecsv.reader(ifile, encoding='utf-8')
	for row in reader:
		filepath = os.path.join("districts", row[2]+".csv")
		print "Printing csv for ", row[1], row[2], " at ", filepath
		prepareDistrictWiseCSV(filepath, row[0], row[1], row[2])
	ifile.close()

# voters = Voters(68, 3037, 1, 7764)
# print voters.cache.filepath
# if not voters.cache.isPresent():
# 	voters.makeHttpRequest()
# 	voters.prepare()
# for voter in voters.voters_list:
# 	print voter['election_id'], voter['name'], voter['gender'], voter['father_name'], voter['mother_name']

