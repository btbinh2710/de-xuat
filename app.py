from flask import Flask, request, jsonify
   import sqlite3
   import bcrypt
   import jwt
   import datetime
   import os

   app = Flask(__name__)
   JWT_SECRET = os.environ.get('JWT_SECRET')

   if not JWT_SECRET:
       raise ValueError("JWT_SECRET environment variable is not set")

   def get_db():
       try:
           conn = sqlite3.connect('data.db')
           conn.row_factory = sqlite3.Row
           return conn
       except sqlite3.Error as e:
           app.logger.error(f"Database connection error: {e}")
           raise

   @app.route('/', methods=['GET'])
   def health_check():
       return jsonify({'status': 'healthy'}), 200

   @app.route('/api/register', methods=['POST'])
   def register():
       try:
           data = request.get_json()
           username = data['username']
           password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
           branch = data['branch']
           role = data.get('role', 'branch')
           conn = get_db()
           c = conn.cursor()
           c.execute('INSERT INTO users (username, password, branch, role) VALUES (?, ?, ?, ?)',
                     (username, password, branch, role))
           conn.commit()
           return jsonify({'message': 'User created'}), 201
       except sqlite3.IntegrityError:
           return jsonify({'error': 'Username already exists'}), 400
       except Exception as e:
           app.logger.error(f"Register error: {e}")
           return jsonify({'error': 'Internal server error'}), 500
       finally:
           if 'conn' in locals():
               conn.close()

   @app.route('/api/login', methods=['POST'])
   def login():
       try:
           data = request.get_json()
           username = data['username']
           password = data['password'].encode('utf-8')
           conn = get_db()
           c = conn.cursor()
           c.execute('SELECT * FROM users WHERE username = ?', (username,))
           user = c.fetchone()
           if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
               token = jwt.encode({
                   'username': username,
                   'branch': user['branch'],
                   'role': user['role'],
                   'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
               }, JWT_SECRET, algorithm='HS256')
               return jsonify({'token': token, 'branch': user['branch'], 'role': user['role']})
           return jsonify({'error': 'Invalid credentials'}), 401
       except sqlite3.Error as e:
           app.logger.error(f"Database error during login: {e}")
           return jsonify({'error': 'Database error'}), 500
       except Exception as e:
           app.logger.error(f"Login error: {e}")
           return jsonify({'error': 'Internal server error'}), 500
       finally:
           if 'conn' in locals():
               conn.close()

   @app.route('/api/proposals', methods=['POST'])
   def create_proposal():
       try:
           token = request.headers.get('Authorization', '').split(' ')[1]
           payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
           data = request.get_json()
           data['branch'] = payload['branch']
           conn = get_db()
           c = conn.cursor()
           c.execute('''INSERT INTO proposals (proposer, department, date, code, proposal, content, supplier, estimated_cost, approved_amount, notes, completed, branch)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (data['proposer'], data['department'], data['date'], data['code'], data['proposal'],
                      data['content'], data['supplier'], data['estimated_cost'], data['approved_amount'],
                      data['notes'], data['completed'], data['branch']))
           conn.commit()
           proposal_id = c.lastrowid
           return jsonify({'id': proposal_id, **data}), 201
       except jwt.ExpiredSignatureError:
           return jsonify({'error': 'Token expired'}), 401
       except jwt.InvalidTokenError:
           return jsonify({'error': 'Invalid token'}), 401
       except Exception as e:
           app.logger.error(f"Create proposal error: {e}")
           return jsonify({'error': 'Internal server error'}), 500
       finally:
           if 'conn' in locals():
               conn.close()

   @app.route('/api/proposals', methods=['GET'])
   def get_proposals():
       try:
           token = request.headers.get('Authorization', '').split(' ')[1]
           payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
           conn = get_db()
           c = conn.cursor()
           if payload['role'] == 'admin':
               c.execute('SELECT * FROM proposals')
           else:
               c.execute('SELECT * FROM proposals WHERE branch = ?', (payload['branch'],))
           proposals = [dict(row) for row in c.fetchall()]
           return jsonify(proposals)
       except jwt.ExpiredSignatureError:
           return jsonify({'error': 'Token expired'}), 401
       except jwt.InvalidTokenError:
           return jsonify({'error': 'Invalid token'}), 401
       except Exception as e:
           app.logger.error(f"Get proposals error: {e}")
           return jsonify({'error': 'Internal server error'}), 500
       finally:
           if 'conn' in locals():
               conn.close()

   @app.route('/api/proposals/<int:id>', methods=['PUT'])
   def update_proposal(id):
       try:
           token = request.headers.get('Authorization', '').split(' ')[1]
           payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
           data = request.get_json()
           conn = get_db()
           c = conn.cursor()
           c.execute('''UPDATE proposals SET proposer = ?, department = ?, date = ?, code = ?, proposal = ?, content = ?, supplier = ?, estimated_cost = ?, approved_amount = ?, notes = ?, completed = ?
                        WHERE id = ? AND branch = ?''',
                     (data['proposer'], data['department'], data['date'], data['code'], data['proposal'],
                      data['content'], data['supplier'], data['estimated_cost'], data['approved_amount'],
                      data['notes'], data['completed'], id, payload['branch']))
           conn.commit()
           if c.rowcount == 0:
               return jsonify({'error': 'Proposal not found or unauthorized'}), 404
           return jsonify(data)
       except jwt.ExpiredSignatureError:
           return jsonify({'error': 'Token expired'}), 401
       except jwt.InvalidTokenError:
           return jsonify({'error': 'Invalid token'}), 401
       except Exception as e:
           app.logger.error(f"Update proposal error: {e}")
           return jsonify({'error': 'Internal server error'}), 500
       finally:
           if 'conn' in locals():
               conn.close()

   @app.route('/api/proposals/<int:id>', methods=['DELETE'])
   def delete_proposal(id):
       try:
           token = request.headers.get('Authorization', '').split(' ')[1]
           payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
           conn = get_db()
           c = conn.cursor()
           c.execute('DELETE FROM proposals WHERE id = ? AND branch = ?', (id, payload['branch']))
           conn.commit()
           if c.rowcount == 0:
               return jsonify({'error': 'Proposal not found or unauthorized'}), 404
           return jsonify({'message': 'Proposal deleted'})
       except jwt.ExpiredSignatureError:
           return jsonify({'error': 'Token expired'}), 401
       except jwt.InvalidTokenError:
           return jsonify({'error': 'Invalid token'}), 401
       except Exception as e:
           app.logger.error(f"Delete proposal error: {e}")
           return jsonify({'error': 'Internal server error'}), 500
       finally:
           if 'conn' in locals():
               conn.close()

   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 10000))
       app.run(host='0.0.0.0', port=port)