from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import pickle

import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
# Load the model and label encoders
model = pickle.load(open('loan_model.pkl', 'rb'))
label_encoders = pickle.load(open('label_encoders.pkl', 'rb'))

# MySQL Database Connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='loan'
)
cursor = conn.cursor()

# Database setup
cursor.execute('''
CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
)
''')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('INSERT INTO User (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM User WHERE username=%s AND password=%s', (username, password))
        user = cursor.fetchone()
        if user:
            session['user'] = username
            return redirect(url_for('enter_details'))
        else:
            return 'Invalid Credentials'
    return render_template('login.html')



@app.route('/enter_details', methods=['POST', 'GET'])
def enter_details():
    if request.method == 'POST':
        details = request.form.to_dict()

        # Drop loan_id if present
        details.pop('loan_id', None)  # Use pop with default value None to avoid KeyError if loan_id is not present

        # Encode categorical features
        for column, le in label_encoders.items():
            if column in details:
                details[column] = le.transform([details[column]])[0]

        # Prepare input data for prediction
        input_data = []
        for feature in model.feature_names_in_:
            input_data.append(details.get(feature, 0))  # Default to 0 if feature is missing

        input_data = np.array(input_data).reshape(1, -1)

        # Make prediction
        prediction = model.predict(input_data)
        # print(f"Loan Details: {details}")
        # print(f"Prediction result: {prediction[0]}")
        return render_template('result.html', prediction=prediction[0])
    return render_template('predict.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, render_template, request, redirect, url_for, session
# import pickle
# import numpy as np
# import os

# app = Flask(__name__)
# app.secret_key = os.urandom(24)  # Generates a random secret key

# # Load the model and label encoders
# model = pickle.load(open('loan_model.pkl', 'rb'))
# label_encoders = pickle.load(open('label_encoders.pkl', 'rb'))

# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/register', methods=['POST', 'GET'])
# def enter_details():
#     if request.method == 'POST':
#         details = request.form.to_dict()

#         # Drop loan_id if present
#         details.pop('loan_id', None)  # Use pop with default value None to avoid KeyError if loan_id is not present

#         # Encode categorical features
#         for column, le in label_encoders.items():
#             if column in details:
#                 details[column] = le.transform([details[column]])[0]

#         # Prepare input data for prediction
#         input_data = []
#         for feature in model.feature_names_in_:
#             input_data.append(details.get(feature, 0))  # Default to 0 if feature is missing

#         input_data = np.array(input_data).reshape(1, -1)

#         # Make prediction
#         prediction = model.predict(input_data)
#         # print(f"Loan Details: {details}")
#         # print(f"Prediction result: {prediction[0]}")
#         return render_template('result.html', prediction=prediction[0])
#     return render_template('predict.html')

# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     return redirect(url_for('login'))

# if __name__ == '__main__':
#     app.run(debug=True)


# @app.route('/enter_details', methods=['GET', 'POST'])
# def enter_details():
#     if 'user' not in session:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         details = request.form.to_dict()
#         for column, le in label_encoders.items():
#             if column in details:
#                 details[column] = le.transform([details[column]])[0]
#         input_data = [details[key] for key in model.feature_names_in_]
#         prediction = model.predict([input_data])[0]
#         return render_template('result.html', result=prediction)
#     return render_template('predict.html')