
from copy import copy
from http.client import HTTPResponse
import os
import datetime

from enum import Enum
from tkinter import N
from certifi import contents

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, PositiveFloat

from database import Database

from convert_utility import currency_converter

from account_utility import initialize_transaction, check_if_data_is_existing

app = FastAPI()

from fastapi.encoders import jsonable_encoder

#Pour lancer le serveur :
#python -m uvicorn app:app --reload


#Types de transaction
class Transaction_type(str, Enum):
    depot = 'deposit'
    retrait = 'withdrawal'


#Liste des devises étrangères autorisées
class Allowed_currencies(str, Enum):
    australie = "AUD"
    canada = "CAD"
    suisse = "CHF"
    danemark = "DKK"
    euro = "EUR"
    royaume_uni = "GBP"
    hong_kong = "HKD"
    inde = "INR"
    japon = "JPY"
    mexique = "MXN"
    norvege = "NOK"
    russie = "RUB"
    suede = "SEK"
    taiwan = "TWD"
    usa = "USD"
    afrique_sud = "ZAR"
    

#Transaction
class Transaction(BaseModel):
    label: str
    trade_amount: PositiveFloat
    trade_currency: Allowed_currencies
    type: Transaction_type
    date: datetime.date=datetime.datetime.now().strftime('%Y-%m-%d')


class Account(BaseModel):
    account_id: str


class Client(BaseModel):
    name: str
    first_name: str


def transStr(valeur):
    return valeur.upper()


#=============================================================================================
#==========    CLIENTS                                                              ==========
#=============================================================================================


# ************************** GET Client **************************

@app.get("/clients/")
async def list_clients():
    """
    Liste les clients de la banque.
    
    Returns :
        api_response (list): liste des clients de la banque
    """
    
    # Récupère les clients de la base
    db = Database()
    db_clients = db.get_clients()

    # Retourne une liste formatée
    api_response = []
    for client_id, client_dict in db_clients.items():
        api_response.append({
            'id': client_id,
            'name': client_dict['name'],
            'first_name': client_dict['first_name'],
        })
    return api_response


@app.get("/clients/{client_id}")
async def get_client(client_id: str):
    """
    Récupère un client de la banque en fonction de son identifiant.

    args:
        client_id (string) : identifiant du client

    Returns:
        Détail du client (sous forme de dictionnaire)

    """
    # Récupère le client de la base
    db = Database()
    db_client = db.get_client(client_id)

    # Retourne la réponse formatée
    return {
        'id': client_id,
        'name': db_client['name'],
        'first_name': db_client['first_name']
        #get_client_accounts(client_id)
    }


# ************************** POST Client *************************

@app.post("/clients/")
async def create_client(client: Client):
    """
    Création d'un nouveau client.

    args:
        client (classe) : nom et prénom du client à créer

    Returns :
        client (classe) : détail du client créé
    """
    # Récupère les clients de la base
    db = Database()
    db_clients = db.get_clients()

    # Trouve un nouvel identifiant
    client_id = str(int(max(map(int, db_clients.keys()), default=0)) + 1)

    # Ajoute le client à la base
    db_clients[client_id] = {
        'name': client.name,
        'first_name': client.first_name,
        'accounts': {}
    }

    # Sauvegarde la base
    db.save()

    return client


# ************************** PUT Client **************************

@app.put("/clients/{client_id}/")
async def update_client(client_id: str, client: Client):
    """
    Mise à jour un client.

    args:
        client_id (string) : idntification du client
        client (classe): données du client à mettre à jour

    Returns :
        client (classe) : détail du client mis à jour
    """
    # Récupère le client de la base
    db = Database()
    db_client = db.get_client(client_id)

    # Met à jour le client
    db_client.update(client)

    # Sauvegarde la base
    db.save()

    return client


# ************************** DELETE Client ***********************

@app.delete("/clients/{client_id}/")
async def delete_client(client_id: str):
    """
    Suppression un client.

    args :
        client_id (string) : identifiant du client à supprimer

    Returns:
        message de réalisation ou de non réalisation de la suppression
    """
    # Récupère le client de la base
    db = Database()
    db.get_client(client_id)

    #suppression du client
    deleted_client = db.get_clients().pop(client_id)

    # Sauvegarde la base
    db.save()

    #On retourne le client supprimé
    return deleted_client



#=============================================================================================
#==========    ACCOUNTS                                                             ==========
#=============================================================================================


# ************************** GET Client accounts **************************

#@app.get("/clients/{client_id}/{account_id}")
@app.get("/clients/{client_id}/accounts/")
async def get_client_accounts(client_id: str):
    """
    Liste les comptes d'un client.

    args :
        client_id (string) : identifiant du client à supprimer

    Returns:
        db.get_accounts(client_id) (dict) : détail des comptes du client
    """
    # Récupère le client de la base
    db = Database()

    return db.get_accounts(client_id)


@app.get("/clients/{client_id}/{account_id}/")
async def get_client_account(client_id: str, account_id: str):
    """
    Liste d'un seul compte d'un client.

    args :
        client_id (string) : identifiant du client à supprimer

    Returns:
        db_account (dict) : détail du compte du client
    """
    'On force le compte en majuscule'
    account_id = account_id.upper()

    # Récupère le client de la base
    db = Database()
    db.get_client(client_id)

    # Retourne une liste formatée
    return db.get_account(client_id, account_id)


# ************************** POST Client accounts *************************

@app.post("/clients/{client_id}/accounts/")
async def create_account(client_id: str, account_id: str, authorized_overdraft: float=0.0):
    """
    Créer un nouveau compte à un client.

    args : 
        client_id (string) : identification du client 
        account_id (string) : numéro de compte à créer 
        authorized_overdraft (float) : montant du découvert autorisé (par défaut : 0) 

    Returns :
        db_client (dict) : détail du compte créé s'il n'était pas déjà éxistant
    """
    'On force le compte en majuscule'
    account_id = account_id.upper()
    # Récupère les clients de la base
    db = Database()
    db_client=db.get_client(client_id)

    if account_id in db_client['accounts'].keys():
        raise HTTPException(status_code=210, detail="Account already existing")
    else:
        db_account=db.get_accounts(client_id)

        'On crée le compte'
        db_account[account_id]={'balance':0, 'authorized_overdraft': abs(authorized_overdraft), 'transaction':[]}

        # Sauvegarde la base
        db.save()

        return db.get_account(client_id, account_id)
  
        


# ************************** DELETE Client accounts ***********************

@app.delete("/clients/{client_id}/{account_id}/")
async def delete_client_account(client_id: str, account_id: str):
    """
    Suppression d'un compte.

    args :
        client_id (string) : identification du client
        account_id (string) : numéro de compte à supprimer

    return :
        message : statut en fonction de la suppression ou non du compte.
    """
    'On force le compte en majuscule'
    account_id = account_id.upper()
    # Récupère le client de la base
    db = Database()
    db_client = db.get_client(client_id)
    db_account = db.get_account(client_id, account_id)

    solde_compte = db_account['balance']
    
    #Suppression du compte si son solde est à 0
    if solde_compte != 0:
        raise HTTPException(status_code=202, detail=f"Suppression du compte {account_id} impossible car le solde n'est pas à 0 (solde du compte : {solde_compte} €)")
    else:
        del db_client['accounts'][account_id]

        # Sauvegarde la base
        db.save()
        return f"Suppression du compte {account_id} pour le client {client_id} effectuée."


# ************************** PUT Client accounts **************************

@app.patch("/clients/{client_id}/{account_id}")
async def update_client_balance(client_id: str, account_id: str, amount_to_set: float):
    """
    Modification du solde du compte d'un client.

    args :
        client_id (string) : identification du client
        account_id (string) : compte sur lequel la modification de solde doit être effectuée
        amount_to_set (float) : Nouveau solde du compte

    Returns :
        message : information sur l'opération effectuée/non effectué.
    """
    'On force le compte en majuscule'
    account_id = account_id.upper()
    type_transaction = None

    # Récupère le client de la base
    db = Database()
    db.get_client(client_id)
    db_account = db.get_account(client_id, account_id)

    solde_avant_modif = db_account['balance']

    #Calcul du montant de l'opération à enregistrer
    montant_operation = amount_to_set-solde_avant_modif

    #Détermination du type de transaction
    if montant_operation < 0:
        type_transaction = Transaction_type.retrait.value 
    else:
        type_transaction = Transaction_type.depot.value 

    id_transaction = len(db_account["transaction"])+1

    #Création de la transaction liée à la modiciation de solde
    transaction = initialize_transaction(label="Modification du solde", trade_amount=abs(montant_operation), type=type_transaction, id_transaction=id_transaction)

    #Enregistrement de la transaction
    db_account["transaction"].append(transaction)

    #Enregistrement du nouveau solde
    db_account['balance']=amount_to_set

    # Sauvegarde la base
    db.save()

    return f"Modification du solde du compte {account_id} (client n°{client_id}) effectuée."


#=============================================================================================
#==========    TRANSACTIONS                                                         ==========
#=============================================================================================


# ************************** GET Transactions **************************

@app.get("/clients/{client_id}/{account_id}/transactions/")
async def get_account_transactions(client_id: str, account_id: str):
    """
    Voir les transactions sur le compte d'un client

    args :
        client_id (string) : Numéro du client
        account_id (string) : Référence du compte client

    Returns :
        db_transactions (list) : Détail des transaction du compte
    """
    'On force le compte en majuscule'
    account_id = account_id.upper()

    db = Database()
    
    db.get_client(client_id)
    db.get_account(client_id, account_id)

    return db.get_transactions(client_id, account_id)


@app.get("/clients/{client_id}/{account_id}/transactions/{transaction_id: int}")
async def get_account_transactions(client_id: str, account_id: str, transaction_id: int):
    """
    Voir les transactions sur le compte d'un client

    args :
        client_id (string) : Numéro du client
        account_id (string) : Référence du compte client

    Returns :
        db_transactions (list) : Détail des transaction du compte
    """
    'On force le compte en majuscule'
    account_id = account_id.upper()

    db = Database()

    db.get_client(client_id)
    db.get_account(client_id, account_id)

    return db.get_transaction(client_id, account_id, transaction_id)


# ************************** POST Transactions *************************

#@app.post("/clients/{client_id}/accounts/transaction")
@app.post("/clients/{client_id}/{account_id}/transaction/")
#async def create_transaction(client_id: str, account_id: str, transaction_type: Transaction_type, amount: float, label: str, date=str(datetime.now().strftime('%Y-%m-%d'))):#Avec les données en paramètre
async def create_transaction(client_id: str, account_id: str, transaction: Transaction): #Avec paramètres de la transaction dans le body (utilise l'objet Transaction)
    """
    Créer une transaction sur le compte d'un client.
    Les transactions sont acceptées à partir du moment où le solde du compte est positif.

    args :
        client_id (string) : Numéro du client
        account_id (string) : Référence du compte client
        transaction (Transaction) : données obligatoires à la création d'une transaction

    Returns :

    """
    'On force le compte en majuscule'
    account_id = account_id.upper()

    db = Database()
    db.get_client(client_id)
    db_account= db.get_account(client_id, account_id)

    db_clients = db.get_clients()
    
    #On récupère le solde du compte
    solde_compte = float(db_account["balance"])
 
    decouvert_autorise = db_account['authorized_overdraft']

    db_transaction = db_clients[client_id]['accounts'][account_id]["transaction"]

    #On transforme le json en dictionnaire
    transaction = jsonable_encoder(transaction)

    if transaction['type'] == Transaction_type.retrait and solde_compte <= 0 and abs(solde_compte) >= decouvert_autorise:
        return "Transaction refusée"
    
    #On récupère le montant de l'opération
    montant_operation = float(transaction['trade_amount'])

    if transaction['trade_currency'] == "EUR":
        # Si la transaction est en Euros, pas de conversion
        amount_in_euro = montant_operation
    else:
        # Si la transaction est en devise, on passe par l'API de conversion
        retour_convertion = currency_converter(transaction['trade_currency'], "EUR", montant_operation) 
        amount_in_euro = round(retour_convertion["result"],2)

    # On renseigne le montant en Euros de la transaction
    transaction['amount_in_euro']=amount_in_euro
    transaction['account_currency']="EUR"

    #On récupère le sens de l'opération
    type_transaction = transaction['type']

    #On calcul le nouveau solde
    if Transaction_type.depot == type_transaction:
        solde_compte += amount_in_euro
    else:
        solde_compte -= amount_in_euro
    
    #On affecte le nouveau solde
    db_clients[client_id]['accounts'][account_id]["balance"]=solde_compte

    #On détermine le numéro de transaction
    id_transaction = len(db_transaction)+1
    transaction['id_transaction']=id_transaction

    # On ajoute la transaction
    db_transaction.append(transaction)

    # Sauvegarde de la base
    db.save()

    return f"Transaction n°{id_transaction} enregistrée sur le compte {account_id}"



# ************************** PUT Transactions **************************

@app.put("/clients/{client_id}/{account_id}/transaction/{transaction_id}/")
async def update_transaction(client_id: str, account_id: str, transaction_id: int, transaction_label: str=None):
    """
    Mise àjour du libellé d'une transaction.

    args :
        client_id (string) : Numéro du client
        account_id (string) : Référence du compte client
        transaction_id (int) : référence de la transaction à modifier
        transaction_label (string) : nouveau libellé de la transaction
    """
    'On force le compte en majuscule'
    account_id = account_id.upper()

    if transaction_label !=None:
        db = Database()

        db.get_client(client_id)
        db.get_account(client_id, account_id)

        #On récupère la liste des transactions
        db_transaction = db.get_transaction(client_id, account_id, transaction_id)
        
        db_transaction['label'] = transaction_label

        db.save()

        return db_transaction


# *********************** DELETE Transactions **************************

@app.delete("/clients/{client_id}/{account_id}/transaction/{transaction_id}/cancel/")
async def delete_transaction(client_id: str, account_id: str, transaction_id: int):
    """
    Annulation d'un transaction (la transaction ne sera pas supprimée mais contre-passée)

    args :
        client_id (string) : Numéro du client
        account_id (string) : Référence du compte client
        transaction_id (int) : référence de la transaction à modifier

    Returns :
        Message de confirmation de l'annulation ou ntransaction non trouvée
    """
    'On force le compte en majuscule'
    account_id = account_id.upper()

    db = Database()
    db.get_client(client_id)
    db_account = db.get_account(client_id, account_id)
    db_transaction = db.get_transaction(client_id, account_id, transaction_id)
    db_transactions = db.get_transactions(client_id, account_id)

    # On crée la transaction d'annulation (reflet de la trasaction d'origine)
    cancellation = copy(db_transaction)

    # On modifie les éléments de la transaction d'annulation
    if db_transaction['type'] == Transaction_type.depot.value:
        cancellation['type'] = Transaction_type.retrait.value
        db_account['balance'] -= db_transaction['amount_in_euro']
    else:
        cancellation['type'] = Transaction_type.depot.value
        db_account['balance'] += db_transaction['amount_in_euro']

    cancellation['id_transaction'] = len(db_transactions)+1
    cancellation['label'] = f"Annulation opération n°{transaction_id}"

    #Modification du solde
    db_transactions.append(cancellation)

    db.save()

    return cancellation


@app.post("/clients/{client_id}/{accouunt_id}/transfert/")
async def transfert(client_id: str, account_id_debited: str, account_id_credited: str, amount_to_transfer: float):
    """
    Virement entre deux comptes appartenant au client.

    args :
        client_id (string) : Numéro du client
        account_id_debited (string) : Référence du compte client à débiter
        account_id_credited (string) : Référence du compte client à créditer
        amount_to_transfer (float) : montant du transfert à effectuer

    Returns :
        messages : avis d'exécution (ou de non-exécution) du virement        
    """
    'On force les numéros de compte en majuscule'
    account_id_debited = account_id_debited.upper()
    account_id_credited = account_id_credited.upper()

    # Récupère le client de la base
    db = Database()
    db.get_client(client_id)

    # Compte à débiter
    account_debited = db.get_account(client_id, account_id_debited)
    db_transactions_account_debited = db.get_transactions(client_id, account_id_debited)

    # Compte à créditer
    account_credited = db.get_account(client_id, account_id_credited)
    db_transactions_account_credited = db.get_transactions(client_id, account_id_credited)

    if account_id_debited == account_id_credited:
        return f"Les comptes séléctionnés sont identiques (séléction : {account_id_credited})."
    else:
        id_transaction = len(db_transactions_account_debited)+1
        transaction_debitrice = initialize_transaction(label = f"Virement interne vers compte {account_id_credited}", trade_amount = amount_to_transfer, type = Transaction_type.retrait.value, id_transaction=id_transaction)
        account_debited["transaction"].append(transaction_debitrice)
        id_transaction = len(db_transactions_account_credited)+1
        transaction_creditrice = initialize_transaction(label = f"Virement interne du compte {account_id_debited}", trade_amount = amount_to_transfer, type = Transaction_type.depot.value, id_transaction=id_transaction)
        account_credited["transaction"].append(transaction_creditrice)

        #On affecte les soldes des comptes concernés
        account_debited['balance']-=amount_to_transfer
        account_credited['balance']+=amount_to_transfer

        db.save()
        
        return f"Transfert de {amount_to_transfer} € du compte {account_id_debited} vers le compte {account_id_credited} effectué."
