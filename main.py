# [START app]
import logging
import requests

# [START imports]
from flask import Flask, request
from flask import jsonify
from google.cloud import spanner
import os
# [END imports]

# [START create_app]
app = Flask(__name__)
# [END create_app]

# [START create_spanner]
spanner_client = spanner.Client()
user_microservices = os.getenv("USER_MICROSERVICES")
instance_id = os.getenv("SPANNER_INSTANCE")
database_id = os.getenv("SPANNER_DATABASE")
# [END create_spanner]

def is_admin(token):
    response = requests.get(user_microservices +"/isAdmin", params={'token': token})
    if response.status_code == 200:
        return response.json().get('is_admin', False)
    else:
        print(f"Failed to check admin status. Status code: {response.status_code}")
        return False


# [END app]