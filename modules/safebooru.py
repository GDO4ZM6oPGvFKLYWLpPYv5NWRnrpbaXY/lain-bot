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
		
		randImage = random.randint(0, 99)
		
		
		print(dir(r))
		
		
		randImageDirectory = r_dict[randImage]['directory']
		randImageFile = r_dict[randImage]['image']
		randImageID = r_dict[randImage]['id']
		
		randImageURL = 'https://safebooru.org//images/'+str(randImageDirectory)+'/'+str(randImageFile)+'?'+str(randImageID) #puts together the json info to find the image 
		
		print(randImageURL)
		return(randImageURL)