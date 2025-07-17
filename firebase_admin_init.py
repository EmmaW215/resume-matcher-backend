import firebase_admin
from firebase_admin import credentials, firestore

# 用你刚下载的 JSON 文件路径替换下面的路径
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()