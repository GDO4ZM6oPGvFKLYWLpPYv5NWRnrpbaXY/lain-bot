import requests
import os
import random

class Safebooru:
	
	def booruSearch(searchTerm):
		r = requests.get("https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags="+searchTerm)
		r_dict = r.json()
		
		# file = open('test.json', 'w')
		# for listitem in r_dict:
			# file.write(str(listitem))
			# file.write(os.linesep)
		# file.close()
		
		
		
		randImage = random.randint(0, len(r_dict)-1)
		
		
		#print(dir(r))
		
		
		randImageDirectory = r_dict[randImage]['directory']
		randImageFile = r_dict[randImage]['image']
		randImageID = r_dict[randImage]['id']
		
		randTags = r_dict[randImage]['tags']
		
		randImageTags = randTags.split(" ")
		
		randImageURL = 'https://safebooru.org//images/'+str(randImageDirectory)+'/'+str(randImageFile)+'?'+str(randImageID) #puts together the json info to find the image 
		randImagePage = 'https://safebooru.org/index.php?page=post&s=view&id='+str(randImageID)
		
		randomTagsCount = len(randImageTags)
		
		tagNumber = random.sample(range(1, randomTagsCount), 3)
		
		randTagOne = randImageTags[tagNumber[0]]
		randTagTwo = randImageTags[tagNumber[1]]
		randTagThree = randImageTags[tagNumber[2]]
		
		randTagsTogether = str(searchTerm+' | '+randTagOne+' | '+randTagTwo+' | '+randTagThree)
		
		returnList = [randImageURL, randImagePage, randTagsTogether]
		
		# print(randImageURL)
		return(returnList)