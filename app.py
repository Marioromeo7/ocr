from flask import Flask, jsonify, render_template, request
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
        result=o(path)
        if request.accept_mimetypes.best == "application/json":
            return jsonify(result)
        return render_template('index.html',path=f"uploads/{file.filename}",result=result)
    return render_template('index.html')
if __name__=="__main__":
    app.run(debug=True)
