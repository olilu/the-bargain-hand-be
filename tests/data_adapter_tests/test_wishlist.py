from sqlalchemy.orm import Session
from datetime import datetime

from pydantic_models.wishlist import WishlistCreate
from data_adapter.wishlist import create_new_wishlist, list_wishlists

# Write a test for the list_wishlists function
def test_list_wishlists(db_session:Session):
    test_time = datetime.now().time()
    wishlist = WishlistCreate(
        name="test wishlist",
        email="test@test.com",
        schedule_timestamp=test_time,
        country_code="CH",
    )
    wishlist = create_new_wishlist(wishlist,db_session)
    wishlist.name = "test wishlist 2"
    wishlist.email = "test2@test.com"
    wishlist = create_new_wishlist(wishlist,db_session)
    # Call the list_wishlists function
    wishlists = list_wishlists(db_session)
    # Check that the wishlist is in the list
    assert wishlist in wishlists
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

        
