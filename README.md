\# NYC 311 Monitor



A Python-based monitoring system for analyzing NYC 311 service requests, storing historical complaint data, detecting unusual activity using contextual historical baselines, and investigating alerts through a Streamlit dashboard.



The project was built as an end-to-end data pipeline and alerting system, with an emphasis on explainable anomaly detection rather than fixed complaint-count thresholds.



\## What It Does



The system:



1\. Fetches NYC 311 service requests from the NYC Open Data API.

2\. Processes and categorizes incoming records.

3\. Stores complaint data in SQLite with duplicate protection.

4\. Evaluates complaint activity against historical, context-specific baselines.

5\. Generates email alerts when activity is unusually high.

6\. Provides a Streamlit dashboard for exploring historical complaint patterns and investigating alerts.

7\. Supports scheduled ingestion, alert evaluation, and historical backfills.



\## Architecture



```text

NYC 311 Open Data API

&#x20;       │

&#x20;       ▼

&#x20;   Data Fetching

&#x20;       │

&#x20;       ▼

&#x20;  Data Processing

&#x20;       │

&#x20;       ▼

&#x20;     SQLite

&#x20;       │

&#x20;       ├───────────────┐

&#x20;       │               │

&#x20;       ▼               ▼

&#x20; Alert Detection   Dashboard

&#x20;       │

&#x20;       ▼

&#x20;Alert Aggregation

&#x20;       │

&#x20;       ▼

&#x20;  SendGrid Email

```



\## Alert Detection



The alert system is designed to answer:



> "Is this complaint volume unusual for this particular situation?"



Rather than using a fixed threshold such as "100 complaints means an alert," the detector builds a historical baseline using comparable periods.



The baseline considers:



\* Borough

\* Complaint category

\* Hour of day

\* Day of week

\* Season

\* Historical lookback period



The current implementation uses a \*\*365-day historical lookback\*\* and a \*\*95th-percentile threshold\*\*.



Comparable historical periods include zero-count periods rather than ignoring them, while a minimum amount of nonzero historical activity is required before an alert can be generated.



This approach helps account for recurring patterns such as higher Noise complaint volume on weekend evenings compared with weekday evenings.



\### Alert aggregation



Multiple alert conditions can be evaluated during the same alert cycle. Rather than sending a separate email for every individual trigger, the system aggregates triggered conditions into a single notification.



\## Data Processing



Incoming 311 records are normalized and enriched with additional fields used by the alerting system and dashboard.



Examples include:



\* Hour of day

\* Time bucket

\* Hour label

\* Day of week

\* Weekend indicator

\* Complaint category



Current complaint categories include:



\* Noise

\* Heat / Hot Water

\* Rodents

\* Water System

\* Sanitation

\* Parking

\* Other



\## Database



The project uses SQLite for local persistence.



The database stores the underlying complaint records so that historical activity can be:



\* Analyzed

\* Used for baseline calculations

\* Backtested

\* Investigated through the dashboard

\* Used to explain why an alert was generated



Records are deduplicated using the NYC 311 `unique\_key`.



The `created\_date` field is indexed to support historical date-range and aggregation queries.



The local database is intentionally excluded from Git because it is generated application data rather than source code.



\## Dashboard



The project includes a Streamlit dashboard for exploring the stored 311 data.



Launch it with:



```powershell

python -m streamlit run src\\app\\dashboard.py

```



The dashboard provides:



\* Total complaint counts

\* Most recent completed-hour activity

\* Last data received

\* Historical complaint trends

\* Borough filtering

\* Complaint category filtering

\* Hour/date filtering

\* Alert investigation



The Alert Investigation view exposes the historical comparison used by the detector, including the current count, calculated threshold, and comparable historical observations.



\## Scheduled Pipeline



The project includes an APScheduler-based scheduler.



Run it from the repository root with:



```powershell

python -m src.app.scheduler

```



The scheduler is configured to:



\* Run ingestion every 15 minutes

\* Evaluate alerts hourly at five minutes past the hour

\* Evaluate the previous completed clock hour

\* Use overlapping ingestion windows to provide protection against delayed records

\* Rely on database deduplication to make overlapping fetches safe



\### Data freshness limitation



The NYC 311 dataset used by this project is a public NYC Open Data dataset that is updated daily.



Therefore, although the application contains a 15-minute scheduled ingestion pipeline, \*\*the system cannot provide true real-time monitoring when the upstream dataset has not received new data\*\*.



The scheduler demonstrates the periodic ingestion and alerting architecture, while the actual freshness of the system is constrained by the upstream NYC 311 dataset.



\## Historical Backfills



Historical data can be loaded using the backfill command:



```powershell

python run.py --backfill N

```



where `N` is the number of days to backfill.



Backfills use daily API windows and feed the same processing and database pipeline used by normal ingestion.



\## Alert-Only Evaluation



Alerts can be evaluated against data that is already stored locally without fetching new data:



```powershell

python run.py --alerts-only

```



This is useful for testing and historical analysis of the alerting system.



\## Normal Pipeline



The standard pipeline can be run with:



```powershell

python run.py

```



The pipeline fetches data, processes it, stores new records, and evaluates alerts.



\## Email Alerts



Email notifications are sent through SendGrid.



The application expects SendGrid configuration to be provided through environment variables rather than committed to the repository.



The `.env` file is intentionally excluded from Git.



\## Testing



The project uses pytest.



Run the complete test suite with:



```powershell

pytest

```



The test suite covers:



\* Alert detection

\* Alert formatting

\* Alert runner behavior

\* Email sending

\* API fetching and retry behavior

\* Pipeline execution

\* Scheduler behavior



Current test suite:



\*\*20 tests passing\*\*



\## Project Structure



```text

nyc-311-monitor/

│

├── README.md

├── requirements.txt

├── pytest.ini

├── logging\_config.py

├── run.py

│

├── src/

│   ├── alerts/

│   │   ├── detector.py

│   │   ├── formatter.py

│   │   └── runner.py

│   │

│   ├── app/

│   │   ├── backfill.py

│   │   ├── dashboard.py

│   │   ├── db.py

│   │   ├── fetch\_data.py

│   │   ├── process\_data.py

│   │   └── scheduler.py

│   │

│   └── email/

│       ├── email\_sender.py

│       └── sendgrid\_client.py

│

└── tests/

&#x20;   ├── test\_detector.py

&#x20;   ├── test\_email\_sender.py

&#x20;   ├── test\_fetch\_data.py

&#x20;   ├── test\_formatter.py

&#x20;   ├── test\_run.py

&#x20;   ├── test\_runner.py

&#x20;   └── test\_scheduler.py

```



\## Setup



Create and activate a Python virtual environment:



```powershell

python -m venv venv

.\\venv\\Scripts\\Activate.ps1

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



Configure the required environment variables in `.env`.



Run the tests:



```powershell

pytest

```



\## Design Decisions



Several design decisions shaped the project:



\### Contextual baselines instead of fixed thresholds



Complaint volume varies significantly by time, location, complaint type, and season. A fixed threshold can therefore produce misleading alerts.



The detector instead compares activity with historically comparable periods.



\### Raw complaint records as the source of truth



The database stores individual complaint records rather than only precomputed aggregates. This preserves the underlying evidence needed for analysis, backtesting, and explaining alerts.



\### Database deduplication



Ingestion windows intentionally overlap. Duplicate protection at the database layer makes overlapping fetches safe and provides resilience against delayed or repeated API results.



\### 365-day baseline



A one-year lookback provides enough historical observations to capture recurring seasonal and weekly patterns while keeping the baseline reasonably relevant to current conditions.



\### V1 scope



The initial alert model focuses on configurable combinations of:



\* Borough

\* Complaint type/category

\* Time/frequency conditions



More granular geographic conditions such as radius-based monitoring are considered future functionality rather than part of the current implementation.



\## Limitations



The project has several known limitations:



\* The public NYC 311 dataset is updated daily, limiting effective data freshness.

\* API windows larger than the configured fetch limit would require additional pagination handling.

\* Historical baseline quality depends on the amount and distribution of stored data.

\* The current geographic configuration uses borough-level monitoring rather than arbitrary-radius locations.

\* Email delivery depends on external SendGrid configuration.



\## Future Ideas



Potential future extensions include:



\* Radius-based geographic monitoring

\* More configurable alert conditions

\* Additional anomaly-detection approaches

\* More advanced dashboard visualizations

\* Improved handling of large API result sets

\* Additional notification channels



These are intentionally outside the current V1 implementation.



\## Project Status



The initial implementation is complete and includes:



\* NYC 311 data ingestion

\* Data processing and categorization

\* SQLite persistence

\* Duplicate protection

\* Historical backfill support

\* Contextual anomaly detection

\* Alert aggregation

\* SendGrid email notifications

\* Scheduled ingestion and alert evaluation

\* Streamlit dashboard

\* Automated tests

\* Historical detector validation



