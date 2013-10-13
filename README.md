election-voters-scraper
=======================

The scrapes the election centers from the election commission website of Nepal http://election.gov.np. The election centers are listed in the districts folder, segregated by districts. The centers, vdcs are in Devanagari (Nepali Unicode) as per the site content. The district is mentioned in both English and Nepali. The codes for districts, vdcs, wards and centers are as per the election.gov.np and the same codes are used to scrape the voters list from the site.

The voters lists are not scraped yet as it need to make almost 36000 hits in the server. Be careful if you are planning to do that. That part of the code still needs to be worked on and tested. 

Look into your district election centers file, and find the codes for district, vdc, ward and center. The following code should bring the list of the people registered under that center. It also creates cache once it reads it from the website. 

voters = Voters(68, 3037, 1, 7764)
print voters.cache.filepath
if not voters.cache.isPresent():
	voters.makeHttpRequest()
	voters.prepare()
for voter in voters.voters_list:
	print voter['election_id'], voter['name'], voter['gender'], voter['father_name'], voter['mother_name']

run.py doesn't do anything now. It has code to scrape the centers and create csv from the cache files and you have to update the code to execute the functinos. 
