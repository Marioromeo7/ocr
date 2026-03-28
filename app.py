from flask import Flask,url_for,render_template,request,redirect,url_for
import os
from o import o
app=Flask(__name__)
UploadFolder='static/uploads'
os.makedirs(UploadFolder,exist_ok=True)
@app.route('/',methods=['POST','GET'])
def index():
    if request.method=='POST':
        if 'image' not in request.files:
            return 'img not found'
        file=request.files['image']
        path=os.path.join(UploadFolder,file.filename)
        file.save(path)
        return render_template('index.html',path=f"uploads/{file.filename}",v=o(path))
    return render_template('index.html')
if __name__=="__main__":
    app.run(debug=True)