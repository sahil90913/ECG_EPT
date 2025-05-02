# from flask import Flask, render_template, request
# from Ecg import ECG
# import os
# from werkzeug.utils import secure_filename
# from flask_mysqldb import MySQL 
# import MySQLdb.cursors

# app = Flask(__name__)

# app.secret_key = 'abc@gcetts1234'  # <-- Add this line

# app.config['UPLOAD_FOLDER'] = 'static/uploads'

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'  # change if needed
# app.config['MYSQL_PASSWORD'] = 'SAHIL9735'
# app.config['MYSQL_DB'] = 'Ecg_gpt'

# mysql = MySQL(app)
# # Ensure upload folder exists
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ecq = ECG()

# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file:
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(filepath)
            
#             # Process ECG image
#             ecg_user_image = ecq.getImage(filepath)
#             leads = ecq.DividingLeads(ecg_user_image)
#             ecq.PreprocessingLeads(leads)
#             ecq.SignalExtraction_Scaling(leads)
#             ecg_1dsignal = ecq.CombineConvert1Dsignal()
#             ecg_final = ecq.DimensionalReduciton(ecg_1dsignal)
#             prediction = ecq.ModelLoad_predict(ecg_final)
            
#             return render_template('Result.html', prediction=prediction, image=filepath)
    
#     return render_template('final2.html')

# from flask import redirect, flash  # make sure these are imported
# from werkzeug.security import generate_password_hash

# @app.route('/register', methods=['POST'])
# def register():
#     name = request.form['name']
#     email = request.form['email']
#     password = request.form['password']

#     hashed_password = generate_password_hash(password)

#     cursor = mysql.connection.cursor()
#     try:
#         cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
#         mysql.connection.commit()
#         flash("Registration successful!", "success")
#     except:
#         flash("Email already exists!", "error")
#     finally:
#         cursor.close()

#     return redirect('/')

# from flask import session
# from werkzeug.security import check_password_hash

# # @app.route('/login', methods=['POST'])
# # def login():
# #     email = request.form['email']
# #     password = request.form['password']

# #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
# #     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
# #     user = cursor.fetchone()
# #     cursor.close()

# #     if user and check_password_hash(user['password'], password):
# #         cursor.execute("INSERT INTO login_logs (email) VALUES (%s)", (email,))
# #         mysql.connection.commit()
# #         session['user'] = user['name']
# #         flash("Login successful!", "success")
# #         return redirect('/')
# #     else:
# #         flash("Invalid email or password!", "error")
# #         return redirect('/')
# from flask import Flask, request, redirect, render_template, session, flash
# from werkzeug.security import check_password_hash
# import MySQLdb.cursors

# @app.route('/login', methods=['POST'])
# def login():
#     email = request.form['email']
#     password = request.form['password']

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#     user = cursor.fetchone()

#     if user and check_password_hash(user['password'], password):
#         session['user'] = user['name']  # You can store email too if needed
#         session['email'] = user['email']
#         flash("Login successful!", "success")

#         # Log the login in the database
#         cursor.execute("INSERT INTO login_logs (email, login_time) VALUES (%s, NOW())", (email,))
#         mysql.connection.commit()
#     else:
#         flash("Invalid email or password!", "error")

#     cursor.close()
#     return redirect('/')

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash("You have been logged out.", "info")
#     return redirect('/')

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from Ecg import ECG

app = Flask(__name__)
app.secret_key = 'abc@gcetts1234'

# Upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'SAHIL9735'
app.config['MYSQL_DB'] = 'Ecg_gpt'

mysql = MySQL(app)
ecq = ECG()

# Upload & Analyze ECG + Store image in MySQL
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'user' not in session:
            flash("Please login before uploading an ECG.", "warning")
            return redirect('/')

        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Convert image to binary for DB storage
            with open(filepath, 'rb') as f:
                binary_image = f.read()

            # Save image to database
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO ecg_data (user_email, image) VALUES (%s, %s)", (session['email'], binary_image))
            mysql.connection.commit()
            cursor.close()

            # Analyze the ECG
            ecg_user_image = ecq.getImage(filepath)
            leads = ecq.DividingLeads(ecg_user_image)
            ecq.PreprocessingLeads(leads)
            ecq.SignalExtraction_Scaling(leads)
            ecg_1dsignal = ecq.CombineConvert1Dsignal()
            ecg_final = ecq.DimensionalReduciton(ecg_1dsignal)
            prediction = ecq.ModelLoad_predict(ecg_final)

            return render_template('Result.html', prediction=prediction, image=filepath)

    return render_template('final2.html')

# Register
@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        flash("Registration successful!", "success")
    except:
        flash("Email already exists!", "error")
    finally:
        cursor.close()

    return redirect('/')

# Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        session['user'] = user['name']
        session['email'] = user['email']
        flash("Login successful!", "success")

        cursor.execute("INSERT INTO login_logs (email, login_time) VALUES (%s, NOW())", (email,))
        mysql.connection.commit()
    else:
        flash("Invalid email or password!", "error")

    cursor.close()
    return redirect('/')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)



