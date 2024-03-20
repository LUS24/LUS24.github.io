---
title: Exploring the AACT database metadata
date: 2024-03-15
authors:
  - leonardo
categories:
  - Python
  - Pandas
  - Clinical Trials
  - Data Extraction
comments: true
donations: true
---

# Exploring the AACT database metadata

The objective of this blog post is to explore the downloaded metadata of the "Access to Aggregate Content of ClinicalTrials.gov" (AACT) database, create a brief report, and extract the data that I will use to create an interactive dashboard.

<!-- more -->
In the previous post ([Downloading AACT database metadata with Pandas and Selenium](./downloading-aact-database-metadata-with-pandas-and-selenium.md)) I downloaded three tables:

- The **"AACT Data Elements"** table that contains the names of the tables and the columns along with the column descriptions.
- The "**AACT Tables**" table, with information about study-related tables. The information that I'm interested in is the table name and their description.
- The **"AACT Views & Functions"** table, which contains information about the views and functions in used to make data retrieval easier.

Let