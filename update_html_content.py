import re

with open('dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('build.py', 'r', encoding='utf-8') as f:
    py_code = f.read()

# Encode special chars for HTML
py_code_escaped = py_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# Replace the code block
new_html = re.sub(
    r'(<code class="language-python" id="python-code-block">).*?(</code>)', 
    r'\g<1>' + py_code_escaped + r'\g<2>', 
    html, 
    flags=re.DOTALL
)

# Text replacements inside html string
new_html = new_html.replace('No Sklearn - Built From Scratch', 'Powered by XGBoost &amp; Scikit-Learn')
new_html = new_html.replace('🧠 Ensemble Acc:', '🚀 XGBoost Acc:')
new_html = new_html.replace('🤖 Custom Gaussian Naive Bayes Metrics', '🤖 XGBoost Predictive Metrics')
new_html = new_html.replace('Gaussian Naive Bayes model trend', 'XGBoost model trend')
new_html = new_html.replace('Data split: 80% Train | 20% Test', 'Data split: 80% Train | 20% Test') # just checking string exist

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("HTML string replacements and embedded Python code updated successfully.")
