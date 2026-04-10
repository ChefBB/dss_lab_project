> Project for *Laboratory of Data Science* — M.Sc. Data Science, A.Y. 2025/26

# Decision Support System for a Music Streaming Company

**Course:** Laboratory of Data Science (Decision Support Systems — Module II)  
**University:** Università di Pisa — Master's in Data Science & Business Informatics  
**Academic Year:** 2025/26  
**Authors:** Federica Braghin, Bruno Barbieri, Nicholas Vannucci

## Overview

End-to-end decision support system built on a music streaming dataset (`tracks.json`, `artists.xml`).  
The project covers the full pipeline from raw data to interactive dashboards, simulating a real-world analytics environment for a streaming company.

## Pipeline

- **Data Understanding & Cleaning** — missing value analysis, song profiling via lyrics and melodic features
- **Data Warehouse Design** — star schema with fact table on monthly streams, dimension tables for artist, album, geography, date, and lyrics
- **ETL with SSIS** — data ingestion and transformation using SQL Server Integration Services
- **OLAP Analysis** — MDX queries in SQL Server Management Studio for multidimensional analysis
- **Dashboards** — interactive reports built in Power BI

## Tools & Technologies

- Python (data preparation and DB population)
- Microsoft SQL Server Management Studio (SSMS)
- SQL Server Integration Services (SSIS)
- SQL Server Analysis Services (SSAS) — datacube and MDX queries
- Power BI

## Presentation

Full methodology, results, and dashboard screenshots are documented in the project report (`report.pdf`).
