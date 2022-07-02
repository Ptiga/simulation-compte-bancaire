import requests

def currency_converter(source_currency, aimed_currency, amount_to_convert):

    url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/convert"

    querystring = {"from":f"{source_currency}","to":f"{aimed_currency}","amount":f"{amount_to_convert}"}

    headers = {
        "X-RapidAPI-Host": "currency-conversion-and-exchange-rates.p.rapidapi.com",
        "X-RapidAPI-Key": "6da360a04bmsh5f411badbd570c0p1e8016jsn833f7a3d16a6"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()

#    print('réponse: ',response)
#    print('réponse (en txt): ',response.text)
#    print(type(response.text))
#    print(response.content)
#    print('JSON: ',response.json())
#    print(type(response.json()))

#    reponse_dico = jsonable_encoder(response.json())

#    print('réponse dico:')
#    print(reponse_dico)
#    print(type(reponse_dico))
#    print(reponse_dico["result"])



#currency_converter("USD", "EUR", 100.00)
