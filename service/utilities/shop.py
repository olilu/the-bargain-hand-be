class ShopUtilities:
    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        self.wishlist_uuid = wishlist_uuid
        self.country_code = country_code
        self.language_code = language_code
        self.country_language_code = f"{country_code.lower()}_{language_code.lower()}"
        