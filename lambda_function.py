import json
import boto3
import random
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('TicTac-Users')
games_table = dynamodb.Table('TicTac-Games')

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return build_response(200, 'OK')

    path = event.get('path', '')
    method = event.get('httpMethod', '')

    try:
        # 1. LOGIN
        if path == '/login' and method == 'POST':
            body = json.loads(event.get('body', '{}'))
            email = body.get('email')
            username = body.get('username')
            users_table.put_item(Item={'email': email, 'username': username})
            return build_response(200, {'message': 'Logged in successfully'})

        # 2. CREATE GAME (Generates 4-digit code)
        elif path == '/create' and method == 'POST':
            body = json.loads(event.get('body', '{}'))
            creator = body.get('email')
            
            # Generate a random 4-digit code
            code = str(random.randint(1000, 9999))
            
            new_game = {
                'gameId': code,
                'playerX': creator,
                'playerO': 'waiting',
                'board': ['', '', '', '', '', '', '', '', ''],
                'turn': creator,
                'status': 'waiting_for_player',
                'winner': 'none'
            }
            games_table.put_item(Item=new_game)
            return build_response(200, {'message': 'Game created!', 'code': code})

        # 3. JOIN GAME (Uses 4-digit code)
        elif path == '/join' and method == 'POST':
            body = json.loads(event.get('body', '{}'))
            joiner = body.get('email')
            code = str(body.get('code'))
            
            # Lookup the game by the code directly!
            game = games_table.get_item(Key={'gameId': code}).get('Item')
            
            if not game:
                return build_response(404, {'message': 'Invalid 4-digit code!'})
            if game['status'] != 'waiting_for_player':
                return build_response(400, {'message': 'Game is already full!'})
                
            game['playerO'] = joiner
            game['status'] = 'playing'
            games_table.put_item(Item=game)
            
            return build_response(200, {'message': 'Joined successfully!'})

        # 4. GET GAME (Polling)
        elif path == '/game' and method == 'GET':
            email = event.get('queryStringParameters', {}).get('email')
            
            response_x = games_table.query(IndexName='PlayerXIndex', KeyConditionExpression=Key('playerX').eq(email))
            response_o = games_table.query(IndexName='PlayerOIndex', KeyConditionExpression=Key('playerO').eq(email))
            
            games = response_x.get('Items', []) + response_o.get('Items', [])
            
            # Return either a playing game or a game waiting for someone to join
            for game in games:
                if game['status'] in ['playing', 'waiting_for_player', 'finished']:
                    return build_response(200, game)
                    
            return build_response(200, {'status': 'no_active_game'})

        # 5. MAKE MOVE
        elif path == '/move' and method == 'POST':
            body = json.loads(event.get('body', '{}'))
            game_id = body.get('gameId')
            email = body.get('email')
            position = int(body.get('position'))
            
            game = games_table.get_item(Key={'gameId': game_id}).get('Item')
            
            if game['turn'] != email: return build_response(400, {'message': 'Not your turn!'})
            if game['board'][position] != '': return build_response(400, {'message': 'Spot taken!'})
                
            symbol = 'X' if email == game['playerX'] else 'O'
            game['board'][position] = symbol
            game['turn'] = game['playerO'] if symbol == 'X' else game['playerX']
            
            win_states = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
            board = game['board']
            for state in win_states:
                if board[state[0]] != '' and board[state[0]] == board[state[1]] == board[state[2]]:
                    game['winner'] = email
                    game['status'] = 'finished'
            
            if '' not in board and game['status'] != 'finished':
                game['winner'] = 'draw'
                game['status'] = 'finished'
                
            games_table.put_item(Item=game)
            return build_response(200, game)

        # 6. CLEAR STUCK GAMES
        elif path == '/clear' and method == 'POST':
            body = json.loads(event.get('body', '{}'))
            email = body.get('email')
            
            response_x = games_table.query(IndexName='PlayerXIndex', KeyConditionExpression=Key('playerX').eq(email))
            response_o = games_table.query(IndexName='PlayerOIndex', KeyConditionExpression=Key('playerO').eq(email))
            games = response_x.get('Items', []) + response_o.get('Items', [])
            
            for game in games:
                games_table.delete_item(Key={'gameId': game['gameId']})
                
            return build_response(200, {'message': 'Games cleared!'})

        return build_response(404, {'message': 'Route not found'})

    except Exception as e:
        return build_response(500, {'error': str(e)})