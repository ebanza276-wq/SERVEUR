from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey,or_
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

import psutil
import os
import time

# Temps de démarrage du serveur
start_time = time.time()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_BINDS'] = {
    'admin': 'sqlite:///admin.db',
    'superadmin': 'sqlite:///superadmin.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Clé secrète JWT (à remplacer par une clé longue et aléatoire)
app.config["JWT_SECRET_KEY"] = "Votre_Cle_Secrete_Tres_Longue"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
db = SQLAlchemy(app)
jwt = JWTManager(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# MODELS
# =========================
class Admin(db.Model):
    __bind_key__ = "admin"

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))

class SuperAdmin(db.Model):
    __bind_key__ = "superadmin"

    __tablename__ = "superadmins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    numero = db.Column(db.String(100), nullable=False)
    my_annonces = db.relationship("My_Annonces",backref="user",lazy=True)
    favories = db.relationship("Favories",backref="user",lazy=True)
class Annonce(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    prix = db.Column(db.String(100), nullable=False)
    titre = db.Column(db.String(100), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    numero = db.Column(db.String(100), nullable=False)
    categories = db.Column(db.String(100), nullable=False)
class My_Annonces(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    prix = db.Column(db.String(100), nullable=False)
    titre = db.Column(db.String(100), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    numero = db.Column(db.String(100), nullable=False)
    categories = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
class Favories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annonce_id = db.Column(db.Integer, db.ForeignKey("annonce.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    prix = db.Column(db.String(100), nullable=False)
    titre = db.Column(db.String(100), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    numero = db.Column(db.String(100), nullable=False)
    categories = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
admin=[
    {
        "username":"Alice Martin",
        "password": "123",
    },
    ]
utilisateur = [
    {
        "nom": "Alice Martin",
        "password": "123",
        "email": "alice@gmail.com",
        "numero": "+233831734567"
    },
    {
        "nom": "Bob",
        "password": "123",
        "email": "bob@gmail.com",
        "numero": "+243831234567"
    },
    {
        "nom": "Elie",
        "password": "1234",
        "email": "elie@gmail.com",
        "numero": "+243831234567",
    }
]
annonces_data = [
        {"id": "a1", "name": "Marc", "image": "https://picsum.photos/500/300?1", "prix": "250 €", "titre": "Canapé 3 places", "ville": "Paris, 75011", "details": "Très bon état, peu utilisé.", "categories": "immobilier", "numero": "+243831234567"},
        {"id": "a2", "name": "Micheal", "image": "https://picsum.photos/500/300?2", "prix": "8 500 €", "titre": "Peugeot 208 2019", "ville": "Lyon, 69003", "details": "45 000 km, révision faite.", "categories": "voiture", "numero": "+243831234599"},
        {"id": "a3", "name": "Paul", "image": "https://picsum.photos/500/300?3", "prix": "320 €", "titre": "iPhone 11 64Go", "ville": "Bordeaux, 33000", "details": "Bon état général, chargeur inclus.", "categories": "electronique", "numero": "+233831734567"},
        {"id": "a4", "name": "Marcus", "image": "https://picsum.photos/203/203", "prix": "900 €", "titre": "iPhone 15", "ville": "Bordeaux", "details": "Comme neuf, boîte d'origine.", "categories": "electronique", "numero": "+243831234567"},
        {"id": "a5", "name": "Emmanuel", "image": "https://picsum.photos/500/300?4", "prix": "120 €", "titre": "Table en bois", "ville": "Nantes, 44000", "details": "Table massive, quelques traces d'usage.", "categories": "maison", "numero": "+243831234567"},
        {"id": "a6", "name": "Simpson", "image": "https://picsum.photos/500/300?6", "prix": "120 €", "titre": "Chaises assorties", "ville": "Nantes, 44000", "details": "Lot de 4 chaises en bon état.", "categories": "maison", "numero": "+223831234967"},
    ]
my_annonces = [
    {
        "name": "Elie",
        "image": "https://picsum.photos/500/300?1",
        "titre": "Téléphone",
        "prix": "100",
        "ville": "Paris, 75011",
        "details": "Très bon état, peu utilisé.",
        "categories": "electronique",
        "numero": "+243831234567",
        "user_id": 3
    },
    {
        "name": "Elie",
        "image": "https://picsum.photos/500/300?12",
        "titre": "Ordinateur",
        "prix": "500",
        "ville": "Paris, 75011",
        "details": "Très bon état, peu utilisé.",
        "categories": "electronique",
        "numero": "+243831234567",
        "user_id": 3
    }
]
favories = [
    {
        "annonce_id": 1,
        "name": "Elie",
        "image": "https://picsum.photos/500/300?30",
        "titre": "Téléphone",
        "prix": "100",
        "ville": "Paris, 75011",
        "details": "Très bon état, peu utilisé.",
        "categories": "electronique",
        "numero": "+243831234567",
        "user_id": 3
    },
    {
        "annonce_id": 2,
        "name": "Elie",
        "image": "https://picsum.photos/500/300?32",
        "titre": "Ordinateur",
        "prix": "500",
        "ville": "Paris, 75011",
        "details": "Très bon état, peu utilisé.",
        "categories": "electronique",
        "numero": "+243831234567",
        "user_id": 3
    },
    {
        "annonce_id": 3,
        "name": "Elie",
        "image": "https://picsum.photos/500/300?32",
        "titre": "Ordinateur",
        "prix": "500",
        "ville": "Paris, 75011",
        "details": "Très bon état, peu utilisé.",
        "categories": "electronique",
        "numero": "+243831234567",
        "user_id": 3
    }
]
def seed_admin():
    for users in admin:

        new_pub = Admin(
            username=users["username"],
            password=generate_password_hash(users["password"]),
        )

        db.session.add(new_pub)
        db.session.flush()
    db.session.commit()
def seed_user():
    for users in utilisateur:

        new_pub = User(
            nom=users["nom"],
            password=generate_password_hash(users["password"]),
            email=users["email"],
            numero=users["numero"],
        )

        db.session.add(new_pub)
        db.session.flush()
    db.session.commit()
def seed_annonce():
    for annonce in annonces_data:
        new_pub = Annonce(
            name=annonce["name"],
            image_url=annonce["image"],   # Correction ici
            prix=annonce["prix"],
            titre=annonce["titre"],
            ville=annonce["ville"],
            details=annonce["details"],
            numero=annonce["numero"],
            categories=annonce["categories"]
        )

        db.session.add(new_pub)

    db.session.commit()
def seed_my_annonce():
    for annonce in my_annonces:
        new_pub = My_Annonces(
            name=annonce["name"],
            image_url=annonce["image"],
            prix=annonce["prix"],
            titre=annonce["titre"],
            ville=annonce["ville"],
            details=annonce["details"],
            numero=annonce["numero"],
            categories=annonce["categories"],
            user_id=annonce["user_id"]
        )

        db.session.add(new_pub)

    db.session.commit()
def seed_favories():
    for annonce in favories:
        new_pub = Favories(
            annonce_id=annonce["annonce_id"],
            name=annonce["name"],
            image_url=annonce["image"],
            prix=annonce["prix"],
            titre=annonce["titre"],
            ville=annonce["ville"],
            details=annonce["details"],
            numero=annonce["numero"],
            categories=annonce["categories"],
            user_id=annonce["user_id"]
        )

        db.session.add(new_pub)

    db.session.commit()
with app.app_context():
    db.create_all()

    if Admin.query.first() is None:
            seed_admin()

    if User.query.first() is None:
        seed_user()

    if Annonce.query.first() is None:
        seed_annonce()
    if My_Annonces.query.first() is None:
        seed_my_annonce()
    if Favories.query.first() is None:
        seed_favories()

@app.route('/login', methods=['POST'])
def login_http():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    access_token = create_access_token(identity=str(user.id))
    #print(access_token)
    if user and check_password_hash(user.password, password):
        return jsonify({
            "status": "success",
            "token": access_token,
            "user": {
                "id": user.id,
                "nom": user.nom,
                "numero": user.numero,
                "email": user.email,
                "password": user.password  # ⚠️ Not recommended
            }
        }), 200
    return jsonify({"status": "error", "message": "Identifiants incorrects"}), 401

@app.route('/admin/login', methods=['POST'])
def login_admin():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = Admin.query.filter_by(username=username).first()
    access_token = create_access_token(identity=str(user.id))
    if user and check_password_hash(user.password, password):
        return jsonify({
            "status": "success",
            "token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "password": user.password  # ⚠️ Not recommended
            }
        }), 200
    

    return jsonify({"status": "error", "message": "Identifiants incorrects"}), 401

@socketio.on('register')
def register(data):
    username = data['username']
    password = data['password']
    email= data['email']

    if User.query.filter_by(username=username,email=email).first():
        emit('register_response', {'status': 'exists'})
    else:
        new_user=User(username=username,password=generate_password_hash(password),email=email)
        db.session.add(new_user)
        db.session.commit()
        emit('register_response', {'status': 'success'})

@app.route('/annonces_data/', methods=['GET'])
def get_annonces():

    annonces = Annonce.query.all()

    result = []

    for p in annonces:
        result.append({
            "id": p.id,
            "name": p.name,
            "image": p.image_url,
            "prix": p.prix,
            "titre": p.titre,
            "ville": p.ville,
            "details": p.details,
            "numero": p.numero,
            "categories": p.categories
        })

    return jsonify(result)

@app.route('/my_annonces/<int:user_id>', methods=['GET'])
@jwt_required()
def get_my_annonces(user_id):
    #user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "Utilisateur introuvable"
        }), 404

    annonces = My_Annonces.query.filter_by(user_id=user_id).all()

    result = []

    for p in annonces:
        result.append({
            "id": p.id,
            "name": p.name,
            "image": p.image_url,
            "prix": p.prix,
            "titre": p.titre,
            "ville": p.ville,
            "details": p.details,
            "numero": p.numero,
            "categories": p.categories,
            "user_id": p.user_id
        })

    return jsonify(result), 200

@app.route('/my_annonces/count/<int:user_id>', methods=['GET'])
def count_my_annonces(user_id):
    total = My_Annonces.query.filter_by(user_id=user_id).count()

    return jsonify({
        "user_id": user_id,
        "count": total
    }), 200

@app.route('/favories/<int:user_id>', methods=['GET'])
def get_favories(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "Utilisateur introuvable"
        }), 404

    annonces = Favories.query.filter_by(user_id=user_id).all()

    result = []

    for p in annonces:
        result.append({
            "id": p.id,
            "name": p.name,
            "image": p.image_url,
            "prix": p.prix,
            "titre": p.titre,
            "ville": p.ville,
            "details": p.details,
            "numero": p.numero,
            "categories": p.categories,
            "user_id": p.user_id
        })

    return jsonify(result), 200

@app.route("/favories/<int:user_id>/<int:annonce_id>", methods=["POST"])
def ajouter_favori(user_id,annonce_id):
    existant = Favories.query.filter_by(user_id=user_id,annonce_id=annonce_id).first()
    if existant:
        return jsonify({"ok": True, "message": "Déjà en favori"}), 200
    annonce = Annonce.query.get(annonce_id)

    favori = Favories(
        annonce_id=annonce.id,
        name=annonce.name,
        image_url=annonce.image_url,
        prix=annonce.prix,
        titre=annonce.titre,
        ville=annonce.ville,
        details=annonce.details,
        numero=annonce.numero,
        categories=annonce.categories,
        user_id=user_id,
    )

    db.session.add(favori)
    db.session.commit()

    return jsonify({"message": "favories enregistré"})

@app.route("/favories/<int:user_id>/<int:annonce_id>", methods=["DELETE"])
def retirer_favori(user_id,annonce_id):
    favori = Favories.query.filter_by(user_id=user_id,annonce_id=annonce_id).first()

    if not favori:
        return jsonify({
            "success": False,
            "message": "Favori introuvable"
        }), 404

    db.session.delete(favori)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Favori supprimé"
    }), 200

@app.route('/favories/count/<int:user_id>', methods=['GET'])
def count_my_favories(user_id):
    total = Favories.query.filter_by(user_id=user_id).count()

    return jsonify({
        "user_id": user_id,
        "count": total
    }), 200

@app.route("/publie", methods=["POST"])
def ajouter_my_annonces():
    data = request.json

    message = My_Annonces(
        name=data["name"],
        image_url=data["image_url"],
        prix=data["prix"],
        titre=data["titre"],
        ville=data["ville"],
        details=data["details"],
        numero=data["numero"],
        categories=data["categories"],
        user_id=data["user_id"],
    )

    db.session.add(message)
    db.session.commit()

    return jsonify({"message": "My_Annonces enregistré"})

@app.route('/admin/<int:user_id>', methods=['GET'])
def get_recupere(user_id):
    user = Admin.query.get(user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "Utilisateur introuvable"
        }), 404
   
    annonces = Annonce.query.all()
    result = []
    for all in annonces:
        result.append({
            "id": all.id,
            "name": all.name,
        })
    return jsonify(result)
if __name__ == "__main__":
    socketio.run(app, port=5000, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)
    #socketio.run(app, port=5000,debug=True)
    #app.run(debug=True)
