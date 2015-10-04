import os
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory
from werkzeug import secure_filename

app = Flask(__name__)
app.config.from_pyfile('SkinDoc.cfg')
UPLOAD_FOLDER = os.environ['OPENSHIFT_REPO_DIR'] + "Uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET'])
def index():
    return render_template("index.html")
@app.route('/',methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File Uploaded"
    else:
        return "Invalid File"

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)

@app.route("/test")
def test():
    return "<strong>It's Alive!</strong>"

if __name__ == '__main__':
    app.run(app.config['IP'], app.config['PORT'])


