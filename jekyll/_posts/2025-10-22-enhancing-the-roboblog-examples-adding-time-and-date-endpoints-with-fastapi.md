---
layout: post
title: "Enhancing the Roboblog Examples: Adding Time and Date Endpoints with FastAPI"
date: 2025-10-22 12:53:11 +0000
categories: development updates
author: m42839360-cell
---

In the fast-paced world of web development, providing users with relevant and real-time data is essential. The latest updates to the `roboblog-examples` repository demonstrate just that by introducing two new endpoints: one for fetching the current date and another for retrieving the current time. These enhancements were made using FastAPI, a modern web framework for building APIs with Python. This blog post delves into the recent changes, their impact on the application, and how they empower users with dynamic information.

## New Date and Time Endpoints

### Overview of Changes

In total, seven commits were made over a two-day period, resulting in significant functionality improvements. The main focus was the addition of two pivotal endpoints:

1. **GET /date**: Returns the current date along with time and timestamp.
2. **GET /time**: Returns the current time in both 12-hour and 24-hour formats.

### Implementation Details

#### Adding the Date Endpoint

The date endpoint was implemented first, allowing users to obtain the current date and time. The following code snippet illustrates the implementation in `main.py`:

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/date")
def get_date():
    now = datetime.now()
    return {
        "date": now.date().isoformat(),
        "time": now.time().isoformat(),
        "datetime": now.isoformat(),
        "timestamp": now.timestamp()
    }
```

This code utilizes the `datetime` module, creating a simple API that responds with the current date and time in various formats. The endpoint responds with a JSON object encapsulating the date, time, and timestamp, enhancing the application's utility for users needing real-time information.

#### Adding the Time Endpoint

Following the date endpoint, the time endpoint was added. This endpoint provides the time in both 12-hour and 24-hour formats, as demonstrated in the following code:

```python
@app.get("/time")
def get_time():
    now = datetime.now()
    return {
        "time_24h": now.strftime("%H:%M:%S"),
        "time_12h": now.strftime("%I:%M:%S %p"),
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second
    }
```

Here, the `strftime` method is employed to format the current time appropriately, catering to different user preferences.

### Documentation Updates

Both endpoints were accompanied by updates to the `README.md` file, ensuring that users are informed about how to utilize the new features. This practice is crucial for onboarding new users and facilitating ease of access to the API's capabilities.

## Statistics of the Changes

The recent updates to the repository resulted in the modification of several files, with the following statistics reflecting the changes made:

- **Total Commits**: 7
- **Files Changed**: 4
  - `README.md`: Modified to include new endpoint documentation
  - `main.py`: Core logic for new endpoints added
  - `requirements.txt`: Added to manage dependencies
- **Lines Added**: 80
- **Lines Removed**: 1

These statistics highlight the active development and refinement of the `roboblog-examples` project, showcasing the commitment to enhancing the user experience.

## Conclusion and Next Steps

The inclusion of date and time endpoints enriches the `roboblog-examples` repository, providing users with critical real-time information. As we move forward, potential next steps could include:

- **Error Handling**: Implementing robust error handling to manage potential issues with time retrieval.
- **Testing**: Writing unit tests to ensure the reliability of the endpoints.
- **Further Enhancements**: Considering additional features, such as time zone support or historical date information.

With these improvements, the `roboblog-examples` project not only demonstrates the power of FastAPI but also sets the stage for future enhancements that can further benefit users looking for dynamic and real-time data.