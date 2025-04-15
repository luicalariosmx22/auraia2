import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the service account key file
cred = credentials.Certificate("serviceAccountKey.json")

# Initialize the Firebase app
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()

# Add data to Firestore
doc_ref = db.collection("test_collection").document("test_document")
doc_ref.set({"message": "hello"})

print("Data added to Firestore successfully!")