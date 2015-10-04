import os
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory
from werkzeug import secure_filename
import cv2
import numpy
#from sklearn.decomposition import RandomizedPCA
from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score, KFold
from scipy.stats import sem
from sklearn import metrics

app = Flask(__name__)
app.config.from_pyfile('SkinDoc.cfg')
UPLOAD_FOLDER = "upload"#os.environ['OPENSHIFT_TMP_DIR']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

standardSize = (550, 360)
def LoadAllImages(FolderPath,LabelType,LabelArray,ImageArray):
    for filename in os.listdir(FolderPath):
        SingleImage = cv2.imread(os.path.join(FolderPath,filename))
        if SingleImage != None:
            #rows,cols,ch = SingleImage.shape
            #if rows > 430:
            #    RotationMatrix = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
            #    dst = cv2.warpAffine(SingleImage,RotationMatrix,(cols,rows))
            #    cv2.imshow(filename,dst)
            #    cv2.waitKey(0)
            #    cv2.destroyAllWindows()
            #images.append(SingleImage)
            #blur = cv2.blur(SingleImage,(30,30))
            greyImage = cv2.cvtColor(SingleImage, cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(greyImage,100,255,0)
            NumpyImage = numpy.array(thresh,'uint8')
            resized = cv2.resize(NumpyImage,standardSize)
            #equalized = cv2.equalizeHist(resized)
            ImageArray.append(FlattenImage(resized))
            LabelArray.append(LabelType)
            #print filename
    return {'ImageArray':ImageArray,'LabelArray':LabelArray}

def LoadPrediction(FolderPath):
    for filename in os.listdir(FolderPath):
        ImageArray = []
        SingleImage = cv2.imread(os.path.join(FolderPath,filename))
        if SingleImage != None:
            #rows,cols,ch = SingleImage.shape
            #if rows > 430:
            #    RotationMatrix = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
            #    dst = cv2.warpAffine(SingleImage,RotationMatrix,(cols,rows))
            #    cv2.imshow(filename,dst)
            #    cv2.waitKey(0)
            #    cv2.destroyAllWindows()
            #images.append(SingleImage)
            #blur = cv2.blur(SingleImage,(30,30))
            greyImage = cv2.cvtColor(SingleImage, cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(greyImage,100,255,0)
            NumpyImage = numpy.array(thresh,'uint8')
            resized = cv2.resize(NumpyImage,standardSize)
            #equalized = cv2.equalizeHist(resized)
            ImageArray.append(FlattenImage(resized))
             #print filename
    return ImageArray



def EvaluateCrossValidation(clf, X, y, K):
    crossValidation = KFold(len(y), K, shuffle=True, random_state=0)
    print X.shape
    print y.shape
    print y
    crossScores = cross_val_score(clf, X, y, cv=crossValidation)
    print (crossScores)
    print ("Mean score: {0:.3f} (+/-{1:.3f})".format(
        numpy.mean(crossScores), sem(crossScores)))

def FlattenImage(image):
    Length = image.shape[0] * image.shape[1]
    imageWide = image.reshape(1, Length)
    return imageWide[0]
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
        SingleImage = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if SingleImage != None:
            ImageArray = []
            #rows,cols,ch = SingleImage.shape
            #if rows > 430:
            #    RotationMatrix = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
            #    dst = cv2.warpAffine(SingleImage,RotationMatrix,(cols,rows))
            #    cv2.imshow(filename,dst)
            #    cv2.waitKey(0)
            #    cv2.destroyAllWindows()
            #images.append(SingleImage)
            #blur = cv2.blur(SingleImage,(30,30))
            greyImage = cv2.cvtColor(SingleImage, cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(greyImage,100,255,0)
            NumpyImage = numpy.array(thresh,'uint8')
            resized = cv2.resize(NumpyImage,standardSize)
            #equalized = cv2.equalizeHist(resized)
            ImageArray.append(FlattenImage(resized))
             #print filename
            images = []
            labels = []
            MelanomaOutput = LoadAllImages("SkinData/melanoma",1,labels,images)
            MArrayData = MelanomaOutput['ImageArray']
            MArrayLabel = MelanomaOutput['LabelArray']
            NotMelanomaOutput = LoadAllImages("SkinData/notmelanoma",0,MArrayLabel,MArrayData)
            NArrayData = numpy.array(NotMelanomaOutput['ImageArray'])
            NArrayLabel = numpy.array(NotMelanomaOutput['LabelArray'])
            svc_1 = SVC(kernel='linear')
            svc_1.fit(NArrayData,NArrayLabel)
            y_pred = svc_1.predict(numpy.array(ImageArray))
            print y_pred
            ResponseText = ""
            if y_pred.item(0) == 0:
                ResponseText = "This segment is normal/harmless"
            elif y_pred.item(0) == 1:
                ResponseText = "This segment is cancerous" 
            
            return render_template("Result.html",value=ResponseText)
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


