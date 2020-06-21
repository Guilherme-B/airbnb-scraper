# Python imports
import json
from json.decoder import JSONDecoder
from typing import Dict, List, Union

# The upper module isn't being recognized by sys, force it
import sys
import pathlib

print(pathlib.Path(__file__).parents[2].absolute())
sys.path.insert(0, (str(pathlib.Path(__file__).parents[2].absolute())))

# Scrapy imports
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from airbnb_scraper.items import AirbnbItem

class AirBnbSpider(scrapy.Spider):
    
    name = 'airbnb'
    allowed_domains = ['www.airbnb.pt']

    __website: str = 'https://www.airbnb.pt'
    __api_endpoint: str = '/api/v2/explore_tabs'
    __api_endpoint_rooms: str = '/api/v2/pdp_listing_details'

    __items_per_section: int = 18
    __section_offset: int = 5
    __headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}

    __currency = "EUR"

    def __init__(self, cities, *args, **kwargs): #config: Dict[str, Dict[str, str]] = None, *args, **kwargs):

        super(AirBnbSpider, self).__init__(*args, **kwargs)

        if cities is None:
            raise ValueError(__name__,'::init() missing cities.')

        self.__cities = cities.split(',')

    def start_requests(self):

        for city in self.__cities:
            print(__name__, '::start_requests() for city: ', city)    

            yield scrapy.Request(
                url = self._generate_url(city, section_offset = self.__section_offset, items_offset=self.__items_per_section),
                callback = self.parse,
                headers = self.__headers,
                meta = {
                    'city': city,
                },
                dont_filter = False,
            )
            

    def _generate_url(self, city_name: str, section_offset: int, items_offset: int) -> Union[str, None]:

        if city_name is None:
            print(__name__,'::generate_url() invalid inputs.')
            return None

        params: str = "?_format=for_explore_search_web" \
                    "&_intents=p1&allow_override%5B%5D=&auto_ib=false" \
                    "&client_session_id=621cf853-d03e-4108-b717-c14962b6ab8b" \
                    "&currency={currency}" \
                    "&experiences_per_grid=20" \
                    "&fetch_filters=true" \
                    "&guidebooks_per_grid=20" \
                    "&has_zero_guest_treatment=true" \
                    "&is_guided_search=true" \
                    "&is_new_cards_experiment=true" \
                    "&is_standard_search=true" \
                    "&items_per_grid=18" \
                    "&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&locale=en" \
                    "&luxury_pre_launch=false&metadata_only=false" \
                    "&query={city}&query_understanding_enabled=true" \
                    "&refinement_paths%5B%5D=%2Fhomes" \
                    "&s_tag=QLb9RB7g" \
                    "&search_type=FILTER_CHANGE" \
                    "&selected_tab_id=home_tab" \
                    "&show_groupings=true" \
                    "&supports_for_you_v3=true&timezone_offset=-240" \
                    "&version=1.5.6" \
                    "&items_offset={items_offset}" \
                    "&section_offset={section_offset}".format(
            currency = self.__currency,
            city = city_name,
            section_offset = section_offset,
            items_offset = items_offset,
        )
        
        url: str = (self.__website +
                    self.__api_endpoint + 
                    params)

        return url

    def __generate_listing_url(self, listing_id: int) -> str:
        
        params: str = self.__api_endpoint_rooms + "/{room_id}?currency={currency}" \
                "&adults=1" \
                "&key=d306zoyjsyarp7ifhu67rjxn52tv0t20" \
                "&_format=for_rooms_show".format(
                    room_id = listing_id,
                    currency = self.__currency,
        )

        url: str = (self.__website + params)

        return url

    def _parse_detail(self, response: scrapy.http.TextResponse): 
        entity: AirbnbItem = response.meta.get('listing')

        if entity is None:
            print(__name__, '::_parse_detail() could not retrieve entity')
            yield None
        
        place_json: Dict = json.loads(response.body.decode("utf-8"))
        listing_json: Dict = place_json.get('pdp_listing_detail', {})
        host_json: Dict = listing_json.get('primary_host', {})

        if not listing_json is None:
            entity['name'] = listing_json.get('name')
            entity['lat'] = listing_json.get('lat')
            entity['lng'] = listing_json.get('lng')
            entity['city'] = listing_json.get('localized_city')
            entity['neighbourhood_id'] = listing_json.get('neighborhood_id')
            entity['is_hotel'] = listing_json.get('is_hotel')
            entity['capacity'] = listing_json.get('person_capacity')
            entity['rating'] = listing_json.get('star_rating')
            entity['localized_rating'] = listing_json.get('reviews_module').get('localized_overall_rating')

            if entity['localized_rating'] is not None:
                entity['localized_rating'] =  entity['localized_rating'].replace(',', '.')

            entity['license'] = listing_json.get('license')
            entity['license_required'] = listing_json.get('requires_license')
            entity['property_type'] = listing_json.get('room_and_property_type')
            entity['room_category'] = listing_json.get('room_type_category')

            entity['host_id'] = host_json.get('id')
            entity['host_name'] = host_json.get('host_name')
            entity['is_superhost'] = host_json.get('is_superhost')
            entity['response_rate'] = host_json.get('response_rate_without_na')
            entity['response_time'] = host_json.get('response_time_without_na')

            logging_data = listing_json.get('p3_event_data_logging')
            entity['instant_book'] = logging_data.get('instant_book_possible', False)
            entity['room_type'] = logging_data.get('room_type')

            entity['accuracy_rating'] = logging_data.get('accuracy_rating')
            entity['cleanliness_rating'] = logging_data.get('cleanliness_rating')
            entity['communication_rating'] = logging_data.get('communication_rating')
            entity['checkin_rating'] = logging_data.get('checkin_rating')
            entity['guest_satisfaction_overall_rating'] = logging_data.get('guest_satisfaction_overall')
            entity['location_rating'] = logging_data.get('location_rating')
            entity['value_rating'] = logging_data.get('value_rating')

            yield entity

        yield None

    def parse(self, response: scrapy.http.TextResponse):
        city: str = response.meta['city']
        data_json: Dict = json.loads(response.body.decode("utf-8"))

        try:
            listings = data_json.get('explore_tabs')[0].get('sections')[0].get('listings')
        except:
            listings = None

        if listings is None:
            try:
                listings = data_json.get('explore_tabs')[0].get('sections')[1].get('listings')
            except IndexError:
                try:
                    listings = data_json.get('explore_tabs')[0].get('sections')[2].get('listings')
                except IndexError:
                    #raise CloseSpider("No available listings for the specified parameters.")
                    yield None
            
        if listings is not None:
            for listing in listings:
                entity = AirbnbItem.from_json(listing)

                if entity:
                    yield scrapy.Request(
                        url = self.__generate_listing_url(entity['id']),
                        callback = self._parse_detail,
                        dont_filter = False,
                        headers = 
                        {
                            'user-agent': self.__headers.get('user-agent'),
                            'origin': self.__website,
                        },
                        meta = {
                            'listing': entity
                        }
                    )

            pagination_metadata: Dict = data_json['explore_tabs'][0]['pagination_metadata']
            next_page: bool = bool(pagination_metadata.get('has_next_page', False))
            items_offset: int = pagination_metadata.get('items_offset', 16)
            section_offset: int = pagination_metadata.get('section_offset', 0)

            if next_page:
                yield scrapy.Request(
                    url = self._generate_url(city_name = city, items_offset = items_offset, section_offset = section_offset),
                    meta = {
                        'city': city,
                    },
                    headers = self.__headers,
                    dont_filter = False
                )

