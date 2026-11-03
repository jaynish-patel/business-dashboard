# Business Listings Dashboard

Explore 550 business listings by city, brewery category, and directory source. A Python collector prepares the records, FastAPI validates and inserts them into MySQL, and a React dashboard displays the grouped counts.

## Run the dashboard on Windows

Start Docker Desktop in Linux container mode. Open PowerShell in the project folder containing `compose.yaml` and run:

```powershell
docker compose up --build -d
docker compose ps
```

Wait until `db` is healthy and `api` and `frontend` are running. Import the bundled dataset and open the dashboard:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/listings -ContentType 'application/json; charset=utf-8' -InFile .\data\directory.json
Start-Process http://localhost:5173
```

On an empty database, the response should show **550 received and 550 inserted**. Importing the same file again should show **550 received and 0 inserted**. Click **Refresh counts** in the dashboard after an import.

## Check the results

Each chart groups the same 550 listings. The source chart should contain one bar labeled **Open Brewery DB**. To verify all three totals from PowerShell:

```powershell
$reports = Invoke-RestMethod http://localhost:8000/api/dashboard
foreach ($group in 'city', 'category', 'source') {
    $total = ($reports.$group | Measure-Object -Property count -Sum).Sum
    Write-Output "$group = $total"
}
```

Expected output for the submission dataset:

```text
city = 550
category = 550
source = 550
```

## Collection and data quality

`collect.py` reads Open Brewery DB’s published CSV and takes the first 550 qualifying listings in directory order. It captures business name, brewery type as category, city, address, phone when available, and source. Collection details and the source snapshot identifier are in [COLLECTION.md](COLLECTION.md). The dataset license is in [OPENBREWERYDB-LICENSE.txt](OPENBREWERYDB-LICENSE.txt).

| Data challenge | Handling |
| --- | --- |
| Incomplete or inactive listings | The collector skips records missing a name, city, category, or street address and excludes entries marked closed or planning. Missing phone numbers are stored as SQL NULL. |
| Repeated rows or repeated imports | The collector deduplicates records. MySQL also enforces a unique fingerprint of source, business name, city, and address so retrying a request preserves the count. |
| Changes to the upstream directory | The bundled JSON reproduces the submission dataset. Running `python collect.py` rebuilds it from the current directory and can produce a different selection. |

## Project layout and API

| Path | Purpose |
| --- | --- |
| `frontend/` | React dashboard and Vite development server |
| `backend/` | FastAPI service with request validation and parameterized inserts |
| `data/directory.json` | The 550 records used for the dashboard |
| `data/sample.json` | Ten synthetic records for separate development tests |
| `database/schema.sql` | Creates the MySQL table on first startup |
| `database/listings.sql` | Populated MySQL export for the submission |

`POST /api/listings` accepts a JSON array of 1–1,000 listings and returns the received and inserted counts. `GET /api/dashboard` returns city, category, and source groups, each with a label and count. Explore both endpoints in the [local FastAPI docs](http://localhost:8000/docs).

To inspect a startup error, run `docker compose logs db api frontend`. To stop the stack and keep the database for the next run, use `docker compose down`.
