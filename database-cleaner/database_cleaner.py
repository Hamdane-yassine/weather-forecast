from datetime import datetime, timedelta
from database import Database

# Connect to the database
database = Database()

# Get the current time - 1h (The data is stored in UTC)
current_time = datetime.now() - timedelta(hours=1)

# Calculate the timestamp threshold (10 minutes ago)
threshold = current_time - timedelta(minutes=10)

print("Looking for documents older than: " + str(threshold), flush=True)

# Get the documents older than the threshold
documents = database.find({"timestamp": {"$lt": threshold}})

for document in documents:
    print("Deleting document: " + str(document['_id']), flush=True)
    database.delete({"_id": document['_id']})

print("Job finished", flush=True)