from flask import Flask, render_template, request
from Ecg import ECG  # Ensure file is named correctly
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ecq = ECG()  # Ensure this class is properly implemented in ecg.py

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        print(f"File saved to {filepath}")  # Debugging

        try:
            # Process ECG image
            ecg_user_image = ecq.getImage(filepath)
            leads = ecq.DividingLeads(ecg_user_image)
            ecq.PreprocessingLeads(leads)
            ecq.SignalExtraction_Scaling(leads)
            ecg_1dsignal = ecq.CombineConvert1Dsignal()
            ecg_final = ecq.DimensionalReduciton(ecg_1dsignal)
            prediction = ecq.ModelLoad_predict(ecg_final)

            print("Prediction:", prediction)  # Debugging

            return render_template('Result.html', prediction=prediction, image=filepath)

        except Exception as e:
            print("Error:", e)
            return f"Processing error: {str(e)}", 500

    return render_template('hi (1).html')

if __name__ == '__main__':
    app.run(debug=True)
