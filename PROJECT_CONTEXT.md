\# NYC 311 Monitor — Project Context



\## Project Purpose



NYC 311 Monitor is a Python project that monitors NYC 311 complaint data and

can generate automated alerts when potentially meaningful activity is detected.



The original purpose of the project is twofold:



1\. Build a substantial real-world coding project to improve practical software

&#x20;  engineering skills.

2\. Explore whether the monitoring/alerting concept could eventually become

&#x20;  something useful enough to turn into a business or SaaS product.



This is intentionally being built incrementally rather than starting with a

fully defined commercial product.



\---



\## Current Project Status



The project already has a working basic data pipeline:



&#x20;   NYC Open Data 311 API

&#x20;           ↓

&#x20;      fetch\_data.py

&#x20;           ↓

&#x20;     process\_data.py

&#x20;           ↓

&#x20;         SQLite

&#x20;           ↓

&#x20;       alert logic



The application is scheduled to run every 15 minutes using APScheduler.



The SendGrid email connection has been successfully tested.



The remaining major work is designing and implementing a useful, reliable

alert engine.



\---



\## Current Architecture



\### Data ingestion



`src/app/fetch\_data.py`



Fetches NYC 311 complaint data from the NYC Open Data API.



Current endpoint:



`https://data.cityofnewyork.us/resource/erm2-nwe9.json`



Current implementation requests the newest 1,000 records ordered by

`created\_date DESC`.



This works for the prototype but should eventually be changed to incremental

fetching based on the last successful fetch timestamp.



\---



\### Data processing



`src/app/process\_data.py`



Currently:



\- Converts `created\_date` to datetime

\- Normalizes borough names

\- Extracts hour of day

\- Creates time-of-day buckets

\- Creates human-readable time labels

\- Adds day-of-week

\- Identifies weekends

\- Categorizes complaints using keyword-based rules



Current categories include:



\- Noise

\- Heat/Hot Water

\- Rodents

\- Water System

\- Sanitation

\- Parking

\- Other



The categorization system is intentionally simple and can be improved later.



\---



\### Database



`src/app/db.py`



Uses SQLAlchemy with SQLite.



Database:



`data/311.db`



The database is local development state and should NOT be committed to Git.



`/data/` is included in `.gitignore`.



The database was previously tracked by Git and has now been removed from Git

tracking while preserving the local database file.



\---



\### Scheduler



`src/app/scheduler.py`



Uses APScheduler's `BlockingScheduler`.



Current behavior:



\- Runs the pipeline immediately when the scheduler starts

\- Runs again every 15 minutes

\- Logs exceptions from scheduled runs



\---



\### Main pipeline



`run.py`



Current pipeline:



1\. Fetch NYC 311 data

2\. Process the DataFrame

3\. Save complaints to SQLite

4\. Generate alerts

5\. Log generated alerts



There is also a `--run-alerts` option for running alert generation against

existing database data.



\---



\## Email System



\### Current working implementation



`src/email/email\_sender.py`



This is currently the preferred SendGrid implementation.



It:



\- Loads environment variables from `.env`

\- Reads `SENDGRID\_API\_KEY`

\- Uses `certifi` for SSL certificate verification

\- Creates a SendGrid client

\- Sends HTML email

\- Returns success/failure

\- Logs errors



SendGrid connectivity has been successfully tested.



A direct SendGrid sanity check returned:



`HTTP 202`



This confirms the API request was accepted by SendGrid.



\---



\### Older SendGrid implementation



`src/email/sendgrid\_client.py`



This appears to be an older/duplicate implementation.



It currently:



\- Creates its own SendGrid client

\- Uses a different sender address

\- Does not contain the newer SSL/certifi handling



Do not delete it yet. Decide whether to remove it after the email architecture

is finalized.



\---



\## Experimental New-Complaint Alert System



\### File



`src/alerts/new\_complaint\_alert.py`



This was created as an experimental implementation to prove that a newly

inserted complaint could trigger an email.



Current behavior:



`should\_trigger\_alert()` returns `True` for every new complaint.



This was intentionally done as a testing mechanism rather than as final

alert logic.



Current flow:



&#x20;   new complaint

&#x20;         ↓

&#x20;   should\_trigger\_alert()

&#x20;         ↓

&#x20;      send\_email()

&#x20;         ↓

&#x20;   mark alert\_sent=True



The database model currently includes:



\- `alert\_sent`

\- `alert\_sent\_at`



These were added to prevent duplicate notifications.



The current implementation is NOT considered final architecture.



\---



\## Existing Pattern/Spike Alert Logic



\### File



`src/app/alerts.py`



This contains an earlier experimental alert implementation.



It currently compares:



\- the most recent 3 days

\- against the previous 3 days



It checks for spikes in:



\- total complaints

\- complaint categories

\- boroughs



The current threshold is approximately 1.5x the previous period.



This logic is NOT considered final.



It currently generates strings/log messages rather than being integrated

properly with the email notification system.



\---



\## Important Architectural Direction



The intended direction is a rules-based alert engine rather than a collection

of hardcoded conditions.



Potential alert dimensions include:



\- What type of complaint?

\- What category?

\- Where?

\- When?

\- How many?

\- How unusual is the activity?

\- What notification action should occur?



Potential future alert types:



\### Event alerts



Example:



A new complaint matching a configured condition occurs.



\### Pattern alerts



Example:



A complaint category experiences an unusual spike compared with its

historical baseline.



The system may eventually support both.



\---



\## Current Git State



Main branch baseline:



`aa0da53`



Current working branch:



`feature/alert-logic`



The branch is currently aligned with the remote branch.



There are experimental uncommitted changes related to:



\- SendGrid testing

\- new complaint alerts

\- database alert fields



These changes should be evaluated before being committed as final architecture.



\---



\## Development Environment



Current virtual environment:



`venv`



Current Python interpreter:



Python 3.12



The project previously experimented with Python 3.14 and Python 3.10.



A stray `python310.exe` file was found in the project root and deleted because

it was an untracked Python executable and was not part of the intended project

structure.



\---



\## Current Requirements



The project currently uses:



\- requests

\- pandas

\- Flask

\- SQLAlchemy

\- APScheduler



SendGrid and certifi are now also being used by the email implementation and

should eventually be reflected appropriately in `requirements.txt`.



\---



\## Known Issues / Future Improvements



1\. Finalize alert logic.

2\. Separate alert evaluation from data ingestion.

3\. Decide whether new-complaint alerts, pattern alerts, or both should be

&#x20;  supported.

4\. Prevent duplicate notifications cleanly.

5\. Improve incremental data fetching.

6\. Improve complaint categorization.

7\. Add automated tests.

8\. Improve error handling/retry behavior.

9\. Properly integrate email notifications with the alert engine.

10\. Determine whether a dashboard is useful.

11\. Eventually evaluate whether the system has commercial/product potential.



\---



\## Development Philosophy



This project is being built as a learning project as well as a potentially

useful application.



The goal is not simply to produce working code. Major architectural decisions

should be explained and understood before implementation.



The system should be built incrementally, with working checkpoints and tests.



GitHub should remain the source of truth for the codebase.



`PROJECT\_CONTEXT.md` should be updated whenever major architectural decisions

or project milestones occur.



