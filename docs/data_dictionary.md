# Data Dictionary: Metro Interstate Traffic Volume Dataset

## Overview
The dataset contains hourly traffic volume reports for westbound Interstate 94 (I-94) between Minneapolis and St. Paul, Minnesota, spanning October 2012 through September 2018. Meteorological observations and holiday indicators from the Minnesota Department of Transportation (MnDOT) and the National Weather Service are joined at hourly intervals.

---

## 1. Raw Dataset Fields

| Column Name | Data Type | Physical Units | Valid Range / Categories | Description | Handling in Data Pipeline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `holiday` | String | Categorical | `None`, or US/State holiday name | Designation of US national or Minnesota state holiday. Note: literal string `'None'` represents normal non-holiday days. | Encoded via `StringIndexer` and `OneHotEncoder` for modeling. |
| `temp` | Double | Kelvin (K) | 240.0 K – 315.0 K (typical) | Hourly average ambient temperature. | Sensor failure 0.0 K (10 instances) set to `NULL`; imputed with median during ML training. |
| `rain_1h` | Double | Millimeters (mm) | 0.0 mm – 100.0 mm | Amount in mm of rain that occurred in the hour. | Gauge glitch > 100 mm (1 instance at 9831.3 mm) set to `NULL`; valid zeros preserved. |
| `snow_1h` | Double | Millimeters (mm) | 0.0 mm – 1.0 mm | Amount in mm of snow that occurred in the hour. | 48,124 valid zero observations preserved; 63 positive values preserved. |
| `clouds_all` | Integer | Percentage (%) | 0% – 100% | Percentage of cloud cover observed. | Verified within valid range $[0, 100]$; preserved as numeric feature. |
| `weather_main` | String | Categorical | 11 categories: `Clear`, `Clouds`, `Rain`, `Drizzle`, `Snow`, `Mist`, `Haze`, `Fog`, `Thunderstorm`, `Squall`, `Smoke` | Short textual summary of prevailing weather conditions. | Encoded via `StringIndexer` and `OneHotEncoder`. |
| `weather_description` | String | Categorical | Granular descriptions (e.g., `sky is clear`, `light rain`, `proximity thunderstorm`) | Detailed description of weather events. | Used in granular EDA; preserved in clean parquet dataset. |
| `date_time` | Timestamp | `YYYY-MM-DD HH:MM:SS` | 2012-10-02 09:00:00 to 2018-09-30 23:00:00 | Hourly observation timestamp in US Central Time (CST/CDT). | Parsed as Spark SQL `timestamp`; used for chronological ordering and temporal feature extraction. |
| `traffic_volume` | Integer | Vehicles / Hour (vph) | 0 – 7,280 vph | Target Variable: Total hourly westbound traffic volume passing the sensor station. | Preserved as target label. Valid 0 vph (2 records) preserved. |

---

## 2. Engineered Features

| Feature Name | Derived From | Data Type | Formula / Logic | Explanation & Operational Notes |
| :--- | :--- | :--- | :--- | :--- |
| `date` | `date_time` | Date | `to_date(date_time)` | Calendar date (`YYYY-MM-DD`) for daily aggregations. |
| `hour` | `date_time` | Integer | `hour(date_time)` | Hour of the day (`0` to `23`). Critical feature for capturing morning (7–8 AM) and evening (4–5 PM) rush hour commute peaks. |
| `day_of_week` | `date_time` | Integer | `dayofweek(date_time)` | Day index. **Important Note:** Spark SQL `dayofweek()` standard designates `Sunday = 1, Monday = 2, ..., Saturday = 7`. |
| `month` | `date_time` | Integer | `month(date_time)` | Month index (`1` to `12`). Captures seasonal variations (summer leisure travel vs. winter blizzard reductions). |
| `is_weekend` | `day_of_week` | Integer | `WHEN day_of_week IN (1, 7) THEN 1 ELSE 0` | Binary indicator for weekend days (`1` = Saturday/Sunday, `0` = Monday through Friday). Separates bimodal commute curves from unimodal leisure plateaus. |

---

## 3. Critical Target Clarification
- **Vehicle Count vs. Speed/Delay**: `traffic_volume` quantifies the number of vehicles passing the sensor point in one hour. It is **not** a direct measurement of vehicle speed (mph) or travel delay (minutes).
- In conditions of complete gridlock, traffic volume can paradoxically decrease because vehicles are stationary.
