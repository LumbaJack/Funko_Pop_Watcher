import re
import time
import json
import hashlib
import logging
import requests
import portalocker
import platform
import os
import subprocess

from popwatch import config
from popwatch import popProfiles
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from operator import itemgetter

# Get Profile From Json Config
def profileInit():
    with portalocker.Lock(config.USER_INFO, "r", timeout=10) as data_file:
        userProfileVars = json.load(data_file)
        city = userProfileVars.get('city')
        ccNumber = userProfileVars.get('ccNumber')
        f_name = userProfileVars.get('f_name')
        l_name = userProfileVars.get('l_name')
        zipCode = userProfileVars.get('zipCode')
        mm = userProfileVars.get('mm')
        yy = userProfileVars.get('yy')
        phone = userProfileVars.get('phone')
        ad_one = userProfileVars.get('ad_one')
        ad_two = userProfileVars.get('ad_two')
        ccSecurityCode = userProfileVars.get('ccSecurityCode')
        email = userProfileVars.get('email')
        ccOwner = f_name + " " + l_name
        expDate = mm + '/' + yy

    return popProfiles.Profile(city, ccNumber, f_name, l_name, zipCode, phone, ad_one, ad_two, ccSecurityCode, email, ccOwner, expDate)

# Instantiating Pop Profile
profile = profileInit()

_LOG = logging.getLogger(__name__)

HTML_OBJ = {
    "hottopic": "presale-pdp",
    "boxlunch": "presale-pdp",
    "walmart": "spin-button-children",
    "barnesandnoble": "btn-addtocart",
    "gamestop": "addOnSalesModalEligible",
    "blizzard": "product-addtocart-button",
    "geminicollectibles": "add-to-cart",
    "hbo": "AddToCart-product-template",
    "target": "h-text-orangeDark"}

def get_distro():
    # Checking Distrobution before passing in connection string
    distroName = platform.system()
    return distroName

class storeStock(object):

    def __init__(self, UPDATER):
        self.TIMEOUT = {}
        self.UPDATER = UPDATER
        self.THREAD_ALIVE = False
        self.driver = self.init_driver()

    def ht_bl_checkout_process(self, site):
        # Checkout Button then as unregistrated user
        checkoutBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="checkout-form"]/fieldset/div/button')))
        checkoutBtn.click()
        # Start as an Unregistered User
        checkoutBtnAsGuest = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="primary"]/div[2]/div[1]/form/fieldset/div/button/span')))
        checkoutBtnAsGuest.click()
        # Fill Out Form for Guest Checkout
        # USER FORM AUTOMATION #
        email_form = self.driver.find_element_by_id("dwfrm_singleshipping_email_emailAddress")
        email_form.send_keys(profile.email)
        first_name_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_firstName")
        first_name_form.send_keys(profile.f_name)
        last_name_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_lastName")
        last_name_form.send_keys(profile.l_name)
        country_selection =  WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress_addressFields_country"]/option[2]')))
        country_selection.click()
        zip_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_postal")
        zip_form.send_keys(profile.zipCode)
        ad_one_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_address1")
        ad_one_form.send_keys(profile.ad_one)
        ad_two_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_address2")
        ad_two_form.send_keys(profile.ad_two)
        city_form = self.driver.find_element_by_id("dwfrm_singleshipping_shippingAddress_addressFields_city")
        city_form.send_keys(profile.city)
        state_selection =  WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress_addressFields_states_state"]/option[5]')))
        state_selection.click()
        phone_form = self.driver.find_element_by_id("formatted-phone")
        phone_form.send_keys(profile.phone)
        # Continue to Billing Button
        continueBillingBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_singleshipping_shippingAddress"]/div[2]/fieldset/div/button')))
        continueBillingBtn.click()
        # Enter Credit Card Information
        # Credit Card Owner
        creditCardOwner = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_owner")
        creditCardOwner.send_keys(profile.ccOwner)
        # Credit Card Number
        creditCardNum = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_number")
        creditCardNum.send_keys(profile.ccNumber)
        # Credit Card Expiration Date
        creditCardExp = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_userexp")
        creditCardExp.send_keys(profile.expDate)
        # Credit Card Security Code
        creditCardCCV = self.driver.find_element_by_id("dwfrm_billing_paymentMethods_creditCard_cvn")
        creditCardCCV.send_keys(profile.ccSecurityCode)
        # Billing Review Button
        reviewBillingBtn = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dwfrm_billing"]/div[3]/button')))
        reviewBillingBtn.click()
        # Place Order Button
        if os.environ['POPENV'] == "dev":
            self.UPDATER.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID,
                                          text="Funko Bot in Test Mode. Checkout Not Proceeding")
        elif os.environ['POPENV'] == "stg":
            self.UPDATER.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID,
                                          text="Running Checkout Process Without Headless")
            placeOrderBtn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="summarySubmit"]')))
            placeOrderBtn.click()
        elif os.environ['POPENV'] == "prd":
            placeOrderBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="summarySubmit"]')))
            placeOrderBtn.click()

    def hbo_checkout_process(self):
        # # Check if Pop Overlay Exists
        # # popup = self.driver.find_elements_by_xpath(
                #     '//*[@id="privy-inner-container"]/div[1]/div/div/div[3]/div[5]/button')

        # # Logic to Close Pop when it does exist
        # for popupCloseBtn in popup:
        #     popInnerText = popupCloseBtn.get_attribute('innerText')
        #     if popInnerText:
        #         print('Pop Found Initiating Closer of Pop Up')
        #         # Pop Up Found and Needs to be Dismissed
        #         popup.click()
        #     else:
        #         self.driver.refresh()
        # Find quantity element by name
        quantity = self.driver.find_element_by_name("quantity")
        # Reset Default Quantity Value
        self.driver.execute_script("arguments[0].value = ''", quantity)
        # Input to form number of items wanted
        quantity.send_keys("2")
        # Using Javascript to Add Item to Cart
        self.driver.execute_script("document.getElementById('AddToCart-product-template').click()")
        # Checkout Button
        hboCheckoutBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="MiniCart"]/a[1]')))
        hboCheckoutBtn.click()
        #  Enter Coupon Code
        # couponCode = self.driver.find_element_by_id("checkout_reduction_code")
        # couponCode.send_keys("WELCOME15")
        # Start Entering User Information
        hboEmailForm = self.driver.find_element_by_id("checkout_email")
        hboEmailForm.send_keys(profile.email)
        hboFName = self.driver.find_element_by_id("checkout_shipping_address_first_name")
        hboFName.send_keys(profile.f_name)
        hboLName = self.driver.find_element_by_id("checkout_shipping_address_last_name")
        hboLName.send_keys(profile.l_name)
        hboADOne = self.driver.find_element_by_id("checkout_shipping_address_address1")
        hboADOne.send_keys(profile.ad_one)
        hboADTwo = self.driver.find_element_by_id("checkout_shipping_address_address2")
        hboADTwo.send_keys(profile.ad_two)
        hboCity = self.driver.find_element_by_id("checkout_shipping_address_city")
        hboCity.send_keys(profile.city)
        hboCountrySelection = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="checkout_shipping_address_country"]/option[1]')))
        hboCountrySelection.click()
        hboStateSelection = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="checkout_shipping_address_province"]/option[5]')))
        hboStateSelection.click()
        hboZipCode = self.driver.find_element_by_id("checkout_shipping_address_zip")
        hboZipCode.send_keys(profile.zipCode)
        hboPhone = self.driver.find_element_by_id("checkout_shipping_address_phone")
        hboPhone.send_keys(profile.phone)
        # Go to Shipping Method Page
        hboShippingMethodBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/div/form/div[2]/button')))
        hboShippingMethodBtn.click()
        # Go to Payment Method Page
        hboPaymentMethodBtn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/div/form/div[2]/button')))
        hboPaymentMethodBtn.click()
        # Credit Card Information Form Fill Out
        # Credit Card Number
        hbocreditCardNumIframe = self.driver.switch_to.frame(
            self.driver.find_element_by_class_name("card-fields-iframe"))
        self.driver.switch_to.frame(hbocreditCardNumIframe)
        hbocreditCardNum = self.driver.find_element_by_name('number')
        hbocreditCardNum.send_keys(profile.ccNumber)
        self.driver.switch_to_default_content
        # Credit Card Owner
        # hbocreditCardOwner = self.driver.find_element_by_id("name")
        # hbocreditCardOwner.send_keys(profile.ccOwner)
        # # Credit Card Expiration Date
        # hbocreditCardExp = self.driver.find_element_by_id("expiry")
        # hbocreditCardExp.send_keys(profile.expDate)
        # # # Credit Card Security Code
        # hbocreditCardCCV = self.driver.find_element_by_id("verification_value")
        # hbocreditCardCCV.send_keys(profile.ccSecurityCode)
        # # Complete Order Button
        # hboCompleteOrderBtn = WebDriverWait(self.driver, 20).until(
        #     EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/div/div/form/div[3]/div[1]/button')))
        # hboCompleteOrderBtn.click()

    # def walmart_checkout_process(self):
    #     quantity = WebDriverWait(self.driver, 20).until(
    #         EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div[3]/div[4]/div[2]/div[1]/div/div/div/div[10]/div/div/div[1]/select/option[1]')))
    #     quantity.click()
    #     walmartACOBtn = WebDriverWait(self.driver, 20).until(
    #         EC.element_to_be_clickable((By.XPATH, '/ html/body/div[1]/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div[3]/div[4]/div[2]/div[1]/div/div/div/div[10]/div/div/div[2]/button'))
    #     walmartACOBtn.click()

    def init_driver(self):
        chrome_options = Options()
        if os.environ['POPENV'] == "dev":
            print('Not Setting Headless for Development Purposes')
        elif os.environ['POPENV'] == "stg":
            print("Will run checkout process without headless chrome option enabled")
        elif os.environ['POPENV'] == "prd":
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--credentials_enable_service=false")
        chrome_options.add_argument("--profile.password_manager_enabled=false")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--credentials_enable_service=false")
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-default-apps')

        # Rasberry Pi Support
        if get_distro() == "Linux":
            driver = webdriver.Chrome(executable_path=config.DRIVER_LOCATION, chrome_options=chrome_options)
            driver.wait = WebDriverWait(driver, 3)
            _LOG.info('Initialized Chrome Driver.')
            return driver
        # Windows Support
        elif get_distro() == "Windows":
            driver = webdriver.Chrome(executable_path=config.DRIVER_LOCATION, chrome_options=chrome_options)
            driver.wait = WebDriverWait(driver, 3)
            _LOG.info('Initialized Chrome Driver.')
            return driver
        # Darwin AKA: macOS Support
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
            driver.wait = WebDriverWait(driver, 3)
            _LOG.info('Initialized Chrome Driver.')
            return driver

    def check_funko(self, site, url):
        status = False

        _LOG.info('Checking: {0}'.format(site + " " + url))

        if site in ['hottopic', 'boxlunch']:
            status = self.in_stock(site, url)
        elif site in ['walmart', 'barnesandnoble', 'gamestop', 'blizzard', 'geminicollectibles', 'hbo']:
            status = self.add_to_cart(site, url)
        elif site in ['target']:
            status = self.out_of_stock(site, url)

        # Report from Bot When in Stock
        if status:
            msg = site + " - In Stock: " + ":\n" + url
            self.UPDATER.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID,
                  text=msg)

            #  Setting Timout for Search Item
            url_md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
            # When set prevents lookup until TIMEOUT Expires
            self.TIMEOUT[url_md5] = datetime.today().date()
            _LOG.info('Timeout Set: {0}'.format(url_md5))

            if site in ['hottopic', 'boxlunch']:
                # Adds Item to the Cart
                self.driver.get(url)
                # Check if Pop Overlay Exists
                popup = self.driver.find_elements_by_xpath('//*[@id="acsFocusFirst"]')

                # Logic to Close Pop when it does exist
                for popupCloseBtn in popup:
                    popInnerText = popupCloseBtn.get_attribute('innerText')
                    if popInnerText:
                        print('Pop Found Initiating Closer of Pop Up')
                        # Pop Up Found and Needs to be Dismissed
                        popup.click()
                    else:
                        self.driver.refresh()

                # TODO: Add Quantity Input for the Check Funko Function
                # A. This will also dictate the original message sent to channel
                # B. This will dictate number to buy
                # NOTE: May want to run multiple instances and buy in singles.
                # Setup Quantity Sudo Dynamic
                if os.environ['POPENV'] == "dev":
                    amount = "1"
                    quantitySelectorString = '//*[@id="Quantity"]/option[' + amount + ']'
                elif os.environ['POPENV'] == "stg":
                    amount = "3"
                    quantitySelectorString = '//*[@id="Quantity"]/option[' + amount + ']'
                elif os.environ['POPENV'] == "prd":
                    amount = "5"
                    quantitySelectorString = '//*[@id="Quantity"]/option[' + amount + ']'
                # Select Quantity
                quantity = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, quantitySelectorString)))
                quantity.click()
                # Add to Cart Button
                atcBtn = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(string(), "Add to Bag")]')))
                atcBtn.click()
                #  Logic to Decide Sites Cart Link
                if site in ['hottopic']:
                    cartLink = "https://www.hottopic.com/cart"
                    # Checkout Button
                    self.driver.get(cartLink)
                    # Function to do Checkout Process
                    self.ht_bl_checkout_process(site)
                    # Check if Pop Overlay Exists Again
                    # This is to allow for Clean Order Screenshot
                    popup = self.driver.find_elements_by_xpath('//*[@id="acsFocusFirst"]')

                    # Logic to Close Pop when it does exist
                    for popupCloseBtn in popup:
                        popInnerText = popupCloseBtn.get_attribute('innerText')
                        if popInnerText:
                            print('Pop Found Initiating Closer of Pop Up')
                            # Pop Up Found and Needs to be Dismissed
                            popup.click()
                        else:
                            self.driver.refresh()
                    # Take Screen Shot of Order
                    self.driver.save_screenshot("order.png")
                    self.UPDATER.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID,
                                                  text="Checkout was SUCCESSFUL! Order Screenshot Below")
                    self.UPDATER.bot.send_photo(chat_id=config.TELEGRAM_CHAT_ID, photo=open('./order.png', 'rb'))
                    # Quit After Checkout
                    self.driver.quit()
                    # Remove Order Image from Disk
                    subprocess.Popen('rm -rf ./order.png', shell=True, stdout=subprocess.PIPE)
                elif site in ['boxlunch']:
                    cartLink = "https://www.boxlunch.com/cart"
                    # Checkout Button
                    self.driver.get(cartLink)
                    # Function to do Checkout Process
                    self.ht_bl_checkout_process(site)
                    # Check if Pop Overlay Exists Again
                    # This is to allow for Clean Order Screenshot
                    popup = self.driver.find_elements_by_xpath('//*[@id="acsFocusFirst"]')

                    # Logic to Close Pop when it does exist
                    for popupCloseBtn in popup:
                        popInnerText = popupCloseBtn.get_attribute('innerText')
                        if popInnerText:
                            print('Pop Found Initiating Closer of Pop Up')
                            # Pop Up Found and Needs to be Dismissed
                            popup.click()
                        else:
                            self.driver.refresh()
                    # Take Screen Shot of Order
                    self.driver.save_screenshot("order.png")
                    self.UPDATER.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID,
                                                  text="Checkout was SUCCESSFUL! Order Screenshot Below")
                    self.UPDATER.bot.send_photo(chat_id=config.TELEGRAM_CHAT_ID, photo=open('./order.png', 'rb'))
                    # Quit After Checkout
                    self.driver.quit()
                    # Remove Order Image from Disk
                    subprocess.Popen('rm -rf ./order.png', shell=True, stdout=subprocess.PIPE)
            elif site in ['walmart', 'barnesandnoble', 'gamestop', 'blizzard', 'geminicollectibles', 'hbo']:
                # Checkout Process for Other Sites
                if site in ['hbo']:
                    self.hbo_checkout_process()
                # elif site in ['walmart']:
                #     self.walmart_checkout_process()
                else:
                    print("Still Work In Progress - Site(s): B&N, Gamestop, Blizzard, Gemini Collectibles")
            elif site in ['target']:
                print("Still Work In Progress - Site(s): Target")


    def set_cookies(self):
        self.driver.get('https://www.hottopic.com')
        self.driver.get('https://www.boxlunch.com')

    def pop_search(self, sleep_interval=2):
        self.set_cookies()
        # Set Bot to Auto Start
        self.THREAD_ALIVE = True
        # Start Infinite Loop to Check if Funko Pop is Available
        while True:
            # Load in items from pops.json
            if self.THREAD_ALIVE:
                with portalocker.Lock(config.FUNKO_POP_LIST, "r", timeout=10) as data_file:
                    funkopop_links = json.load(data_file)

                for funko in funkopop_links:
                    url_md5 = hashlib.md5(funko['url'].encode('utf-8')).hexdigest()
                try:
                    if url_md5 not in self.TIMEOUT:
                        self.check_funko(funko['store'], funko['url'])
                    elif url_md5 in self.TIMEOUT and self.TIMEOUT[url_md5] < datetime.today().date():
                        if datetime.now().hour > 7:
                            self.check_funko(funko['store'], funko['url'])
                except Exception as excp:
                    _LOG.error('Exception {0}'.format(excp))
                    import traceback
                    traceback.print_exc()

            time.sleep(sleep_interval)

    def in_stock(self, site, url):
        self.driver.get(url)

        try:
            inStock = self.driver.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, HTML_OBJ[site])))
        except TimeoutException:
            _LOG.error('Failed to locate element for "In Stock".')
            return False

        if inStock and inStock.text.lower() == "in stock":
            return True

        return False

    def out_of_stock(self, site, url):
        self.driver.get(url)

        try:
            outOfStock = self.driver.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, HTML_OBJ[site])))
        except TimeoutException:
            _LOG.error('Failed to locate element for "Out of Stock".')
            return False

        if outOfStock and "out of stock" in outOfStock.text.lower():
            return False

        return True

    def add_to_cart(self, site, url):
        response = False
        self.driver.get(url)

        try:
            if site == 'blizzard':
                addToCart = self.driver.wait.until(
        EC.presence_of_element_located((By.ID, HTML_OBJ[site])))
            elif site == 'hbo':
                addToCart = self.driver.wait.until(
        EC.presence_of_element_located((By.ID, HTML_OBJ[site])))
            else:
                addToCart = self.driver.wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, HTML_OBJ[site])))
        except TimeoutException:
            _LOG.warning('Failed to locate element for "Add to Cart".')
            return False

        if addToCart and addToCart.text.lower() == "add to cart":
            response = True
        elif addToCart and addToCart.get_attribute('value') in ["ADD TO CART", "Add To Cart"]:
            response = True

        return response
