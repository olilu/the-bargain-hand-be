from sqlalchemy.orm import Session
from datetime import datetime

from pydantic_models.wishlist import WishlistCreate
from data_adapter.wishlist import create_new_wishlist, list_wishlists, delete_wishlist, get_wishlist, update_wishlist

# Test the create_new_wishlist function and the list_wishlists function
def test_list_wishlists(db_session:Session):
    test_time = datetime.now()
    test_results = []
    # Create a wishlist
    wishlist = WishlistCreate(
        name="test wishlist",
        email="test@test.com",
        schedule_timestamp=test_time,
        country_code="CH",
    )
    result = create_new_wishlist(wishlist,db_session)
    test_results.append(result)
    # Create a second wishlist
    wishlist.name = "test wishlist 2"
    wishlist.email = "test2@test.com"
    result = create_new_wishlist(wishlist,db_session)
    test_results.append(result)
    # Call the list_wishlists function
    wishlists = list_wishlists(db_session)
    # Check that the list has length 2
    assert len(wishlists) == 2
    # Check that the wishlist has the correct name
    assert wishlists[0].name == "test wishlist"
    assert wishlists[1].name == "test wishlist 2"
    # Check that the wishlist has the correct email
    assert wishlists[0].email == "test@test.com"
    assert wishlists[1].email == "test2@test.com"
    # Check that the wishlist has the correct country_code
    assert wishlists[0].country_code == "CH"
    assert wishlists[1].country_code == "CH"
    # Check that the wishlist has the correct schedule_frequency
    assert wishlists[0].schedule_frequency == 1
    assert wishlists[1].schedule_frequency == 1
    # Check that the wishlist has the correct schedule_timestamp
    assert wishlists[0].schedule_timestamp == test_time
    assert wishlists[1].schedule_timestamp == test_time
    # Check that each wishlist has a uuid
    assert wishlists[0].uuid is not None
    assert wishlists[1].uuid is not None

# Test the delete_wishlist function
def test_delete_wishlist(db_session:Session):
    test_time = datetime.now()
    # Create a wishlist
    wishlist = WishlistCreate(
        name="test wishlist",
        email="test@test.com",
        schedule_timestamp=test_time,
        country_code="CH"
    )
    result = create_new_wishlist(wishlist,db_session)
    # ensure that the wishlist is created
    search_result = get_wishlist(result.uuid,db_session)
    assert search_result.name == "test wishlist"
    # Call the delete_wishlist function
    result = delete_wishlist(result.uuid,db_session)
    # Check that the wishliste is deleted
    search_result = get_wishlist(result.uuid,db_session)
    assert search_result is None
    
# Test the update_wishlist function
def test_update_wishlist(db_session:Session):
    test_time = datetime.now()
    # Create a wishlist
    wishlist = WishlistCreate(
        name="test wishlist",
        email="test@test.com",
        schedule_timestamp=test_time,
        country_code="CH"
    )

    result = create_new_wishlist(wishlist,db_session)
    print(result.uuid)
    # ensure that the wishlist is created
    search_result = get_wishlist(result.uuid,db_session)
    assert search_result.name == "test wishlist"
    assert search_result.country_code == "CH"
    # Update the wishlist
    wishlist.name = "test wishlist 2"
    wishlist.country_code = "US"
    update_result = update_wishlist(result.uuid,wishlist,db_session)
    # Check that the wishlist is updated
    search_result = get_wishlist(result.uuid,db_session)
    assert update_result == True
    assert search_result.name == "test wishlist 2"
    assert search_result.country_code == "US"

