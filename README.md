Instructional Guide: Scraping Rehabilitation Data from Wildman
Cinthia Pietromonaco, Matias Villalba Lara
cinthia.pietromonaco@sydney.edu.au

**PERMISSION AND USER ACCESS MUST BE GRANT BY GROUP PRIOR TO SCRAPING**

Overview
This workflow is designed to extract rehabilitation records from the Wildman database.
 
Files

•	WebScraper.py – automates data requests to Wildman using those IDs, consolidating the results into a single csv file.

•	config.txt
 
Software
•	Python 3.x
 
Step 1: Download bat IDs from Wildman
1.	Login to Wildman database
2.	Go to ‘Reports’
3.	Click ‘Animal Summary Report’
4.	Change settings as desired
5.	Copy and paste table in excel and save as CSV named ‘numbers.csv’ in working directory with scripts. No headers required.
 
Step 2: Configuration
•	Authentication (config.txt): update the section in italics relevant to your access.
o URL: https://YOURLINKTOWILDMANTHROUGHORGANISATION/AnimalExportMultipleForm.php
o	Login: Your login name
o	Password: Your login password

Step 2: Download Records (WebScraper.py)
Run script. This script logs into the Wildman export page and retrieves XML records for each specified ID, then transforms into csv file.


•	Input: numbers.csv – each row contains one record ID. No header.
•	Output: Consolidated_WildManExport.csv – a combined csv file containing all records. 
•	Output details (change as desired):
        "Animal_Number",
        "Animal_Scientific_Name",
        "Animal_Birth_Date",
        "Animal_Sex",
        "Animal_Status",
        "Animal_Growth_Stage",
        "Animal_Vet_Number",
        "Animal_Care_Group",
        "Animal_Place_Of_Origin",
        "Animal_Care_Reason",
        "Animal_Arrival_Notes",
        "Measure_Date",
        "Weight",
        "Arm_Length"
