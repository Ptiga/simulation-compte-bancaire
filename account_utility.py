import datetime
from operator import truediv

# Fonction d'nitialisation de transaction
def initialize_transaction(label = "", trade_amount = 0.0, trade_currency = "EUR", type = "", date = datetime.datetime.now().strftime('%Y-%m-%d'), amount_in_euro = 0.0, id_transaction = ""):
        if trade_currency == "EUR":
            return {"label": label, \
                "trade_amount": trade_amount, \
                "trade_currency":trade_currency, \
                "type": type, \
                "date": date, \
                "amount_in_euro":trade_amount, \
                "account_currency":"EUR", \
                "id_transaction": id_transaction}
        else:
            return {"label": label, \
                "trade_amount": trade_amount, \
                "trade_currency":trade_currency, \
                "type": type, \
                "date": date, \
                "amount_in_euro":amount_in_euro, \
                "account_currency":"EUR", \
                "id_transaction": id_transaction}


# Fonction de vérification d'éléments existants
def check_if_data_is_existing(list_checked, data_to_check):
    if data_to_check in list_checked.keys():
        return True
    else:
        return False

