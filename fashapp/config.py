class BaseConfig(object):
    ADMIN_EMAIL='quest@email.com'

class LiveConfig(BaseConfig):
    SITE_ADDRESS='https://sites.com'

class TesConfig(BaseConfig):
    SITE_ADDRESS='https://questsite.com'