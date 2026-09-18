# PlayStation Store Utility

`playstation.py` integrates PlayStation wishlist monitoring with the PlayStation Store GraphQL API. It does not crawl rendered product pages.

## API

The utility calls:

```text
https://web.np.playstation.com/api/graphql/v1/op
```

It uses the persisted `getSearchResults` operation with these variables:

- `countryCode`: the wishlist country, upper-cased
- `languageCode`: the wishlist language, lower-cased
- `searchTerm`: the game name or search query
- `pageSize`: 10

The persisted-query hash is stored in `PlayStationUtilities.SEARCH_PERSISTED_QUERY_HASH`. The hash belongs to the current PlayStation Store frontend query. If PlayStation changes that query, search and price checks may need a new hash.

## Search Results

The API returns two relevant result types:

- `Product`: a released store product with an ID and price data.
- `Concept`: a game concept, which may not yet have a released product.

Product prices are read from `price.basePrice` and `price.discountedPrice`. The discounted value becomes `price_new`; the base value becomes `price_old`. A game is considered on sale when the new value is lower than the base value.

The utility selects an image from the result media, preferring these roles:

1. `GAMEHUB_COVER_ART`
2. `FOUR_BY_THREE_BANNER`
3. `EDITION_KEY_ART`
4. the first image returned by the API

## Unreleased Concepts

Concept IDs are numeric and are stored as the stable `game_id`. A concept without products is represented as:

- `price_new = 0.00`
- `price_old = 0.00`
- `on_sale = False`
- a `/concept/{id}` Store URL

During a price check, the utility searches the API again by the stored game name. When the concept gains a product, the first available product is used for price monitoring. The original numeric concept ID is retained, while the stored URL changes to `/product/{product_id}`. This avoids breaking the wishlist-game foreign-key relationship while allowing future checks to use the released product.

A product can also be returned directly by the API for a concept name. In that case it is treated as the concept's newly available product.

## Async Price Checks

Price checks use `aiohttp` and perform one API request per wishlist game concurrently. Results are collected with `asyncio.gather(..., return_exceptions=True)`.

A failure for one game is logged and excluded from the result, while successful games continue through price comparison and notification. This prevents one unavailable or malformed Store response from cancelling the entire wishlist check.

The synchronous `search` method uses `requests`. The scheduled price-check path uses the asynchronous API methods through the existing event-loop helper.

## Price Comparison

`ShopUtilities.compare_prices` compares the new API result with the stored wishlist value:

- a lower `price_new` is returned as a bargain and can trigger an email
- a changed price is persisted
- a changed currency or Store URL is persisted even when the numeric price is unchanged

The URL comparison is required for concept-to-product transitions where both prices can still be `0.00`.

## Operational Notes

- The Store response is country and language dependent. Keep the wishlist country and language values configured correctly.
- API failures are logged with the affected game ID and do not abort the remaining checks.
- If PlayStation changes the persisted GraphQL operation or response fields, update the operation hash and the result/price mapping in `playstation.py`.
