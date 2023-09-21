import re

WISHLIST_DICT = {
    "name": "test wishlist",
    "email": "test@example.com",
    "schedule_timestamp": "2023-09-20T16:05:10.173031",
    "country_code": "DE"
}

WISHLIST2_DICT = {
    "name": "test wishlist2",
    "email": "test2@example.com",
    "schedule_timestamp": "2023-09-20T17:05:10.173031",
    "country_code": "CH"
}


def valid_uuid(uuid):
    regex = re.compile('^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$', re.I)
    match = regex.match(uuid)
    return bool(match)

# Test the /wishlist/create/  endpoint
def test_wishlist_create(client):
    response = client.post("/wishlist/create/",json=WISHLIST_DICT)
    assert response.status_code == 200
    assert valid_uuid(response.json()["uuid"]) == True
    assert response.json()["name"] == WISHLIST_DICT["name"]
    assert response.json()["email"] == WISHLIST_DICT["email"]
    assert response.json()["schedule_timestamp"] == WISHLIST_DICT["schedule_timestamp"]
    assert response.json()["schedule_frequency"] == 1
    assert response.json()["country_code"] == WISHLIST_DICT["country_code"]

# Test the /wishlist/{uuid} endpoint
def test_wishlist_get(client):
    # Create a wishlist
    response = client.post("/wishlist/create/",json=WISHLIST_DICT)
    uuid = response.json()["uuid"]
    # Get the wishlist
    response = client.get("/wishlist/"+uuid)
    assert response.status_code == 200
    assert response.json()["uuid"] == uuid
    assert response.json()["name"] == WISHLIST_DICT["name"]
    assert response.json()["email"] == WISHLIST_DICT["email"]
    assert response.json()["schedule_timestamp"] == WISHLIST_DICT["schedule_timestamp"]
    assert response.json()["schedule_frequency"] == 1
    assert response.json()["country_code"] == WISHLIST_DICT["country_code"]
    # Get a non-existing wishlist
    response = client.get("/wishlist/not-existing-uuid")
    assert response.status_code == 404

# Test the /wishlist/all endpoint
def test_wishlist_all(client):
    # Create two wishlists
    response = client.post("/wishlist/create/",json=WISHLIST_DICT)
    response = client.post("/wishlist/create/",json=WISHLIST2_DICT)

    # Get all wishlists
    response = client.get("/wishlist/all")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == WISHLIST_DICT["name"]
    assert response.json()[0]["email"] == WISHLIST_DICT["email"]
    assert response.json()[0]["schedule_timestamp"] == WISHLIST_DICT["schedule_timestamp"]
    assert response.json()[0]["schedule_frequency"] == 1
    assert response.json()[0]["country_code"] == WISHLIST_DICT["country_code"]
    assert response.json()[1]["name"] == WISHLIST2_DICT["name"]
    assert response.json()[1]["email"] == WISHLIST2_DICT["email"]
    assert response.json()[1]["schedule_timestamp"] == WISHLIST2_DICT["schedule_timestamp"]
    assert response.json()[1]["schedule_frequency"] == 1
    assert response.json()[1]["country_code"] == "CH"

# Test the /wishlist/update/ endpoint
def test_wishlist_update(client):
    # Create a wishlist
    response = client.post("/wishlist/create/",json=WISHLIST_DICT)
    uuid = response.json()["uuid"]
    # Update the wishlist
    response = client.put("/wishlist/update/"+uuid,json=WISHLIST2_DICT)
    assert response.status_code == 200
    assert response.json()["details"] == "wishlist successfully updated"
    # Ensure that the wishlist is updated
    updated_wishlist = client.get("/wishlist/"+uuid)
    assert updated_wishlist.json()["uuid"] == uuid
    assert updated_wishlist.json()["name"] == WISHLIST2_DICT["name"]
    assert updated_wishlist.json()["email"] == WISHLIST2_DICT["email"]
    assert updated_wishlist.json()["schedule_timestamp"] == WISHLIST2_DICT["schedule_timestamp"]
    assert updated_wishlist.json()["schedule_frequency"] == 1
    assert updated_wishlist.json()["country_code"] == "CH"
    # Update a non-existing wishlist
    response = client.put("/wishlist/update/not-existing-uuid",json=WISHLIST2_DICT)
    assert response.status_code == 404

# Test the /wishlist/delete/ endpoint
def test_wishlist_delete(client):
    # Create a wishlist
    response = client.post("/wishlist/create/",json=WISHLIST_DICT)
    uuid = response.json()["uuid"]
    # Delete the wishlist
    response = client.delete("/wishlist/delete/"+uuid)
    assert response.status_code == 200
    assert response.json()["details"] == "wishlist successfully deleted"
    # Ensure that the wishlist is deleted
    response = client.get("/wishlist/all")
    assert len(response.json()) == 0
    response = client.delete("/wishlist/delete/not-existing-uuid")
    assert response.status_code == 404