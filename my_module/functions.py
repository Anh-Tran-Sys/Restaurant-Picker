import string
import random
import requests as request
import numpy as np
import pandas as pd

PROMPT_ADDRESS = 'Enter your address'
PROMPT_FOOD = 'Now what would you like to eat?'
PROMPT_ATTRIBUTES = [('Okay, that\'s a start, is there any other criteria '
                      'you\'re looking for?'),
                     ('Great, is there anything else you are looking for in '
                      'this place?'),
                     'Alright, is there any other conditions you like?',
                     ('Awesome, now is there anything else you want to '
                      'include with this search?')]
PROMPT_INCORRECT = ('Strange, there\'s no locations that fits '
                    'your criteria, we\'ll try this again')
PROMPT_PICK = ('Now would you like for me to pick a random restaurant in the '
               'top 10, or would u prefer the highest '
               'rating or closest distance')
PROMPT_WRONG = 'Sorry, I don\'t understand that'

NO_ANSWER = ['none', 'nah', 'na' 'thats all', 'nothing', 'else',
             'nope', 'no', 'thats all', 'done', 'finish',
             'finished', ' its okay']
YES_ANSWER = ['yeah', 'yes', 'yup', 'yep', 'y', 'yuh', 'ye', 'yeet', 'yee']
CLOSEST_ANSWER = ['closest', 'close', 'distance', 'distant', 'closer']
RATING_ANSWER = ['highest', 'rating', 'rate', 'ratings', 'high', 'best']
RANDOM_ANSWER = ['random', 'randoms']
RANDOM_RESPONSE = ('I didnt understand what you said so I will choose one '
                   'of the top 10 restaurants for you')
DIFFERENT_RESPONSE = 'Would you like me to suggest a different restaurant?'


def string_concatenator(string1, string2, separator):
    """
    Description: concats two strings separated by a separator
    Params:
            string1 - string being concat to
            string2 - string concatting to string1
            seperator - char/string separating string1 and string2
    Return: concatted string1 and string 2 separated by separator
    """
    if(string1 == None):
        string1 = ''
    if (string2 == None):
        string2 = ''
    if (separator == None):
        separator = ''
    return(string1 + separator + string2)


def list_to_string(input_list, separator):
    """
    Description: converts list into string separated by separator
    Params:
            input_list -  list being converted
            separator - char/string separating each element in new string
    Return: returns the string that is converted from list
    """
    output = ''
    for element in input_list:
        if element == separator:
            continue
        output = string_concatenator(output, element, separator)
    return output


def prepare_text(input_string):
    """
    Description: formats string by splitting the words and lowercasing them
    Params: input_string - string being converted
    Return: the formatted string
    """
    temp_string = remove_punctuation(input_string.lower())
    output = temp_string.split()
    return output


def remove_punctuation(input_string):
    """
    Description: removes punctuation from a string
    Params: input_string - the string where the punctuations are being removed
    Return: the string without any punctuations
    """
    out_string = ''
    for character in input_string:
        if (character not in string.punctuation):
            out_string = out_string + character
    return out_string


def is_in_list(list_one, list_two):
    """Check if any element of list_one is in list_two."""
    if(type(list_one) == str):
        if(list_one in list_two):
            return True
        return False

    for element in list_one:
        if element in list_two:
            return True
    return False


def random_selector(input_list):
    """picks random element from input_list"""
    output = random.choice(input_list)
    return output


def have_a_chat():
    """Main function to run our chatbot."""
    # Initialization
    address = ''
    food_choice = ''
    chat = True
    df = pd.DataFrame()
    out_msg = PROMPT_ADDRESS
    key_word = ''
    proceed = False
    choice = False
    restaurant = None

    # prints introduction
    print('This program is designed to choose a restaurant for you!')
    print('First let\'s get your information')

    # Asks user to enter key word
    print(PROMPT_ADDRESS)

    # Loop while user keeps chatting
    while chat:
        # Get a message from the user
        msg = input('INPUT :\t')

        # Prepare the input message
        msg = prepare_text(msg)

        # initialize values using inputs
        # based on what was asked of the user

        # get address
        if(PROMPT_ADDRESS in out_msg):
            address = list_to_string(msg, ' ')
        # get food
        elif(PROMPT_FOOD in out_msg):
            food_choice = list_to_string(msg, ' ')
        # user done entering options
        elif(is_in_list(PROMPT_ATTRIBUTES, out_msg)):
            if(is_in_list(msg, NO_ANSWER)):
                proceed = True
            else:
                key_word = key_word + ',' + list_to_string(msg, ' ')
        # get restaurant
        elif(out_msg == PROMPT_PICK and df is not None):
            restaurant = choose_restaurant(msg, df)
        elif(out_msg == DIFFERENT_RESPONSE and is_in_list(msg, YES_ANSWER)):
            restaurant = choose_restaurant('random', df)
        elif(out_msg == DIFFERENT_RESPONSE and is_in_list(msg, NO_ANSWER)):
            out_msg = ('Great, feel free to boot me up again if'
                       ' you want me to make another search!')
            chat = False

        # Check for an end msg
        if ('quit' in msg):
            out_msg = 'Bye!'
            chat = False
        # If user wants to quit we should quit
        if (chat == True):
            # reset output for this run
            out_msg = None

        # Logic to decide what the output should be
        if not out_msg:
            # if user havent entered an address
            if(address == ''):
                out_msg = PROMPT_ADDRESS
            # if user havent entered any food choices
            elif(food_choice == ''):
                out_msg = PROMPT_FOOD
            # if we picked a restaurant already, we print
            elif(restaurant is not None):
                print(*format_restaurant(restaurant))
                restaurant = None
                out_msg = DIFFERENT_RESPONSE
            # if user already has all info entered, we scrape
            elif(proceed == True):
                key_word = food_choice + ',' + key_word
                df = yelp_scrape(address, key_word)
                out_msg = PROMPT_PICK
                proceed = False
                choice = True
            # if there was no result, we restart
            elif(df is None and address != ''
                 and food_choice != '' and key_word != ''):
                address = ''
                food_choice = ''
                key_word = ''
                proceed = False
                choice = False
                out_msg = PROMPT_INCORRECT + '\n' + PROMPT_ADDRESS
            # if user already read 1 restaurant, ask if user wants another 1
            elif(choice == True):
                out_msg = DIFFERENT_RESPONSE
            # print message for options
            else:
                out_msg = (random_selector(PROMPT_ATTRIBUTES))

        # If no message was printed then we print it's wrong
        if(out_msg is None):
            out_msg == PROMPT_WRONG
        #
        print('OUTPUT:', out_msg)


def choose_restaurant(msg, df):
    """
    Description: function that chooses a restaurant given a condition
                and a dataframe
    Params: 
        msg - input of user deciding method to choose restaurant from list
        df - dataframe containing the top 10 restaurants that was searched
    Return:
        single row dataframe containing the restaurant we want
    """
    # chooses the closest distance
    output = None
    if (is_in_list(msg, CLOSEST_ANSWER)):
        output = df.head(1)
    # chooses the highest rating
    elif(is_in_list(msg, RATING_ANSWER)):
        output = df.sort_values('Rating', ascending=False).head(1)
    # chooses a random one
    else:
        output = df.sample(n=1)

    return(output)


def format_restaurant(restaurant):
    """
    Description: formats dataframe of restaurant into a readable output
    Params:
        restaurant- dataframe of restaurant being printed
    Return:
        string containing a readable format of the restaurant and its info
    """
    return ('Great! The restaurant you want is', str(restaurant.index[0]),
            '. On a scale of $ to $$$$, its price is',
            str(restaurant['Price'][0]),
            '. The location is', str(restaurant['Address'][0]),
            ', which is', str(restaurant['Distance'][0])[:3],
            'miles away from your location.',
            str(restaurant.index[0]), 'has a rating of ',
            str(restaurant['Rating'][0]), '.')


def yelp_scrape(address, key_word, radius=5):
    """ 
    inspired by https://www.youtube.com/watch?v=vgHwPPRM5JE&t=1551s
    Description: scrape data from yelp
    Params: 
        address - the address of the user
        key_word - the key words we're using to search through yelp
        radius - the max distance from address
    Return: dataframe containing all restaurants that meets criteria,
            else None if address is invalid.
    """
    # Initialization
    listings = []
    cols = ['Name', 'Rating', 'Price',
            'Review Count', 'Address', 'Distance', 'Phone', 'Link']
    url = 'https://api.yelp.com/v3/businesses/search'
    key = ('XvhhL00Pccl4m7drH-63PzxPTmkyj2z_B5mOXLGq1uWVAqaFOHArTeSCUdPUktwkd'
           'xSf9eTnvzA_bgIGqoZRClzCSQ1nakw_Fs_sJ2gLOyvBqFyrTLYYVh8im1fTXnYx')
    headers = {
        'Authorization':    'Bearer %s' % key
    }
    preference = {'location': address,
                  'limit': '10',
                  'radius': int(int(radius) / 0.00062137),
                  'term': key_word
                  }
    response = request.get(url, headers=headers, params=preference)
    data = response.json()
    df = None
    # checks if address is valid
    try:
        data['error']
        return df
    except:
        # iterates through all restaurant and turns into dataframe
        for business in data['businesses']:
            name = business['name']
            rating = business['rating']
            try:
                price = business['price']
            except:
                price = 'not known'
            review_count = business['review_count']
            distance = business['distance'] * 0.00062137
            link = business['url']
            phone = business['phone']
            address = business['location']['display_address'][0]
            listings.append([name, rating, price, review_count,
                             address, distance, phone, link])
            df = pd.DataFrame.from_records(listings, index='Name',
                                           columns=cols)
            df = df.sort_values('Distance')
        return df
