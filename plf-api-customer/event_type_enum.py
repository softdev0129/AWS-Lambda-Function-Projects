from enum import Enum


class EventType(Enum):
    REGISTER = "/customer/auth/register"
    LOGIN = "/customer/auth/login"
    SOCIAL_LOGIN = "/customer/auth/socialLogin"
    RESET_PASSWORD = "/customer/auth/resetPassword"
    GET_USER_PROFILE = "/customer/auth/getUserProfile"
    GET_USER_PROVIDER = "/customer/auth/getProvider"
    UPDATE_PASSWORD = "/customer/user/updatePassword"
    GET_BILLING_HISTORY = "/customer/billing/getBillingHistory"
    BUY_SUBSCRIPTION = "/customer/billing/buySubscription"
    CANCEL_SUBSCRIPTION = "/customer/billing/cancelSubscription"
    GET_ALL_SUBSCRIPTIONS = "/customer/billing/getAllSubscriptions"
    CREATE_PRODUCTS_AND_PRICES = "/customer/billing/createProductsAndPrices"
    RENEW_SUBSCRIPTION = "/customer/billing/renewSubscription"
    UPDATE_SUBSCRIPTION = "/customer/billing/updateSubscription"
    CHECK_ALL_BILLING = "/customer/billing/checkallbilling"
    CHECK_USER_BILLING = "/customer/billing/checkuserbilling"
    PROCESS_PAYPAL_SUBSCRIPTION = "/customer/billing/processPaypalSubscription"
    DOC = "/customer/doc"
    OPENAPI = "/customer/openapi"
    UPDATE_NAME = "/customer/user/updateName"
    GET_LOCALE = "/customer/locale"
    CONTACT_US = "/contactus"

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
