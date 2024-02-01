from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sqlalchemy import func
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'mysql+mysqldb://nations:nations!@localhost/nations')
db = SQLAlchemy(app)

class Titanic_RT(db.Model):
    __tablename__ = 'Titanic_RT'
    PassengerId = db.Column(db.BigInteger, primary_key=True)
    Survived = db.Column(db.BigInteger)
    Pclass = db.Column(db.BigInteger)
    Name = db.Column(db.String(1024))
    Sex = db.Column(db.String(1024))
    Age = db.Column(db.String(1024))
    SibSp = db.Column(db.BigInteger)
    Parch = db.Column(db.BigInteger)
    Ticket = db.Column(db.String(1024))
    Fare = db.Column(db.String(1024))
    Cabin = db.Column(db.String(1024))
    Embarked = db.Column(db.String(1024))

app.secret_key = os.environ.get('SECRET_KEY', b'_5#y2L"F4Q8z\n\xecl/')

html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Titanic Info</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
  </head>
  <body>
    <a href="/">Home</a><br>
    <script>document.body.style.backgroundImage = "url('https://cdn.britannica.com/79/4679-050-BC127236/Titanic.jpg')"</script>
    <a href="/SurvPassClass">Survived Passengers By Class</a><br><br><br>
    {{ content | safe }}
  </body>
</html>
"""

def create_stacked_bar_chart(categories, bottom_counts, top_counts, title, xlabel, ylabel, xtick_labels=None, legend_labels=('Bottom', 'Top')):
    plt.figure(figsize=(10, 6))
    width = 0.5
    plt.bar(categories, bottom_counts, width, label=legend_labels[0])
    plt.bar(categories, top_counts, width, bottom=bottom_counts, label=legend_labels[1])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(categories, xtick_labels if xtick_labels else categories)
    plt.grid(True)
    plt.legend()
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f'<img src="data:image/png;base64,{plot_url}">'

@app.route('/')
def index():
    return render_template_string(html, content='')

@app.route('/SurvPassClass')
def SPC():
    data = db.session.query(Titanic_RT.Pclass, Titanic_RT.Survived, func.count(Titanic_RT.PassengerId)).group_by(Titanic_RT.Pclass, Titanic_RT.Survived).all()
    class_data = {1: [0, 0], 2: [0, 0], 3: [0, 0]}
    for pclass, survived, count in data:
        class_data[pclass][survived] += count
    categories = sorted(class_data.keys())
    not_survived_counts = [class_data[category][0] for category in categories]
    survived_counts = [class_data[category][1] for category in categories]
    plot = create_stacked_bar_chart(categories, not_survived_counts, survived_counts, 'Passengers By Class and Survival', 'Class', 'Number of Passengers', xtick_labels=['1st Class', '2nd Class', '3rd Class'], legend_labels=('Not Survived', 'Survived'))
    return render_template_string(html, content=plot)

if __name__ == "__main__":
    app.run('0.0.0.0', port=4242, debug=True)

