# 🌱 Food Waste Reduction and Climate Impact Analyzer

An intelligent, data-driven platform for forecasting food demand, optimizing food preparation, estimating food waste, understanding its potential environmental impact, and facilitating surplus-food redistribution through NGO coordination.

---

## 📌 Project Overview

Food waste is a significant sustainability challenge, particularly in the food service sector. Preparing more food than necessary can result in avoidable waste, resource loss, and environmental consequences.

The **Food Waste Reduction and Climate Impact Analyzer** is a Python-based application designed to help restaurants and food service establishments make informed food preparation decisions using demand forecasting and data-driven waste analysis.

The platform integrates machine learning, contextual demand analysis, serving estimation, climate impact calculations, waste-management recommendations, and NGO-based surplus-food coordination into a unified application.

## ✨ Key Features

### 1. Restaurant and Menu Management

- Includes 12 sample restaurants, cafés, and canteens located in Chennai.
- Each establishment has a unique ID, location, contact information, and a distinct menu containing 7–10 items.
- Supports registration of new restaurants.
- Allows newly registered restaurants to save their menu information.

### 2. Historical Demand Generation

- Generates two years of synthetic historical demand data.
- Incorporates contextual factors such as:
  - Day of the week.
  - Weekends and holidays.
  - Promotional activities.
  - Temperature and rainfall.
  - Rainy-day and hot-day indicators.
  - Historical demand lags.
- Uses item-specific popularity profiles and restaurant-level demand multipliers.

### 3. Machine Learning-Based Demand Forecasting

The application trains and evaluates four machine learning algorithms:

| Algorithm | Purpose |
|---|---|
| Linear Regression | Baseline demand prediction |
| Decision Tree | Non-linear demand modelling |
| Random Forest | Ensemble-based demand prediction |
| XGBoost | Gradient-boosted demand prediction |

**Model selection methodology:**

- Uses chronological validation MAE (Mean Absolute Error) to select the best-performing model.
- Keeps the later chronological test set separate from model selection.
- Avoids using test-set performance to select the winning model.

### 4. Demand and Food Preparation Estimation

- Predicts demand for a selected restaurant and menu item.
- Estimates the recommended food preparation quantity.
- Converts predicted food quantities in kilograms into approximate servings.
- Uses item-specific portion-size assumptions.
- Displays an approximate prediction interval.

**Cold-start handling for new restaurants:**

Newly registered restaurants initially have no historical sales records. Therefore, their initial demand estimates use a labelled transfer estimate based on matching existing restaurants, menu items, and categories.

Once sufficient sales history accumulates, the new restaurant can become part of the historical training dataset.

### 5. Food Waste and Climate Impact Analysis

- Estimates expected food waste.
- Calculates an illustrative climate and disposal burden.
- Helps users understand the potential environmental implications of food waste.
- Supports informed food preparation and waste-management decisions.

**Note:** Climate impact values are illustrative estimates, not measured emissions or verified atmospheric emission reductions.

### 6. Waste Management Recommendations

- Provides category-based waste-management guidance.
- Supports responsible handling of surplus food and organic waste.
- Connects waste-management decisions with sustainability practices.

### 7. NGO-Based Food Redistribution

The platform includes an NGO coordination workflow designed to facilitate surplus-food redistribution.

**Key capabilities:**

- Location-based matching between restaurants and sample NGOs.
- NGO notifications through SMTP email integration.
- Recording of acceptance and rejection responses.
- Sequential NGO request handling.
- 30-minute response timeout logic.
- Simulated acceptance and rejection controls when SMTP is not configured.

**NGO request workflow:**

1. A restaurant initiates a surplus-food request.
2. The system identifies location-matched NGOs.
3. The first NGO in the configured order receives the request.
4. The NGO's acceptance or rejection response is recorded.
5. If an NGO declines or the 30-minute response timeout expires, the request advances to the next matched NGO.

---

## 🏗️ System Workflow

```text
Restaurant and Menu Information
             |
             v
Synthetic Historical Demand Data
             |
             v
Data Preprocessing and Feature Engineering
             |
             v
Machine Learning Model Training
             |
             v
Chronological Validation and Model Selection
             |
             v
Restaurant and Item-Level Demand Prediction
             |
             v
Food Preparation and Serving Estimation
             |
             v
Expected Food Waste Estimation
             |
             v
Illustrative Climate Impact Analysis
             |
             v
Waste Management Recommendations
             |
             v
Location-Based NGO Matching
             |
             v
Email Notification and Response Handling
```

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn, XGBoost |
| Model Evaluation | Mean Absolute Error (MAE) |
| Visualization | Streamlit visualizations |
| Email Integration | SMTP |
| Testing | Pytest |
| Environment Management | Python Virtual Environment |

## 📂 Project Structure

```text
FoodWasteClimateImpactAnalyzer/
│
├── dashboard/
│   └── app.py
│
├── src/
│   ├── climate.py
│   └── ...
│
├── ngo/
│   ├── ngos.csv
│   └── requests.json
│
├── assets/
│   └── demo/
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
├── train_models.py
└── README.md
```

*The structure above highlights the main project components. Additional source files and modules are included in the repository.*

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.11 (recommended)
- Git
- pip
- Windows, Linux, or macOS

### 1. Clone the Repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

Navigate into the cloned project directory:

```bash
cd <YOUR-REPOSITORY-FOLDER>
```

### 2. Create a Virtual Environment

For Windows CMD:

```cmd
py -3.11 -m venv .venv
```

### 3. Activate the Environment

```cmd
.venv\Scripts\activate
```

If PowerShell activation is blocked, you can use the virtual environment's Python executable directly.

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Train the Machine Learning Models

```bash
python train_models.py
```

### 6. Run the Tests

```bash
python -m pytest -q
```

### 7. Launch the Streamlit Dashboard

```bash
python -m streamlit run dashboard/app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## 📧 SMTP Email Configuration

The NGO notification workflow supports SMTP-based email communication.

To enable real email notifications, configure the following environment variables:

| Variable | Description |
|---|---|
| `SMTP_HOST` | SMTP server hostname |
| `SMTP_PORT` | SMTP server port, usually 587 |
| `SMTP_USER` | Email account username |
| `SMTP_PASSWORD` | Email account password or app password |
| `SMTP_FROM` | Sender email address |
| `RESPONSE_BASE_URL` | Publicly reachable dashboard or response endpoint |

### Gmail SMTP Setup

1. Copy `.env.example` to `.env`.
2. Create a dedicated Gmail account for the demonstration.
3. Enable Google 2-Step Verification.
4. Generate a Google App Password.
5. Configure the App Password as `SMTP_PASSWORD`.
6. Set `SMTP_FROM` to the corresponding Gmail address, unless a verified sender configuration is used.
7. Launch the Streamlit application and open the NGO Matching module.
8. Use the SMTP connection/login test provided in the application.

**Important security considerations:**

- Never upload `.env` files or real SMTP credentials to GitHub.
- Ensure `.env` is included in `.gitignore`.
- A publicly reachable HTTPS `RESPONSE_BASE_URL` is required for real NGOs to respond through external links.
- `http://localhost:8501` is suitable only for local testing.
- Without SMTP credentials, simulated acceptance and rejection controls allow the workflow to be demonstrated without sending real emails.

## 🍽️ Portion-Size Assumptions

The conversion from kilograms to servings uses item-specific reference assumptions.

These values are approximate and should not be interpreted as official restaurant serving standards. Actual portion sizes can vary considerably depending on restaurants, preparation methods, and serving styles.

Restaurants should replace the default assumptions with their own measured portion sizes to improve estimation accuracy.

## 📊 Research and Evaluation Transparency

This project uses a **controlled synthetic dataset** representing sample restaurant demand patterns.

The following limitations are important when interpreting its results:

- The generated dataset is not actual sales data collected from operating restaurants.
- Model evaluation metrics apply to the generated benchmark and should not be presented as proven real-world restaurant forecasting performance.
- Chronological validation is used for model selection, while the later test set remains separate.
- New restaurants use labelled cold-start transfer estimates until sufficient historical data becomes available.
- Portion-size conversions rely on explicit assumptions.
- The climate disposal factor implemented in `src/climate.py` is an illustrative placeholder. It must be replaced with a documented, locally applicable factor before making publication-quality environmental claims.
- Prediction intervals and preparation recommendations are prototype decision-support features. Their practical value requires further evaluation.

## 🌍 Sustainability and Food Safety Considerations

The platform is designed around responsible food preparation, waste reduction, and surplus-food redistribution.

Important considerations include:

- Surplus food must be handled and stored safely.
- Food that is unsafe or spoiled must not be donated.
- Appropriate handling, storage, transportation, and record-keeping practices are necessary.
- Food redistribution should take place before food becomes unsafe or expires.
- Composting and anaerobic digestion are possible management pathways for suitable organic waste.

The application's climate estimates are illustrative and do not establish actual greenhouse-gas emission reductions.

## 🚀 Future Research and Development

Potential areas for further research and development include:

- Validation using real restaurant sales and food-waste records.
- Improved demand forecasting using real-world contextual data.
- Evaluation of preparation decisions against food shortage and waste trade-offs.
- Calibration of item-specific portion-size assumptions.
- Replacement of illustrative climate factors with locally validated environmental factors.
- Evaluation of NGO response efficiency and successful redistribution outcomes.

These are potential future directions and should not be interpreted as already implemented capabilities.

---

**Built to explore how machine learning and data-driven decision support can contribute to food waste reduction and more sustainable food management.**
