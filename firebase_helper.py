from firebase_admin import credentials, firestore, storage, initialize_app
import os
import numpy as np

#################FIREBASE##############################################
# #firebase-admin firestore
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(APP_ROOT, "bidex-c1983-firebase-adminsdk.json")
cred = credentials.Certificate(cred_path)
initialize_app(cred, {'storageBucket': 'bidex-c1983.appspot.com'})
##########################################################################
bucket = storage.bucket()
db = firestore.client()



def fetchData(userID, patientID, slideID, clusterIDs):
    #get image_name_list from firestore
    imagesRef = db.collection(u'users').document(userID).collection(u'patients').document(patientID).collection(u'slides').document(slideID).collection(u'images')
    deleted_query = imagesRef.where(u'deleted','==',False)
    processed_query = deleted_query.where(u'processed','==',False)
    docs = processed_query.get()
    image_name_list = []
    for doc in docs:
        image_name_list.append(doc.to_dict()['name'])
    print(f'found {len(image_name_list)} images')

    #divide in to multiple clusters (faster detection time)
    clusterSize = len(clusterIDs)
    splits = np.array_split(image_name_list, clusterSize)
    divided_image_name_list = [list(array) for array in splits]

    #create directory based on clusterIDs
    for dir in clusterIDs:
        if os.path.exists(f'/Users/beau/dev/bidex_at/backend-bidexat/{dir}'):
            continue
        os.makedirs(dir)

    #get image files from storage bucket
    for i, file_list in enumerate(divided_image_name_list):
        print(len(file_list))
        for fileName in file_list:
            blob = bucket.blob(f'input/{userID}/{patientID}/{slideID}/{fileName}')
            print(f'/input/{userID}/{patientID}/{slideID}/{fileName}')
            #savePath = f"/worker/img_cache/inputfolder/{clusterIDs[i]}/{fileName}"
            localSavePath = f'/Users/beau/dev/bidex_at/backend-bidexat/{clusterIDs[i]}/{fileName}'
            print(f'/Users/beau/dev/bidex_at/backend-bidexat/{clusterIDs[i]}/{fileName}')
            blob.download_to_filename(localSavePath) 
    
    
    


fetchData('a@gmail.com','Qd65OmKB3CVo15XEQoG2','QSqME64oh4J7JXqypZfl', ['asdfosiejf','asdfielson'])