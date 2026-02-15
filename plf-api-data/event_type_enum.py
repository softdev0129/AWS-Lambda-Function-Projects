from enum import Enum


class EventType(Enum):
    DATA_DOWNLOAD = "/data/download"
    GET_INTERNATIONAL_CATEGORIES = "/data/getinternationalcategories"
    GET_INTERNATION_EMAIL = "/data/get_internation_email"
    GET_INTERNATION_NUMBER = "/data/get_internation_number"
    GET_LOCALE_EMAIL = "/data/get_locale_email"
    GET_LOCALE_NUMBER = "/data/get_locale_number"
    GET_SERVICED_LINKS = "/data/get_serviced_links"
    GET_MORE_CATEGORIES = "/data/getmorecategories"
    GET_LOCAL_CATEGORIES = "/data/getlocalcategories"
    SEARCH_CATEGORIES = "/data/search"
    GET_HTML = "/data/gethtml"
    FETCH_LOGS = "/data/logs"
    GET_COMPANIES = "/data/getCompanies"
    GET_CONTACT_INFO = "/data/getContactInfo"
    SEARCH_DIRECTORY = "/data/searchDirectory"
    @classmethod
    def from_path(cls, path):
        print(f'Path - {path}')
        if not path and path is not '':
            return None
        path = path.lower()  # Convert the path to lowercase for case-insensitive matching
        for event_type in cls:
            if event_type.value.lower() == path:
                print(f'EventType Matched - {event_type.name}')
                return event_type.name
        return None
