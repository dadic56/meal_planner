from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import pandas as pd
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///selection.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Charger les données CSV
def charger_donnees(fichier):
    return pd.read_csv(fichier)

df = charger_donnees("PLAT_INGREDIENTS_CORRIGE.csv")

class Selection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plat = db.Column(db.String(200), unique=True, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    plats = sorted(df['Plat'].unique())
    return render_template('index.html', plats=plats)

@app.route('/get_selected_plats', methods=['GET'])
def get_selected_plats():
    selected_plats = [selection.plat for selection in Selection.query.all()]
    return jsonify(selected_plats)

@socketio.on('select_plat')
def handle_select_plat(data):
    selected_plats = set([selection.plat for selection in Selection.query.all()])
    plat = data.get('plat')
    if plat in selected_plats:
        selected_plats.remove(plat)
    else:
        selected_plats.add(plat)
    db.session.query(Selection).delete()
    for plat in selected_plats:
        new_selection = Selection(plat=plat)
        db.session.add(new_selection)
    db.session.commit()
    emit('update_selection', list(selected_plats), broadcast=True)

@socketio.on('generer_liste')
def handle_generer_liste():
    selected_plats = [selection.plat for selection in Selection.query.all()]
    liste_courses = defaultdict(float)

    for plat in selected_plats:
        ingredients = df[df['Plat'] == plat]
        for _, row in ingredients.iterrows():
            ingredient, quantite = row['Ingrédient'], row['Quantité']
            if "au goût" in str(quantite):
                continue

            quantite_split = str(quantite).split()
            if len(quantite_split) == 2:
                valeur, unite = quantite_split
                try:
                    valeur = float(valeur)
                    liste_courses[(ingredient, unite)] += valeur
                except ValueError:
                    pass
            else:
                try:
                    valeur = float(quantite_split[0])
                    liste_courses[(ingredient, 'unités')] += valeur
                except ValueError:
                    pass

    liste_finale = [{"ingredient": k[0], "quantite": v, "unite": k[1]} for k, v in liste_courses.items()]
    emit('liste_courses', liste_finale)

@app.route('/get_ingredients', methods=['GET'])
def get_ingredients():
    plat = request.args.get('plat')
    ingredients = df[df['Plat'] == plat][['Ingrédient', 'Quantité']].to_dict('records')
    return jsonify(ingredients)

@app.route('/save_ingredients', methods=['POST'])
def save_ingredients():
    data = request.json
    plat = data['plat']
    ingredients = data['ingredients']
    
    global df
    df = df[df['Plat'] != plat]  # Supprimez les anciens ingrédients du plat
    for ingredient in ingredients:
        df = df.append({'Plat': plat, 'Ingrédient': ingredient['name'], 'Quantité': ingredient['quantity']}, ignore_index=True)
    df.to_csv("PLAT_INGREDIENTS_CORRIGE.csv", index=False)
    return '', 204

@app.route('/delete_plat', methods=['DELETE'])
def delete_plat():
    plat = request.args.get('plat')
    
    global df
    df = df[df['Plat'] != plat]  # Supprimez le plat du DataFrame
    df.to_csv("PLAT_INGREDIENTS_CORRIGE.csv", index=False)
    
    # Supprimez le plat de la sélection s'il est sélectionné
    Selection.query.filter_by(plat=plat).delete()
    db.session.commit()
    
    return '', 204

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
