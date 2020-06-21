# -*- coding: utf-8 -*-

from typing import Dict, List

import scrapy
from scrapy.loader.processors import MapCompose

def remove_unicode(value: str) -> str:
    return value.replace(u"\u201c", '').replace(u"\u201d", '').replace(u"\2764", '').replace(u"\ufe0f", '')

class AirbnbItem(scrapy.Item):

    # Listing Characterization
    id = scrapy.Field()
    name = scrapy.Field(input_processor = MapCompose(remove_unicode))
    city = scrapy.Field()
    city_localized = scrapy.Field()
    neighbourhood_id = scrapy.Field()
    neighbourhood = scrapy.Field()
    neighbourhood_localized = scrapy.Field()
    lat = scrapy.Field()
    lng = scrapy.Field()
    is_hotel = scrapy.Field()
    license = scrapy.Field()
    license_required = scrapy.Field()
    property_type = scrapy.Field()
    room_type = scrapy.Field()
    room_category = scrapy.Field()

    # Host Data
    host_id = scrapy.Field()
    host_name = scrapy.Field()
    is_superhost = scrapy.Field()
    response_rate = scrapy.Field()
    response_time = scrapy.Field()

    # Listing Details
    top_amenities = scrapy.Field()
    pictures_count = scrapy.Field()
    reviews_count = scrapy.Field()
    min_nights = scrapy.Field()
    max_nights = scrapy.Field()
    capacity = scrapy.Field()
    cancelation_policy = scrapy.Field()
    instant_book = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    beds = scrapy.Field()

    # Ratings
    star_rating = scrapy.Field()
    rating = scrapy.Field()
    localized_rating = scrapy.Field()

    # Individual Ratings
    accuracy_rating = scrapy.Field()
    cleanliness_rating = scrapy.Field()
    communication_rating = scrapy.Field()
    checkin_rating = scrapy.Field()
    location_rating = scrapy.Field()
    value_rating = scrapy.Field()
    guest_satisfaction_overall_rating = scrapy.Field()

    @classmethod
    def from_json(cls, json_str: Dict):
        instance = cls()
 
        listing_data: Dict = json_str.get('listing', {})
        host_data: Dict = listing_data.get('user', {})

        instance['id'] = listing_data.get('id')
        instance['city'] = listing_data.get('city')
        instance['city_localized'] = listing_data.get('localized_city')
        instance['neighbourhood'] = listing_data.get('neighborhood')
        instance['neighbourhood_localized'] = listing_data.get('localized_neighborhood')
        instance['name'] = listing_data.get('name')
        instance['property_type'] = listing_data.get('_category')
        instance['star_rating'] = listing_data.get('star_rating')
        instance['capacity'] = listing_data.get('person_capacity')
        instance['reviews_count'] = listing_data.get('reviews_count')
        instance['pictures_count'] = listing_data.get('picture_count')
        instance['top_amenities'] = listing_data.get('preview_amenities')
        instance['min_nights'] = listing_data.get('min_nights')
        instance['max_nights'] = listing_data.get('max_nights')
        instance['cancelation_policy'] = listing_data.get('cancel_policy')

        instance['bedrooms'] = listing_data.get('bedrooms', 0)
        instance['bathrooms'] = listing_data.get('bathrooms', 0)
        instance['beds'] = listing_data.get('beds', 0)

        instance['host_id'] = host_data.get('id')
        instance['host_name'] = host_data.get('first_name')
        instance['is_superhost'] = host_data.get('is_superhost')

        return instance


    def to_list(self) -> List:
        return [
            self['id'],
            self['name'],
            self['lat'],
            self['lng'],
            self['city'],
            self['neighbourhood_id'],
            self['neighbourhood'],
            self['neighbourhood_localized'],
            self['capacity'],
            self['rating'],
            self['star_rating'],
            self['localized_rating'],
            self['reviews_count'],
            self['is_hotel'],
            self['host_id'], 
            self['host_name'],
            self['is_superhost'],
            self['license'],
            self['license_required'],
            self['max_nights'],
            self['min_nights'],
            self['top_amenities'],
            self['property_type'],
            self['room_type'],
            self['room_category'],
            self['cancelation_policy'],
            self['beds'],
            self['bedrooms'],
            self['bathrooms'],
            self['response_time'],
            self['response_rate'],
            self['instant_book'],
            self['accuracy_rating'],
            self['cleanliness_rating'],
            self['communication_rating'],
            self['checkin_rating'],
            self['guest_satisfaction_overall_rating'],      
            self['location_rating'],  
            self['value_rating'],    
        ]
