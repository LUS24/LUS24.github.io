import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # (1)!
from selenium.webdriver.support import expected_conditions as EC  # (2)!
from datetime import datetime


class AACTDataElementsDownloader:
    """
    Class to download the contents of the AACT data elements
    dynamic table.
    """

    def __init__(self, url):
        self.url = url
        self.driver = None
        self.download_path = None
        self.wait = None
        self.metadata = None

    def setup_webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # (3)!
        chrome_options.add_argument("window-size=1920,1080")  # (4)!
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, timeout=10, poll_frequency=1)  # (5)!

    def load_page(self):
        self.driver.get(self.url)

    def wait_for_table(self):
        table_selector = '//*[@id="jsGrid"]/div[2]/table/tbody/tr[1]/td[3]'

        self.wait.until(EC.presence_of_element_located((By.XPATH, table_selector)))
        self.wait.until(
            EC.visibility_of(self.driver.find_element(By.XPATH, table_selector))
        )
        return True

    def click_next_button(self):
        self.driver.execute_script(
            """Array.from(document.querySelectorAll('span.jsgrid-pager-nav-button a'))
                .find(el => el.textContent.trim() === "Next").click()"""
        )

    def update_total_pages(self):
        total_pages = self.driver.execute_script(
            """return document.querySelector("div.jsgrid-pager-container")
                .textContent;"""
        )
        total_pages = int(total_pages.split(" ")[-2])
        return total_pages

    def get_total_pages(self):
        total_pages = self.update_total_pages()
        while total_pages == 0:
            total_pages = self.update_total_pages()
        return total_pages

    def get_data_elements_metadata(self):
        current_page = self.driver.execute_script(
            """return document.querySelector("div.jsgrid-pager-container")
                .textContent;"""
        )
        current_page = int(current_page.split(" ")[-4])
        total_pages = self.get_total_pages()
        table_headers = self.driver.execute_script(
            """return Array.from(document.querySelectorAll("#jsGrid div th"))
            .map(element => element.textContent);"""
        )
        table_data = []
        while current_page <= total_pages:
            print(f"Current page: {current_page} of {total_pages}")
            if self.wait_for_table():
                row_data = self.driver.execute_script(
                    """return Array.from(document.querySelectorAll("table.jsgrid-table tbody tr"))
                        .map(row => Array.from(row.querySelectorAll("td"))
                        .map(cell => cell.textContent));"""
                )
                table_data.extend(row_data)
            if current_page == total_pages:
                break
            self.click_next_button()
            current_page += 1
        self.driver.quit()
        self.metadata = pd.DataFrame.from_records(table_data, columns=table_headers)
        self.metadata.to_csv(self.download_path, index=False)
        print("Data Elements metadata downloaded and saved")

    def download_metadata(self):
        self.setup_webdriver()
        self.load_page()
        self.get_data_elements_metadata()

    def finalize(self):
        self.driver.quit()


if __name__ == "__main__":
    METADATA_URL = "https://aact.ctti-clinicaltrials.org/data_dictionary"
    today = datetime.today().strftime("%Y-%m-%d")
    metadata_downloader = AACTDataElementsDownloader(METADATA_URL)
    metadata_downloader.download_path = f"{today}_aact_data_elements_metadata.csv"
    metadata_downloader.download_metadata()
    metadata_downloader.finalize()
