# -*- coding: utf-8 -*-
"""

@author: manish
"""

from Platypus.platypus import *
from skmoefs.toolbox import MPAES_RCS, load_dataset, normalize
from skmoefs.rcs import RCSInitializer, RCSVariator
from skmoefs.discretization.discretizer_base import fuzzyDiscretization
from sklearn.model_selection import train_test_split


import os
from flask import Flask, flash, request, redirect, url_for, render_template, request
from werkzeug.utils import secure_filename
from contextlib import redirect_stdout
    
from flask import send_from_directory
import webbrowser

from io import StringIO 
import sys



max_evaluations = 10000

#UPLOAD_FOLDER = './UPLOADED_FILES'
ALLOWED_EXTENSIONS = {'dat'}

app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.secret_key = 'super secret key'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    
    global max_evaluations
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            #flash('PROCESSING......') 
            
            return redirect(url_for('download_rules', name=filename))
       
            
    return render_template('index.html', max_evaluations=max_evaluations) 
   

  

@app.route('/<name>')
def download_rules(name):
    
    
    
    
    X, y, attributes, inputs, outputs = load_dataset(name)
    X_n, y_n = normalize(X, y, attributes)
    Xtr, Xte, ytr, yte = train_test_split(X_n, y_n, test_size=0.3)
    my_moefs = MPAES_RCS(variator=RCSVariator(), initializer=RCSInitializer())
    my_moefs.fit(Xtr, ytr, max_evaluations)
    
    
    tmp = sys.stdout
    my_result = StringIO()
    sys.stdout = my_result
    my_moefs.show_model('median', inputs=inputs, outputs=outputs)
    sys.stdout = tmp
    text = my_result.getvalue()
    text = text.splitlines() 
    
    ##### Write rules to a to std output file ###########
    # with open('rules.txt', 'w') as f:
    #     with redirect_stdout(f):
    #         l = str(my_moefs.show_model('median', inputs=inputs, outputs=outputs))
    #         print(l)
    # #return f.name 
    # webbrowser.open('rules.txt')
    return render_template('Rules.html', text=text, pb=True)


    # os.remove('rules.txt')
    # with RedirectedStdout() as out:        
    #     print(my_moefs.show_model('median', inputs=inputs, outputs=outputs))
    #     ll = str(out)
    
#     return redirect(url_for('show_rules', text=ll)) 
        
    

# @app.route('/Rules/<text>')
# def show_rules(text):
    
#      



if __name__ == '__main__':
    app.run()