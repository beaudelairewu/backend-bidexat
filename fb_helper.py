from firebase_admin import credentials, firestore, storage, initialize_app
import os
import uuid
import random
import string
from ai_helper import rundetect

#################FIREBASE##############################################
# #firebase-admin firestore
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(APP_ROOT, "bidex-c1983-firebase-adminsdk.json")
cred = credentials.Certificate(cred_path)
initialize_app(cred, {'storageBucket': 'bidex-c1983.appspot.com'})
##########################################################################
bucket = storage.bucket()
db = firestore.client()



def fetchData(userID, patientID, slideID):
    # 1.1 get image_name_list from firestore
    imagesRef = db.collection(u'users').document(userID).collection(u'patients').document(patientID).collection(u'slides').document(slideID).collection(u'images')
    deleted_query = imagesRef.where(u'deleted','==',False)
    processed_query = deleted_query.where(u'processed','==',False)
    docs = processed_query.get()
    image_name_list = []
    for doc in docs:
        image_name_list.append(doc.to_dict()['name'])
    print(f'found {len(image_name_list)} images')

    # 1.2 create directory based on clusterIDs
    clusterID =  ''.join(random.choices(string.ascii_uppercase+string.ascii_lowercase + string.digits, k=12))
    direc = f'/Users/beau/dev/bidex_at/backend-bidexat/{clusterID}'
    if os.path.exists(direc):
        pass
    os.makedirs(direc)
    # 1.3 fetch actual files
    for fileName in image_name_list:
        print('start fetching')
        blob = bucket.blob(f'input/{userID}/{patientID}/{slideID}/{fileName}')
        #savePath = f"/worker/img_cache/inputfolder/{clusterIDs[i]}/{fileName}"
        localSavePath = f'/Users/beau/dev/bidex_at/backend-bidexat/{clusterID}/{fileName}'
        blob.download_to_filename(localSavePath)
        print('fetch finished')
    
    rundetect(clusterID)


def saveData(userID, patientID, slideID):



fetchData('a@gmail.com','Qd65OmKB3CVo15XEQoG2','QSqME64oh4J7JXqypZfl')