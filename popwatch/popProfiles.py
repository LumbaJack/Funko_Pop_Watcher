# Class to Create/Store Profiles for Each Store.
import json
import portalocker

from popwatch import config


class Profile(object):

    def __init__(self, city, ccNumber, f_name, l_name, zipCode, phone, ad_one, ad_two, ccSecurityCode, email, ccOwner, expDate):
        self.city = city
        self.ccNumber = ccNumber
        self.f_name = f_name
        self.l_name = l_name
        self.zipCode = zipCode
        self.phone = phone
        self.ad_one = ad_one
        self.ad_two = ad_two
        self.ccSecurityCode = ccSecurityCode
        self.email = email
        self.ccOwner = ccOwner
        self.expDate = expDate
