from firebase_admin import credentials, firestore, storage, initialize_app
import os
import shutil
import random
import string
from ai_helper import rundetect

#################FIREBASE##############################################
# #firebase-admin firestore
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(APP_ROOT, "bidex-atl-firebase-adminsdk-s9roj-43b9086b07.json")
cred = credentials.Certificate(cred_path)
initialize_app(cred, {'storageBucket': 'bidex-atl.appspot.com'})
##########################################################################
bucket = storage.bucket()
db = firestore.client()

inputFolder = '/worker/img_cache/inputfolder/'
outputFolder = '/worker/img_cache/outputfolder/'

# inputFolder = '/Users/beau/dev/bidex_at/backend-bidexat/img_cache/inputfolder'
# outputFolder = '/Users/beau/dev/bidex_at/backend-bidexat/img_cache/outputfolder'

def fullcycle(userID, patientID, slideID, image_name_list, detectUnprocessed=False):
    # if detectUnprocessed:
    #     imagesRef = db.collection(u'users').document(userID).collection(u'patients').document(patientID).collection(u'slides').document(slideID).collection(u'images')
    #     deleted_query = imagesRef.where(u'deleted','==',False)
    #     processed_query = deleted_query.where(u'processed','==',False)
    #     docs = processed_query.get()
    #     image_name_list = []
    #     for doc in docs:
    #         image_name_list.append(doc.to_dict()['name'])
    #     print(f'found {len(image_name_list)} images')

    # 1.2 create directory based on clusterIDs
    clusterID =  ''.join(random.choices(string.ascii_uppercase+string.ascii_lowercase + string.digits, k=12))
    inputFolderID = os.path.join(inputFolder,clusterID)
    outputFolderID = os.path.join(outputFolder, clusterID)
    if (os.path.exists(inputFolderID) and os.path.exists(outputFolderID)):
        shutil.rmtree(inputFolderID)
        shutil.rmtree(outputFolderID)
        os.makedirs(inputFolderID)
        os.makedirs(outputFolderID)
    else:
        os.makedirs(inputFolderID)
        os.makedirs(outputFolderID)

    # 1.3 fetch actual files
    print('start fetching')
    # try:
    for fileName in image_name_list:
        blob = bucket.blob(f'input/{userID}/{patientID}/{slideID}/{fileName}')
        blob.download_to_filename(os.path.join(inputFolderID,fileName))
    # except:
    #     print(f'error downloading: {fileName}')
    print('fetch finished')
    
    #2.1 run ai on image data
    results = rundetect(clusterID)
    
    #3.1 save detected images
    print('start saving')
    # try:
    for fileName in image_name_list:
        blob = bucket.blob(f"output/{userID}/{patientID}/{slideID}/{fileName}")
        blob.upload_from_filename(os.path.join(outputFolderID, fileName))
        blob.make_public()
    # except:
    #     print(f'error uploading: {fileName}')
    print('save finished')
    
    #3.2 save detected images' data
    # try:
    for key in results:
        print(key)
        print(results[key])
        imagesRef = db.collection(u'users').document(userID).collection(u'patients').document(patientID).collection(u'slides').document(slideID).collection(u'images').document(key)
        imagesRef.update({
            u'computed': True,
            u'ovCount': results[key]
        })
    # except:
        # print(f'error saving info: {key}')

    # for fileName in image_name_list:
    #     imagesRef = db.collection(u'users').document(userID).collection(u'patients').document(patientID).collection(u'slides').document(slideID).collection(u'images').document(fileName)
    #     imagesRef.update({
    #         u'computed': True,
    #         u'ovCount': results['']
    #     })

    #3.3 delete used folders
    shutil.rmtree(inputFolderID)
    shutil.rmtree(outputFolderID)
    print('congrats fullcycle successful!')


# fullcycle('beam@gmail.com', 'cLfxSmlA5UTPwzHiQau3', 'JvuXwEtkvKH8qjk0EBNZ',["0VZMOOZ5P7E2.jpg", "12I2610UX3T2.jpg"])