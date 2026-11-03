# Directory collection and import
Copy collect.py, the license, and data/directory.json into the existing Honeybee project, preserving the data folder. Keep this note as COLLECTION.md in the final repository.

The bundled file contains 550 unique directory listings from Open Brewery DB's published CSV. The source CSV Git blob was 73f1c591d94a8bf507f02b4110394b8a117e75cb, obtained on 4 November 2026 IST. Source: https://github.com/openbrewerydb/openbrewerydb/blob/master/breweries.csv . The collector reads the directory's structured export, not HTML pages. Rebuild with python collect.py or use python collect.py --csv breweries.csv with a downloaded snapshot. Later source revisions may produce different results.

The collector takes the first 550 qualifying records in directory order. It skips listings marked closed or planning and rows missing a name, street, city, or category. Brewery type supplies the category. Missing phone numbers stay null. It deduplicates by case-insensitive name, city and address within this source. Listings are directory records, not independently verified operating businesses. Cities group by directory city label. Source-wise reporting correctly shows one source for the real dataset.

From the running project's PowerShell terminal:
~~~powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/listings -ContentType 'application/json; charset=utf-8' -InFile .\data\directory.json
docker compose exec db mysql -udashboard -plocal_demo_only honeybee -e "SELECT source, COUNT(*) AS listings FROM listing_master GROUP BY source;"
~~~
Compare the Open Brewery DB count with 550. Reimporting the same file should insert zero additional rows. Before the final database export, exclude the ten synthetic test records; keep the original fixture available for testing. The starter README explains how to export the final database.
