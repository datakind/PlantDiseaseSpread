# coding:utf-8
import pandas as pd, requests, sys
from os.path import join
import time

url_template = "https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom_level}&size=400x400&maptype=satellite&key={api_key}"
    
def crea_url(data):
    return url_template.format(**data)
     
def save_image(base_dir,data):
    url = crea_url(data)
    image = session.get(url)
    filename = '%s-%s.png' % (data["id"],data["zoom_level"])
    f=open(join(base_dir,filename),'wb')
    f.write(image.content)
    f.close()
         
session = requests.Session()

#Note: Fill in your Google Maps Static api_key here to get this script to work
api_key = "FILL IN YOUR API KEY"
data = pd.read_csv(sys.argv[1],low_memory=False)
base_dir = "images"
for index, row in data.iterrows():
    data = {"id": row["Location.ID"],"lat": row["Latitude"], "lon": row["Longitude"],"api_key": api_key}
    for zoom_level in [18]:
        data["zoom_level"] = zoom_level 
        save_image(base_dir,data)
        print "Saved image for location id: %d" % row["Location.ID"]
    time.sleep(0.1)
