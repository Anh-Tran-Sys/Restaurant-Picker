from functions import choose_restaurant, format_restaurant, yelp_scrape
import pandas as pd


def test_choose_restaurant():
    df = yelp_scrape('95111', 'chicken')
    list_restaurant = df.index.tolist()
    msg = 'random'
    assert (str(choose_restaurant(
        msg, df).index[0]) in list_restaurant)
    msg = 'some unknown criteria'
    assert (str(choose_restaurant(
        msg, df).index[0]) in list_restaurant)

    msg = 'rating'
    max_rating = str(df['Rating'].max()).replace('\n', '')
    assert (str(choose_restaurant(msg, df)['Rating'][0])
            == max_rating)

    msg = 'closest'
    min_distance = str(df['Distance'].min()).replace('\n', '')
    assert (str(choose_restaurant(msg, df)
                ['Distance'][0]) == min_distance)


def test_format_restaurant():
    cols = ['Name', 'Rating', 'Price',
            'Review Count', 'Address', 'Distance', 'Phone', 'Link']
    listings = []
    review_count = '100'
    phone = '4040400404'
    link = 'http/'
    name = 'Foodworx'
    price = '$'
    distance = '5'
    rating = '0.5'
    address = 'middle of nowhere'
    listings.append([name, rating, price, review_count,
                     address, distance, phone, link])
    restaurant = pd.DataFrame.from_records(listings, index='Name',
                                           columns=cols)
    expected = ('Great! The restaurant you want is', name,
                '. On a scale of $ to $$$$, its price is',
                price, '. The location is', address,
                ', which is', distance, 'miles away from your location.',
                name, 'has a rating of ', rating, '.')
    assert(format_restaurant(restaurant) == expected)
    print('test complete')
