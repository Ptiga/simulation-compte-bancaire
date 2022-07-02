
import os
import json
from pydantic import BaseModel
from fastapi import HTTPException


# Pour les besoins de la formation nous sauvegarderons les données
# de cette application dans un fichier json.
# En temps normal il faudrait se servir d'une véritable base de données (SQL) :
# https://fastapi.tiangolo.com/tutorial/sql-databases/


# A chaque fois qu'on voudra faire une opération sur les données, il faudra :
# - Télécharger le contenu du fichier json dans une variable python : `db_dict = get_db()`
# - Faire les opérations sur cette variable : `db_dict`
# - Sauvegarder le contenu de la varaible `db_dict` dans le fichier json : `save_db(db_dict)`


DB_FILENAME = 'db.json'


class Database:

    """
    Le schéma du dictionnaire de la base de donnée est le suivant :
    {
        "clients": {
            <client_id>: {
                "name": <name>,
                "first_name": <first_name>,
                "accounts": {
                    <account_id>: {
                        "balance": <balance>,
                        "authorized_overdraft" : <overdraft>
                        "transactions": [
                            {
                                "label": <label>,
                                "amount_in_euro": <value>,
                                "account_currency": <currency>
                                "type": <withdrawal|deposit>,
                                "date": <date>,
                                "id_transaction": <id_transaction>
                                "trade_amount": <trade_amount>
                                "trade_currency": <trade_currency>
                            }
                        ]
                    }
                }
            }
        }
    }
    """

    def __init__(self):
        self._db = self.download()

    def download(self):
        """
        Télécharge la base de donnée du fichier json.
        retourne le contenu du json dans un dict.
        Créer le fichier s'il n'éxiste pas.
        """
        if not os.path.isfile(DB_FILENAME):
            json_file = open(DB_FILENAME, 'w')
            json.dump({"clients": {}}, json_file)

        with open(DB_FILENAME, 'r') as json_file:
            return json.load(json_file)

    def save(self):
        """
        Sauvegarde db_dict dans le ficher json.
        """
        json_dict = json.dumps(self._db, indent=2)
        with open(DB_FILENAME, 'w') as json_file:
            json_file.write(json_dict)

    def get_clients(self):
        return self._db['clients']

    def get_client(self, client_id):
        """
        Récupère un client.
        """
        try:
            return self.get_clients()[client_id]
        except KeyError:
            raise HTTPException(status_code=404, detail="Client not found")


    def get_accounts(self, client_id):
        """
        Récupère les comptes d'un client.
        """
        try:
            return self.get_clients()[client_id]['accounts']
        except KeyError:
            raise HTTPException(status_code=404, detail="No account for this client")


    def get_account(self, client_id, account_id):
        """
        Récupère les comptes d'un client.
        """
        try:
            return self.get_clients()[client_id]['accounts'][account_id]
        except KeyError:
            raise HTTPException(status_code=404, detail="Account not found")


    def get_transactions(self, client_id, account_id):
        """
        Récupère les comptes d'un client.
        """
        try:
            return self.get_clients()[client_id]['accounts'][account_id]["transaction"]
        except IndexError:
            raise HTTPException(status_code=404, detail="No transactions for this account")
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Account {account_id} not existing for client {client_id}")


    def get_transaction(self, client_id, account_id, transaction_id):
        """
        Récupère les comptes d'un client.
        """
        try:
            return self.get_clients()[client_id]['accounts'][account_id]["transaction"][transaction_id-1]
        except IndexError:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Account {account_id} or client {client_id} not existing")

        