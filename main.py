# [START app]
import logging
import requests
import random
import string

# [START imports]
from flask import Flask, request
from flask import jsonify
from flask import make_response
from google.cloud import spanner
from google.cloud import storage
import os
from functools import wraps
# [END imports]

# [START create_app]
app = Flask(__name__)
# [END create_app]

# [START create_spanner]
spanner_client = spanner.Client()
storage_client = storage.Client()
user_microservices = os.getenv("USER_MICROSERVICES")
instance_id = os.getenv("SPANNER_INSTANCE")
database_id = os.getenv("SPANNER_DATABASE")
bucket_image = os.getenv("BUCKET_IMAGE")
# [END create_spanner]
def is_admin(token):
    response = requests.get(user_microservices +"/isAdmin", params={'token': token})
    if response.status_code == 200:
        print(response.json())
        return response.json().get('is_admin', False)
    else:
        print(f"Failed to check admin status. Status code: {response.status_code}")
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_token = request.args.get('token')
        if not user_token:
            return make_response(jsonify({"error": "Token is missing"}), 400)
        
        if not is_admin(user_token):
            return make_response(jsonify({"error": "Forbidden: User is not an admin"}), 403)

        return f(*args, **kwargs)
    return decorated_function


def get_next_id(table):
    sql = "SELECT next_value FROM sequences WHERE name=@tableName;"
    database = spanner_client.instance(instance_id).database(database_id)
    with database.snapshot() as snapshot:
        params = {"tableName": table}
        param_types = {"tableName": spanner.param_types.STRING}
        cursor = snapshot.execute_sql(sql, params=params, param_types=param_types)
    response = list(cursor)
    if response:
        return response[0][0]
    else:
        raise ValueError(f"No next_value found for table: {table}")


def incr_next_id(table):
    database = spanner_client.instance(instance_id).database(database_id)

    def update_next_id(transaction):
        row = transaction.execute_sql(
            "SELECT next_value FROM sequences WHERE name = @tableName",
            params={"tableName": table},
            param_types={"tableName": spanner.param_types.STRING}
        ).one_or_none()

        if row is None:
            raise ValueError(f"No sequence found for table: {table}")

        next_val = int(row[0])

        transaction.update(
            "sequences",
            columns=["name", "next_value"],
            values=[[table, int(next_val+1)]]
        )
        return next_val
    next_val = database.run_in_transaction(update_next_id)
    return next_val


@app.route("/add_image", methods=['POST'])
@admin_required
def add_image():
    if 'image' not in request.files:
        return {"error": "No image provided"}, 400

    image = request.files['image']
    filename = ""
    # Make sure the image is not empty
    if image.filename == '':
        letters = string.ascii_letters
        filename = ''.join(random.choice(letters) for i in range(24))
    else:
        filename = image.filename
    
    try:
        bucket = storage_client.bucket(bucket_image)
        blob = bucket.blob(image.filename)
        blob.upload_from_string(
            image.read(),
            content_type=image.content_type
        )

        return {"name": image.filename}
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/insert_wine", methods=['POST'])
@admin_required
def insert_wine():
    wine_data = request.get_json()
    if wine_data is None:
        return make_response(jsonify({"error": "Bad request: JSON data is missing or improperly formatted"}), 400)

    database = spanner_client.instance(instance_id).database(database_id)
    id = {}
    with database.batch() as batch:
        for field in wine_data["new_field"]:
            if field == "cepage":
                for cep in wine_data["new_field"]["cepage"]:
                    next_id = get_next_id(field)
                    batch.insert(
                        table=field,
                        columns=("id", "cepage"),
                        values=[(next_id, str(cep))],
                    )
                    incr_next_id(field)
                    continue
                continue

            next_id = get_next_id(field)
            if field != "cuve":
                batch.insert(
                    table=field,
                    columns=("id", field),
                    values=[(next_id, wine_data["new_field"][field])],
                )
                if field != "cepage":
                    id["id_" + field] = next_id
                incr_next_id(field)
            else:
                batch.insert(
                    field,
                    columns=["id", "id_prod", "cuve"],
                    values=[(next_id, id["id_productor"], wine_data["new_field"][field])],
                )
                id["id_" + field] = next_id
                incr_next_id(field)

        for field in wine_data["data"]:
            if field == "percent":
                id[field] = float(wine_data["data"][field]) 
            if field != "cepage":
                id[field] = wine_data["data"][field]
        id["id"] = get_next_id("wine")
        batch.insert("wine", columns=id.keys(), values=[tuple(id.values())])
        incr_next_id("wine")

        for cep in wine_data["cepage"]:
            if isinstance(cep, str):
                batch.insert(
                    "cepage",
                    columns=["id", "cepage"],
                    values=[(get_next_id("cepage"), cep)],
                )
                batch.insert(
                    "cepage_join",
                    columns=["id", "id_wine", "id_cepage"],
                    values=[(get_next_id("cepage_join"), int(id["id"]), get_next_id("cepage") )],
                )
                incr_next_id("cepage")
                incr_next_id("cepage_join")
                continue                
    return jsonify({"success": "Wine successfully inserted", "data": id})


# [END app]

