import json
import re

def update_dashboard():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data_str = f.read()
    except FileNotFoundError:
        print("data.json not found. Run build.py first.")
        return

    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            html = f.read()
            
        # Safely replace the ML_DATA object without overwriting user's custom HTML/CSS
        new_html = re.sub(
            r'const ML_DATA = \{.*?\};', 
            lambda m: f'const ML_DATA = {data_str};', 
            html, 
            flags=re.DOTALL
        )
        
        with open('dashboard.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
            
        print("Dashboard cleanly updated with latest ML_DATA while preserving UI!")
    except Exception as e:
        print(f"Error updating dashboard: {e}")

if __name__ == "__main__":
    update_dashboard()
