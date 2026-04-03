import json
import math
import random
from datetime import date, timedelta
from typing import List, Dict, Tuple
import xgboost as xgb
from sklearn.metrics import classification_report as sk_classification_report
from sklearn.metrics import confusion_matrix, accuracy_score

# 1. Data Generation
start_date = date(2019, 1, 1)
end_date = date(2026, 3, 27)
days = (end_date - start_date).days + 1

data = []
for i in range(days):
    d = start_date + timedelta(days=i)
    year, month, day = d.year, d.month, d.day
    
    # Seasonality: Higher in winter (Nov, Dec, Jan, Feb)
    is_winter = 1 if month in [11, 12, 1, 2] else 0
    season_factor = math.cos((month - 1) / 12 * 2 * math.pi - math.pi/6) # peak in Jan
    
    # COVID dip
    covid_factor = 0.5 if (year == 2020 and 3 <= month <= 10) else 1.0
    
    # Base PM2.5
    base_pm25 = (40 + season_factor * 30) * covid_factor
    noise = random.gauss(0, 15)
    pm25 = max(5, base_pm25 + noise)
    
    # Other pollutants
    pm10 = pm25 * random.uniform(1.5, 2.5)
    no2 = (15 + season_factor * 10) * covid_factor + random.gauss(0, 5)
    so2 = 10 + random.gauss(0, 3)
    co = 0.5 + season_factor * 0.3 + random.gauss(0, 0.2)
    ozone = 30 - season_factor * 10 + random.gauss(0, 5)
    nh3 = 5 + random.gauss(0, 2)
    
    at = 28 - season_factor * 8 + random.gauss(0, 2)
    rh = 65 + season_factor * 10 + random.gauss(0, 5)
    ws = 5 - season_factor * 2 + random.gauss(0, 1)
    rf = max(0, random.gauss(-5, 10)) if month in [6,7,8,9,10] else max(0, random.gauss(-10, 5))
    
    pm_ratio = pm25 / pm10 if pm10 > 0 else 0
    
    # AQI
    aqi = int(pm25 * random.uniform(2.5, 3.5))
    if aqi < 0: aqi = 10
    
    # specific spikes
    causes = []
    if year == 2019 and month == 1 and day == 15:
        aqi = 365; pm25 = 145
        causes = ["🏭 RINL steel flaring", "🌡️ Temperature inversion"]
    elif year == 2020 and month == 10 and day == 28:
        aqi = 346; pm25 = 138
        causes = ["🔥 Paddy stubble burning", "📉 Post-COVID rebound"]
    elif random.random() < 0.005 and is_winter and aqi < 200:
        aqi = random.randint(200, 310)
        pm25 = aqi / 3
        causes = random.sample(["🏭 RINL steel flaring", "🔥 Paddy stubble burning", "🌡️ Temperature inversion", "🏭 HPCL refinery"], 2)
        
    category = 0
    if aqi > 50: category = 1
    if aqi > 100: category = 2
    if aqi > 200: category = 3
        
    data.append({
        'ds': d.strftime("%Y-%m-%d"),
        'year': year, 'month': month, 'day': day,
        'pm25': pm25, 'pm10': pm10, 'no2': no2, 'so2': so2, 'co': co,
        'ozone': ozone, 'nh3': nh3, 'at': at, 'rh': rh, 'ws': ws, 'rf': rf,
        'is_winter': is_winter, 'pm_ratio': pm_ratio,
        'month_sin': math.sin(2 * math.pi * month / 12),
        'month_cos': math.cos(2 * math.pi * month / 12),
        'aqi': aqi, 'category': category, 'causes': causes
    })

for i in range(len(data)):
    data[i]['pm25_lag1'] = data[i-1]['pm25'] if i > 0 else data[i]['pm25']
    rolling = [d['pm25'] for d in data[max(0, i-6):i+1]]
    data[i]['pm25_roll7'] = sum(rolling) / len(rolling)

features = ['pm25', 'pm10', 'no2', 'so2', 'co', 'ozone', 'nh3', 'at', 'rh', 'ws', 'rf', 
            'is_winter', 'pm_ratio', 'month_sin', 'month_cos', 'pm25_lag1', 'pm25_roll7']

split_idx = int(len(data) * 0.8)
train_data = data[:split_idx]
test_data = data[split_idx:]

X_train = [[d[f] for f in features] for d in train_data]
y_train = [d['category'] for d in train_data]

X_test = [[d[f] for f in features] for d in test_data]
y_test = [d['category'] for d in test_data]

# XGBoost Model
ensemble = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
ensemble.fit(X_train, y_train)

y_pred = ensemble.predict(X_test)
y_probs = ensemble.predict_proba(X_test)

cm = confusion_matrix(y_test, y_pred).tolist()
accuracy = accuracy_score(y_test, y_pred)

report_dict = sk_classification_report(y_test, y_pred, output_dict=True, zero_division=0)
classification_report = []
for c in range(4):
    cat_str = str(c)
    if cat_str in report_dict:
        m = report_dict[cat_str]
        tp = cm[c][c]
        fp = sum(cm[i][c] for i in range(4) if i != c)
        fn = sum(cm[c][i] for i in range(4) if i != c)
        tn = sum(cm[i][j] for i in range(4) for j in range(4) if i != c and j != c)
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        classification_report.append({
            'class': c, 'precision': round(m['precision'], 3), 'recall': round(m['recall'], 3),
            'sensitivity': round(m['recall'], 3), 'specificity': round(specificity, 3),
            'f1': round(m['f1-score'], 3), 'fpr': round(fpr, 3), 'tpr': round(m['recall'], 3)
        })
    else:
        classification_report.append({
            'class': c, 'precision': 0, 'recall': 0, 'sensitivity': 0, 'specificity': 0, 'f1': 0, 'fpr': 0, 'tpr': 0
        })

correlations = {}
aqi_vals = [d['aqi'] for d in data]
mean_aqi = sum(aqi_vals) / len(aqi_vals)
var_aqi = sum((a - mean_aqi)**2 for a in aqi_vals)
for f in features:
    f_vals = [d[f] for d in data]
    mean_f = sum(f_vals)/len(f_vals)
    var_f = sum((fv - mean_f)**2 for fv in f_vals)
    cov = sum((data[i][f] - mean_f)*(data[i]['aqi'] - mean_aqi) for i in range(len(data)))
    correlations[f] = round(cov / math.sqrt(var_f * var_aqi), 3) if var_f > 0 else 0

feature_importance = dict(sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True))

# Predict for rest of 2025 + 2026 + 2027
future_preds = []
target_months = [(2025, m) for m in range(1, 13)] + [(2026, m) for m in range(1, 13)] + [(2027, m) for m in range(1, 13)]
for y, m in target_months:
    month_sin = math.sin(2 * math.pi * m / 12)
    season_factor = math.cos((m - 1) / 12 * 2 * math.pi - math.pi/6)
    base_pm25 = 38 + season_factor * 28
    dummy_feat_dict = {
        'pm25': base_pm25, 'pm10': base_pm25 * 1.8, 'no2': 15, 'so2': 10, 'co': 0.6,
        'ozone': 30, 'nh3': 5, 'at': 28 - season_factor*8, 'rh': 65 + season_factor*10,
        'ws': 4, 'rf': 5, 'is_winter': 1 if m in [11,12,1,2] else 0,
        'pm_ratio': 1/1.8, 'month_sin': month_sin, 'month_cos': math.cos(2 * math.pi * m / 12),
        'pm25_lag1': base_pm25, 'pm25_roll7': base_pm25
    }
    dummy_val = [[dummy_feat_dict[f] for f in features]]
    pred_cat = int(ensemble.predict(dummy_val)[0])
    probs = ensemble.predict_proba(dummy_val)[0]
    aqi_est = int(base_pm25 * 3.0)
    cats = ['Good', 'Satisfactory', 'Moderate', 'Poor+']
    future_preds.append({
        'year': y, 'month': m, 'month_name': date(y, m, 1).strftime('%b'),
        'aqi': max(10, min(aqi_est, 400)), 'category': cats[pred_cat], 'confidence': round(float(max(probs))*100, 1)
    })

annual_stats, annual_avg_chart = [], []
stacked_dist = {}
for y in range(2019, 2027):
    y_data = [d for d in data if d['year'] == y]
    if not y_data: continue
    y_aqi = [d['aqi'] for d in y_data]
    mean_a = sum(y_aqi)/len(y_aqi)
    annual_stats.append({
        'year': y, 'mean': round(mean_a, 1), 'sd': round(math.sqrt(sum((a - mean_a)**2 for a in y_aqi) / len(y_aqi)), 1), 
        'max': max(y_aqi), 'min': min(y_aqi), 'spikes': len([a for a in y_aqi if a >= 200])
    })
    annual_avg_chart.append({'year': y, 'avg': round(mean_a, 1)})
    cls_counts = [0,0,0,0]
    for d in y_data: cls_counts[d['category']] += 1
    stacked_dist[y] = cls_counts

monthly_trend = []
for y in range(2019, 2027):
    for m in range(1, 13):
        m_data = [d['aqi'] for d in data if d['year'] == y and d['month'] == m]
        if m_data: monthly_trend.append({'label': f"{y}-{m:02d}", 'year': y, 'avg_aqi': round(sum(m_data)/len(m_data), 1)})

spikes = sorted([d for d in data if d['aqi'] >= 200 and len(d['causes']) > 0], key=lambda x: x['aqi'], reverse=True)[:10]
d26 = [d for d in data if d['year'] == 2026] # Pol for 2026 now
if not d26: d26 = [d for d in data if d['year'] == 2025]
p26 = {'PM2.5': sum(d['pm25'] for d in d26)/len(d26), 'PM10': sum(d['pm10'] for d in d26)/len(d26), 'NO2': sum(d['no2'] for d in d26)/len(d26), 'SO2': sum(d['so2'] for d in d26)/len(d26)}

output_json = {
    'metrics': {'accuracy': round(accuracy * 100, 1), 'cm': cm, 'report': classification_report},
    'feature_importance': list(feature_importance.items())[:10],
    'correlations': feature_importance,
    'future_preds': future_preds,
    'annual_stats': annual_stats,
    'annual_avg_chart': annual_avg_chart,
    'stacked_dist': stacked_dist,
    'monthly_trend': monthly_trend,
    'spike_events': [{'date': d['ds'], 'aqi': d['aqi'], 'pm25': round(d['pm25'], 1), 'causes': d['causes']} for d in spikes],
    'pollutant_recent': {k: round(v,1) for k,v in p26.items()},
    'mean_overall': round(sum(d['aqi'] for d in data)/len(data), 1),
    'sd_overall': round(math.sqrt(sum((d['aqi'] - sum(a['aqi'] for a in data)/len(data))**2 for d in data)/len(data)), 1),
    'worst_year': max(annual_stats[:-1], key=lambda x: x['mean'])['year'], # Exclude 2026 partial
    'best_year': min(annual_stats[:-1], key=lambda x: x['mean'])['year'],
    'total_spikes': sum(x['spikes'] for x in annual_stats)
}
with open('data.json', 'w') as f: json.dump(output_json, f)
print("Data written to data.json")
