def extract_token(event):
    auth_header = event['headers'].get('Authorization', '')
    if auth_header.startswith('Bearer '):
        id_token = auth_header.split('Bearer ')[1]
    else:
        id_token = auth_header
    print(f'id_token found: {id_token}')
    return id_token
