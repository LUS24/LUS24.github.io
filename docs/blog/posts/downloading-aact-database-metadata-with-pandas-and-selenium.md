---
title: Downloading AACT database metadata with Pandas and Selenium
date: 2024-03-09
authors:
  - leonardo
categories:
  - Python
  - Selenium
  - Pandas
  - Clinical Trials
  - Data Extraction
  - Webscrapping
comments: true
---

# Downloading AACT database metadata with Pandas and Selenium

In this post I will present how I downloaded the HTML tables that contain the metadata of the "Access to Aggregate Content of ClinicalTrials.gov" (AACT) database and store them as comma separated values (csv) files. The objective is to use this information to create an interactive dashboard that will help users understand the contents of the database.

<!-- more -->

The metadata is comprised of [three HTML tables on the same webpage](https://aact.ctti-clinicaltrials.org/data_dictionary). They are the following:

- The **"AACT Data Elements"** table that contains the names of the tables and the columns along with the column descriptions.
- The "**AACT Tables**" table, with information about study-related tables. The information that I'm interested in is the table name and their description.
- The **"AACT Views & Functions"** table, which contains information about the views and functions in used to make data retrieval easier.

Without further ado, let's get started.

## Requirements

- A working linux installation. I'm running Ubuntu 22.04 in [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install) on Windows 11.

- A Python environment. I'm using [miniconda](https://docs.anaconda.com/free/miniconda/index.html) with a Python 3.11.7 virtual environment.

- Installing the [chrome-driver](https://chromedriver.chromium.org/). In Ubuntu it can be done using the commands below:

```bash
sudo apt-get update
sudo apt install chromium-chromedriver -y
```

- Installing the following python packages:
    - [`selenium`](https://www.selenium.dev/documentation/): we will use it to load the JavaScript-dependent **"AACT Data Elements"** table and extract it's text. This approach is relatively slow but since it is on operation I don't consider that spending time optimization is worth it.
    - [`pandas`](https://pandas.pydata.org/): we will use it to extract the **"AACT Tables"** and **"AACT Views & Functions"** tables. We don't need selenium for those because they are static, meaning that they are already in the HTML when the page is loaded and don't depend on JavaScript to be rendered. Additionally, we will use `pandas` to do some data manipulation and then store the tables as csv files.
    - [lxml](https://lxml.de/): it is a dependency of `pandas` and is used to parse the HTML and extract the tables.

To install the packages, run the following command:

```bash
pip install selenium pandas lxml
```

Once we have the requirements installed, we can start coding.

## Download the metadata

For downloading the metadata, we will use two approaches, one for static tables (the simple ones) and another for the dynamic table (the one that depends on JavaScript to be rendered).

### Downloading the static tables

After inspection of the HTML source code of the page, I found that both static tables have the same class name `dictionaryDisplay`. With that information, we can use the `pandas.read_html` function to extract the tables from the HTML and then store them as csv files. I created a file named `download-static-tables-metadata.py` with the following code:

```python title="download-static-tables-metadata.py" linenums="1"
--8<-- "docs\assets\posts\downloading-aact-database-metadata-with-pandas-and-selenium\code\download-static-tables-metadata.py"
```

After running the code with the command `python download_aact_metadata.py`, we will have two csv files with the metadata of the **"AACT Tables"** and **"AACT Views & Functions"** tables.


### Downloading the dynamic table

To tackle the dynamic table, we will use Selenium to load the page and extract the table. The code is a bit more complex than the previous one, that is why I decided to create a separate file for it.

Additionally, I used Python classes to organize the code and make it more readable and maintainable.

!!! tip "Code explanations"
    Click the little "+" buttons in the code to see the explanation of each part.

!!! info "JavaScript code"
    In a few of the functions I decided to use JavaScript to interact with the page. This is because the page updated the DOM after the table was loaded resulting in the following exceptions when trying to interact using Selenium directly:

    - [ElementNotInteractableException](https://www.selenium.dev/selenium/docs/api/java/org/openqa/selenium/ElementNotInteractableException.html).
    - [StaleElementReferenceException](https://www.selenium.dev/selenium/docs/api/java/org/openqa/selenium/StaleElementReferenceException.html).


```python title="download-dynamic-table-metadata.py" linenums="1"
--8<-- "docs\assets\posts\downloading-aact-database-metadata-with-pandas-and-selenium\code\download-dynamic-tables-metadata.py"
```

1. [WebDriverWait](https://www.selenium.dev/documentation/webdriver/waits/) is used to add selenium's explicit wait to the code. It will wait for the element to be present in the DOM before trying to extract it's text.
2. [EC (expected condition)](https://www.selenium.dev/documentation/webdriver/support_features/expected_conditions/) is used in combination with WebDriverWait to wait for something specific to happen before proceeding with the code.
3. Headless mode is used to run the browser without a graphical interface. This is useful when running the code in a terminal, for example in a server environment.
4. I used a FullHD window size to make sure that the table is fully rendered. This is important because the `find_element` method will only find the elements that are visible in the viewport.
5. The wait is configured to check every 1 second if the expected condition is met with a time limit of 10 seconds before raising a `TimeoutException`.

As you can see there are quite a few lines of code, but the process is relatively straight forward:

  1. The page is loaded.
  2. A wait is added to make sure that the table is fully rendered.
  3. The total number of pages is extracted.
  4. The current page number is extracted.
  5. The table data from the current page is extracted and saved into a variable.
  6. The next button is clicked and the and the current page is updated by adding 1.
  7. Steps 2, 5 and 6 are repeated until the last page is reached.
  8. The table data is saved as a csv file.
  9. The browser is closed.

After running the code with the command `python download-dynamic-tables-metadata.py`, you should and an output like this:

```bash
Current page: 1 of 12
Current page: 2 of 12
Current page: 3 of 12
Current page: 4 of 12
Current page: 5 of 12
Current page: 6 of 12
Current page: 7 of 12
Current page: 8 of 12
Current page: 9 of 12
Current page: 10 of 12
Current page: 11 of 12
Current page: 12 of 12
Data Elements metadata downloaded and saved
```

Finally, a file with the name `aact-data-elements.csv` will be created in the same directory as the script.

??? info "Possible improvements"
    A few improvents that can be made are:
    
    - Refactor the `download_table` method to use a while loop instead of a for loop. This way we can avoid the need to know the total number of pages before starting the download. 
    - Add a try-except block to handle possible exceptions and gracefully close the browser in case of an error.
    - Add a logger to the script to make it easier to debug and understand what is happening.
    - Add tests.
    - Add type hints.
    - Add docstrings.

## Conclusion

In this post I presented how I downloaded the metadata of the "Access to Aggregate Content of ClinicalTrials.gov" (AACT) database using Python, Selenium and Pandas. Selenium was used to deal with the JavaScript-dependant table and Pandas to extract the data from the simple HTML tables and store all the information in CSV files. 

We saw that the Selenium code is a bit more complex than the Pandas code, so it is a good idea to use classes to organize the code and make it more readable and maintainable. Additionally, we saw that it is possible to use JavaScript (through Selenium) to interact with the page and avoid some exceptions that can be raised when trying to interact with the page using Selenium directly.

In the upcoming posts I will present how I cleaned the data and metadata, calculated some statistics and stored the results in files ready to be used in a dashboard.
