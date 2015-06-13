import time
import json
import sys
from selenium import webdriver
from selenium.common import exceptions


SLEEP_INTERVAL = 1800
MAX_RETRIES = 20


class Webpage(object):
    """A headless PhantomJS page running the formular page"""
    def __init__(self, info):
        super(Webpage, self).__init__()
        self.info = info
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1366, 768)
        self.url = "https://formular.berlin.de/xima-forms-29/get/14278898950750000?mandantid=/OTVBerlin_LABO_XIMA/000-01/instantiationTasks.properties"

    def run_flow(self):
        self.driver.get(self.url)
        self.print_title()
        self.screenshot("homepage")
        self.click_button("#btnTerminBuchen")  # schedule a meeting
        self.make_selection("#cobStaat", "441")  # set country in the DD
        self.make_selection("#cobFamAngInBerlin", "Nein")  # answer 'No' in the second DD
        self.make_selection("#cobAnliegen", "305156")  # select type of visa wanted
        self.make_selection("#cbZurKenntnis", "true", "click", "checked")  # check terms and conditions
        self.click_button("#labNextpage")  # click on next page button
        self.make_selection("#tfFirstName", self.info["firstname"], "blur")  # enter first name
        self.make_selection("#tfLastName", self.info["lastname"], "blur")  # enter last name
        self.make_selection("#cobGebDatumTag", self.info["day"])  # enter day of birth
        self.make_selection("#cobGebDatumMonat", self.info["month"])  # enter month of birth
        self.make_selection("#tfGebDatumJahr", self.info["year"], "blur")  # enter year of birth
        self.make_selection("#cobVPers", "1")  # enter number of persons applying
        self.make_selection("#tfMail", self.info["email"], "blur")  # enter e-mail address
        self.make_selection("#cobGenehmigungBereitsVorhanden", "Nein")  # "do you already have a residence permit?"
        self.click_button("#txtNextpage")  # click on next page button

    def select_month(self, month, year):
        while True:
            m = self.wait_for_visibility("#month")
            y = self.wait_for_visibility("#year")
            if (m.text.strip(), y.text.strip()) == (month, year):
                break
            self.click_button("#labnextMonth")

    def check_availability(self, start_day, end_day):
        available_dates = self.driver.find_elements_by_css_selector(".CELL a[link='1']")
        return [date.text for date in available_dates if int(date.text) in range(start_day, end_day)]

    def click_button(self, selector):
        tag = self.wait_for_visibility(selector)
        tag.click()
        self.screenshot(selector)
        self.print_title()

    def make_selection(self, selector, value, event="change", attribue="value"):
        self.wait_for_visibility(selector)  # make sure element is visible
        # print("COMMAND:")
        # print('document.querySelector("%s").%s = "%s"' % (selector, attribue, value))
        self.driver.execute_script('document.querySelector("%s").%s = "%s"' % (selector, attribue, value))
        # print("COMMAND:")
        # print('document.querySelector("%s").dispatchEvent(new Event("%s"))' % (selector, event))
        self.driver.execute_script('document.querySelector("%s").dispatchEvent(new Event("%s"))' % (selector, event))

    def wait_for_visibility(self, selector, timeout_seconds=5):
        retries = timeout_seconds
        pause_interval = 2
        while retries:
            # print("tries left: {}".format(retries))
            try:
                element = self.driver.find_element_by_css_selector(selector)
                if element.is_displayed():
                    return element
                elif "visible" in element.value_of_css_property("visibility"):
                    print("trying to focus on element")
                    self.driver.execute_script("$(\"" + selector + "\").focus()")
            except (exceptions.NoSuchElementException,
                    exceptions.StaleElementReferenceException):
                if retries <= 0:
                    raise
                else:
                    pass

            retries = retries - 1
            time.sleep(pause_interval)
        raise exceptions.ElementNotVisibleException(
            "Element {} not visible despite waiting for {} seconds".format(
                selector, timeout_seconds * pause_interval)
        )

    def print_title(self):
        print("Page title:")
        print(self.driver.title.encode('utf-8'))

    def screenshot(self, filename):
        print("saving %s" % filename)
        self.driver.save_screenshot(filename + ".png")

    def quit(self):
        print("closing page...")
        self.driver.quit()


def get_info(filename):
    with open(filename, "rb") as f:
        return json.loads(f.read())


def main(filename):
    info = get_info(filename)
    print(info)
    for i in xrange(MAX_RETRIES):
        print("************ MESSAGE FROM: " + info["email"] + " ************")
        page = Webpage(info)
        page.run_flow()
        page.select_month(info["wantedmonth"], info["wantedyear"])
        print("Checking for available dates....")
        result = page.check_availability(int(info["startrange"]), int(info["endrange"]))
        if len(result) > 0:
            print("Available date found in the given range!")
            print("Available dates are:")
            print(result)
            page.screenshot("SUCCESS!")
            break
        print("No available dates in the given range...")
        print("Sleeping for %d" % SLEEP_INTERVAL)
        page.quit()
        print("***************************************************\n")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    print(sys.argv[1])
    main(sys.argv[1])
