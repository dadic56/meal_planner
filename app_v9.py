from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import pandas as pd
from collections import defaultdict
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///selection.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Charger les données CSV une seule fois
df = pd.read_csv("PLAT_INGREDIENTS_CORRIGE.csv")

class Selection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plat = db.Column(db.String(200), unique=True, nullable=False)

with app.app_context():
    db.drop_all()
    db.create_all()

@app.route('/')
def index():
    plats = sorted(df['Plat'].unique())
    return render_template('index.html', plats=plats)

@app.route('/get_selected_plats', methods=['GET'])
def get_selected_plats():
    selected_plats = [selection.plat for selection in Selection.query.all()]
    return jsonify(selected_plats)

@app.route('/get_ingredients', methods=['GET'])
def get_ingredients():
    plat = request.args.get('plat')
    if plat:
        ingredients = df[df['Plat'] == plat][['Ingrédient', 'Quantité', 'Unité']].to_dict(orient='records')
        return jsonify(ingredients)
    return jsonify([])

@socketio.on('select_plat')
def handle_select_plat(data):
    print("select_plat event received with data:", data)
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

@socketio.on('reset_selection')
def handle_reset_selection():
    print("reset_selection event received")
    db.session.query(Selection).delete()
    db.session.commit()
    emit('update_selection', [], broadcast=True)

@socketio.on('generer_liste')
def handle_generer_liste(data):
    print("generer_liste event received with data:", data)
    selected_plats = data
    liste_courses = defaultdict(float)

    for plat in selected_plats:
        ingredients = df[df['Plat'] == plat]
        for _, row in ingredients.iterrows():
            ingredient, quantite, unite = row['Ingrédient'], row['Quantité'], row['Unité']
            if not quantite or not unite or "au goût" in str(unite):
                continue

            try:
                valeur = float(quantite)
                if unite in ['g', 'kg']:
                    if unite == 'g':
                        valeur /= 1000  # Convertir en kg
                    liste_courses[(ingredient, 'kg')] += valeur
                elif unite in ['ml', 'l']:
                    if unite == 'l':
                        valeur *= 100  # Convertir en cl
                    liste_courses[(ingredient, 'cl')] += valeur
                else:
                    liste_courses[(ingredient, unite)] += valeur
            except ValueError:
                pass

    liste_finale = [{"ingredient": k[0], "quantite": v, "unite": k[1]} for k, v in liste_courses.items()]
    liste_finale.sort(key=lambda x: x['ingredient'])
    emit('liste_courses', liste_finale)

@socketio.on('ajouter_plat')
def handle_ajouter_plat(data):
    print("ajouter_plat event received with data:", data)
    plat = data.get('plat')
    ingredients = data.get('ingredients')
    if plat and ingredients:
        for ingredient in ingredients:
            df.loc[len(df)] = [plat, ingredient['ingredient'], ingredient['quantite'], ingredient['unite']]
        df.to_csv("PLAT_INGREDIENTS_CORRIGE.csv", index=False)
        new_selection = Selection(plat=plat)
        db.session.add(new_selection)
        db.session.commit()
        emit('plat_ajoute', plat, broadcast=True)

@socketio.on('supprimer_plat')
def handle_supprimer_plat(data):
    print("supprimer_plat event received with data:", data)
    plat = data.get('plat')
    if plat:
        df.drop(df[df['Plat'] == plat].index, inplace=True)
        df.to_csv("PLAT_INGREDIENTS_CORRIGE.csv", index=False)
        db.session.query(Selection).filter_by(plat=plat).delete()
        db.session.commit()
        emit('plat_supprime', plat, broadcast=True)

@socketio.on('modifier_plat')
def handle_modifier_plat(data):
    print("modifier_plat event received with data:", data)
    plat = data.get('plat')
    nouveau_nom = data.get('nouveauNom')
    ingredients = data.get('ingredients')
    if plat and nouveau_nom and ingredients:
        # Supprimer les anciennes entrées pour le plat
        df.drop(df[df['Plat'] == plat].index, inplace=True)
        # Ajouter les nouvelles entrées pour le plat
        for ingredient in ingredients:
            df.loc[len(df)] = [nouveau_nom, ingredient['ingredient'], ingredient['quantite'], ingredient['unite']]
        df.to_csv("PLAT_INGREDIENTS_CORRIGE_v9.csv", index=False)
        # Mettre à jour la base de données
        selection = Selection.query.filter_by(plat=plat).first()
        if selection:
            selection.plat = nouveau_nom
            db.session.commit()
        emit('plat_modifie', nouveau_nom, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)