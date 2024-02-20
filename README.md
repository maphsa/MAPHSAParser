# MAPHSA Parser

Parser meant to read semi-structured dataframes and ingest the resulting heritage site data into a **QGIS/PostGIS database**. 

## General Architecture
The projected architecture forsees the pipeline to funnel data to both of the databases.
* The **Centralized MAPHSA QGIS Database** will hold the integrated depository of heritage data for the project meant to be edited and rendered.
* Every **Source Heritage Data Source** contains heritage site semi-structured data relevant to MAPHSA.
* The **Abstract MAPHSA Parser** is used to specialized **Specialized MAPHSA Parsers** capable of parsing the relevant **Source Heritage Data Source** and ingesting the result into the **Centralized MAPHSA QGIS Database**.
* The **MAPHSA Arches Parser** can extract data from the **Centralized MAPHSA QGIS Database** and ingest it into the **MAPHSA Arches Server**.
```mermaid
graph TD
AMP[\Abstract MAPHSA Parser\] -.-> SMPA[/Specialized MAPHSA Parser A/]
AMP -.-> SMPB[/Specialized MAPHSA Parser B/]
SHDA[(Heritage Data Source A)] -- Data Parsing --> SMPA
SHDB[(Heritage Data Source B)] -- Data Parsing --> SMPB
SMPA-- Data Ingestion --> CMQGISD[(Centralized MAPHSA QGIS Database)]
CMQGISD <-- Data Interface --> MQGISF[MAPHSA QGIS User Experience]
MQGISF <-- Site Browsing --> PU(Project User)
SMPB-- Data Ingestion --> CMQGISD
CMQGISD-- Structured Extraction -->AP[/MAPHSA Arches Parser/]
AP-- Ingestion --> MAD[(MAPHSA Arches Database)]
MAD <-- Data Interface --> MAS[MAPHSA Arches Server]
MAS[MAPHSA Arches Server] <-- Site Browsing --> EU(End User)


```

## Supported Source Heritage Data Sources
* Brazilian SICG data.
* Colombian IPHAN data.

## Major Update History
* 11/17/2023 - Initial commit. SICG data support is built-in.
* 02/20/2024 - Add Colombian ICANH data support.

### Sample Run Commands

```commandline
python command.py database_interface build_database
python command.py arches load_concepts -i ~/archesExportData/maphsa-pkg-master/reference_data/*.xml
python command.py parse icanh -i sources/icanh_sites_filtered.csv
python command.py parse sicg -i sources/iphan_sites.csv -sg

```
