# -*- coding: utf-8 -*-
"""lungcancer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pqPFJWsT5WCJId07-iihEHD4AeHtZ-D1

**Gerekli Kütüphanelerin Kurulumu Gerçekleşti.**

> **pydicom**--> dcm dosyalarıyla işlem yapabilmemizi sağlar.


> **os-sys** --> dosyalara, klasörlere ve içeriklerine erişmemizi sağlar.
"""

pip install pydicom

pip install os-sys

"""Drive hesabını doğrulama ve drive'a yönlendirme yapıldı."""

from google.colab import drive
drive.mount('/content/drive/')

import os
os.chdir("/content/drive/My Drive")

"""csv dosyasındaki hasta bilgileri yazdırıldı."""

import pydicom
import numpy as np
import pandas as pd
import os
data_dir = './proje/stage1/' #dosya yolunu belirttim
patients = os.listdir(data_dir)
print(len(patients))
labels=pd.read_csv('./proje/stage1/stage1_labels.csv', index_col=0) #excel dosyasını okuyoruz
labels.head() #excel dosyasının ilk 5 kaydını yazdırdım

"""Röntgen görüntüleri listdir metoduyla listelendi ve değişkene atıldı."""

path = './proje/sample_images/'
patients = os.listdir(path) #  listdir kullnarak  dcm dosyalar listelendi
patients.sort() #dosyalar içinde sıralama yapıldı
print(patients[0])
print(len(patients))

"""Diziye dcm görüntüleri sırasıyla eklendi."""

lstFilesDCM = []  #boş bir liste oluşturuldu
say=0
for patient in patients:
#     label = labels_df.get_value(patient, 'cancer')
    for dirName, subdirList, fileList in os.walk(path + '/' + patient):
        for filename in fileList:
            if ".dcm" in filename.lower():  # dcm uzantılı olup olmadığı kontrol ettik
                lstFilesDCM.append(os.path.join(dirName,filename)) #dosya yoluyla dosyayı listeye ekliyor
                
                if (len(lstFilesDCM)) ==3500:
                  break
                #print(len(lstFilesDCM))
print("aşama tamamlandı")  
print(len(lstFilesDCM))

"""Boyut ayarlama resimleri yükleme  tip dönüşümü işlemleri yapıldı."""

import matplotlib.pyplot as plt
import pydicom as dicom

def load_images(file_path):
    
    slices = [dicom.read_file(s) for s in file_path] #dosyaları for döngüsüyle tek tek okuduk 
    slices.sort(key = lambda x: int(x.InstanceNumber)) # sort fonksiyonu sıralama yapar--
   #Lambda fonksiyonlarını, bir fonksiyonun işlevselliğine ihtiyaç duyduğumuz, ama konum olarak bir fonksiyon tanımlayamayacağımız veya fonksiyon tanımlamanın zor ya da meşakkatli olduğu durumlarda kullanabiliriz.
   
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2]) #gelen dcm resminin x,y,z koordinatlarında ayarlama yapıldı çıkan sonucun negatif olmasını engellemek için mutlak değeri alındı.
        
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation) # hata çıkarsa tek boyutlu çalışıyoruz görüntü düzleminden işleme alıyoruz
        

    for s in slices:
        s.SliceThickness = slice_thickness 
        #dcm dosyasının dilim kalınlığı atandı
    return slices #dcm dosylarını geri döndürüyoruz
    #print("işlem tamamlandı")

print("resimler dönüstürülmeye baslanıyor")
ornekdata=load_images(lstFilesDCM) #fonksiyona dcm dosyalarını yollandı
print("resimler dönüştürüldü")

with open("Sample_metadata.txt", 'w') as file_handler: #sample_metdata adında bir txte dosyasını açtık
    for item in ornekdata: #ornekdataların içindeki bilgileri txt dosyasına yazdık 
        file_handler.write("{}\n".format(item))
#dataların içideki bilgiler txt dosyasına yazdırıldı

def get_pixels_hu(scans):
    image = np.stack([s.pixel_array for s in scans]) #pixel_array dosyadak pixelleri okuyor ve stack fonksiyonu pixelleri birleştiriyor
  
    image = image.astype(np.int16) # resim tipini hata çıkmaması ve uyumlu olması için dönüştürdük.

    image[image == -2000] = 0
   
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope
    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)    
    image += np.int16(intercept)
    
    return np.array(image, dtype=np.int16)

imgs = get_pixels_hu(ornekdata)# fonksiyona dcm dosyalarını yolladık

output_path = "./Output"
if not os.path.exists(output_path):
    os.makedirs(output_path)
np.save(output_path + "fullimages.npy", imgs)

"""Dcm dosyalarını görüntülemek için işlemler yapıldı.

"""

plt.imshow(imgs[500], cmap='CMRmap') #matplotlible herhangi bir x-ray görüntüsünü görüntüledik.
plt.show()

def sample_stack(stack, rows=5, cols=5, start_with=500, show_every=10):
    fig,ax = plt.subplots(rows,cols,figsize=[8,8]) #subplots metodu ax değişkenine nesneleri doldurma görevinde kullanıldı nesne olarak döndürdü
    for i in range(rows*cols): 
        ind = start_with + i*show_every
        ax[int(i/rows),int(i % rows)].set_title('slice %d' % ind)
        ax[int(i/rows),int(i % rows)].imshow(stack[ind],cmap='CMRmap')
        ax[int(i/rows),int(i % rows)].axis('off')
    plt.show()
    
    
imgs_to_process = np.load(output_path + 'fullimages.npy')
sample_stack(imgs_to_process) # fonksiyona yollama yapıyoruz

"""Tekrar görtüler alınıp boyutları ve özellikleri değiştirildi."""

import numpy as np
import pandas as pd
import pydicom
import os
import matplotlib.pyplot as plt
import cv2
import math
##Setting x*y size to 50
size = 50

## Setting z-dimension (number of slices to 20)
NoSlices = 10


def chunks(l, n):

    count = 0
    for i in range(0, len(l), n):
        if (count < NoSlices):
            yield l[i:i + n]
            count = count + 1


def ortalama(l):
    return sum(l) / len(l)

def dataProcessing(patient, labels_df, size=150, noslices=20, visualize=False):
    print("fonksiyona girdi")
    label = labels_df._get_value(patient, 'cancer')
    path = './proje/sample_images/' + patient
    slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key=lambda x: int(x.ImagePositionPatient[2]))

    new_slices = []
    slices = [cv2.resize(np.array(each_slice.pixel_array), (size, size)) for each_slice in slices]

    chunk_sizes = math.floor(len(slices) / noslices)
    for slice_chunk in chunks(slices, chunk_sizes):
        slice_chunk = list(map(ortalama, zip(*slice_chunk)))
        new_slices.append(slice_chunk)

    if len(new_slices) == noslices-1:
        new_slices.append(new_slices[-1])

    if len(new_slices) == noslices-2:
        new_slices.append(new_slices[-1])
        new_slices.append(new_slices[-1])

    if len(new_slices) == noslices+2:
        new_val = list(map(mean, zip(*[new_slices[noslices-1],new_slices[noslices],])))
        del new_slices[noslices]
        new_slices[noslices-1] = new_val
        
    if len(new_slices) == noslices+1:
        new_val = list(map(mean, zip(*[new_slices[noslices-1],new_slices[noslices],])))
        del new_slices[no_slices]
        new_slices[noslices-1] = new_val

    if visualize:
        fig = plt.figure()
        for num,each_slice in enumerate(new_slices):
            y = fig.add_subplot(4,5,num+1)
            y.imshow(each_slice, cmap='gray')
        plt.show()


    if label == 1:
        label = np.array([0, 1])
    elif label == 0:
        label = np.array([1, 0])
    
    return np.array(new_slices), label


imageData = []
for num, patient in enumerate(patients):
    if num % 100 == 0:
        print('Saved -', num)
    try:
        img_data, label = dataProcessing(patient, labels, size=size, noslices=NoSlices)
        imageData.append([img_data, label,patient])
    except KeyError as e:
        print('data etiketsiz')
       

        
##sonuçlar numpy dosyasına kaydedildi
np.save('./Output/fullimages.npy'.format(size, size, NoSlices), imageData)

pip install tflearn

"""Gerekli kütüphaneler import edildi."""

import tensorflow as tf
import time
import pandas as pd
import tflearn
from tflearn.layers.conv import conv_3d, max_pool_3d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import numpy as np
import matplotlib.pyplot as plt

"""Train ve test dataları ayrıldı boyut ve her seferde kaç görüntünün döneceği ayarlandı."""

from tensorflow.keras.models import Sequential

imageData = np.load('./Output/fullimages.npy', allow_pickle=True)
trainingData = imageData[0:2000]
validationData = imageData[-500:]
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
x = tf.placeholder('float')
y = tf.placeholder('float')

size = 50
keep_rate = 0.8
NoSlices = 10

"""Ayrılan datalara derin öğrenme yöntemleri uygularak öğrenim gerçekleştirildi ve başarı ölçümü yapıldı."""

def convolution3d(x, W):

  return tf.nn.conv3d(x, W, strides=[1, 1, 1, 1, 1], padding='SAME')


def maxpooling3d(x):


  return tf.nn.max_pool3d(x, ksize=[1, 2, 2, 2, 1], strides=[1, 2, 2, 2, 1], padding='SAME')


def cnn(x):

  x = tf.reshape(x, shape=[-1, size, size, NoSlices, 1])
  convolution1 = tf.nn.relu(convolution3d(x, tf.Variable(tf.random_normal([3, 3, 3, 1, 32]))) + tf.Variable(tf.random_normal([32])))
  convolution1 = maxpooling3d(convolution1)
  convolution2 = tf.nn.relu(convolution3d(convolution1, tf.Variable(tf.random_normal([3, 3, 3, 32, 64]))) + tf.Variable(tf.random_normal([64])))
  convolution2 = maxpooling3d(convolution2)
  convolution3 = tf.nn.relu(convolution3d(convolution2, tf.Variable(tf.random_normal([3, 3, 3, 64, 128]))) + tf.Variable( tf.random_normal([128])))
  convolution3 = maxpooling3d(convolution3)
  convolution4 = tf.nn.relu(convolution3d(convolution3, tf.Variable(tf.random_normal([3, 3, 3, 128, 256]))) + tf.Variable( tf.random_normal([256])))
  convolution4 = maxpooling3d(convolution4)
  convolution5 = tf.nn.relu(convolution3d(convolution4, tf.Variable(tf.random_normal([3, 3, 3, 256, 512]))) + tf.Variable( tf.random_normal([512])))
  convolution5 = maxpooling3d(convolution4)
  fullyconnected = tf.reshape(convolution5, [-1, 1024])
  fullyconnected = tf.nn.relu(tf.matmul(fullyconnected, tf.Variable(tf.random_normal([1024, 1024]))) + tf.Variable(tf.random_normal([1024])))
  fullyconnected = tf.nn.dropout(fullyconnected, keep_rate)
  output = tf.matmul(fullyconnected, tf.Variable(tf.random_normal([1024, 2]))) + tf.Variable(tf.random_normal([2]))
  return output


def network(x):
  new_time = time.time()
  prediction = cnn(x)
  cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y))
  optimizer = tf.train.AdamOptimizer(learning_rate=1e-3).minimize(cost)
  epochs = 20
  with tf.Session() as session:
    session.run(tf.global_variables_initializer())
    for epoch in range(epochs):
      epoch_loss = 0
      for data in trainingData:
        X = data[0]
        Y = data[1]
        _, c = session.run([optimizer, cost], feed_dict={x: X, y: Y})
        epoch_loss += c
        

      correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y,1))
      accuracy = tf.reduce_mean(tf.cast(correct, 'float'))

     
      print('Epoch', epoch + 1, 'completed out of', epochs, 'loss:', epoch_loss)
      print('\tAccuracy:', accuracy.eval({x: [i[0] for i in validationData], y: [i[1] for i in validationData]}))
      print("\tLoss: " + str(epoch_loss))
      print("\tTime to complete: %s seconds." % (time.time() - new_time))
    print('Final Accuracy:', accuracy.eval({x: [i[0] for i in validationData], y: [i[1] for i in validationData]}))
 
    patients = []
    actual = []
    predicted = []

    finalprediction = tf.argmax(prediction, 1)
    actualprediction = tf.argmax(y, 1)
    for i in range(len(validationData)):

      patients.append(validationData[i][2])
    for i in finalprediction.eval({x: [i[0] for i in validationData], y: [i[1] for i in validationData]}):
      if(i==1):

        predicted.append("Cancer")
      else:
        predicted.append("No Cancer")
    for i in actualprediction.eval({x: [i[0] for i in validationData], y: [i[1] for i in validationData]}):

      if(i==1):
        actual.append("Cancer")
      else:
        actual.append("No Cancer")
    for i in range(len(patients)):
      print("Patient: ",patients[i])
      print("Actual: ", actual[i])
      print("Predcited: ", predicted[i])

    from sklearn.metrics import confusion_matrix
    y_actual = pd.Series( (actualprediction.eval({x: [i[0] for i in validationData], y: [i[1] for i in validationData]})), name='Actual')
    y_predicted = pd.Series((finalprediction.eval({x: [i[0] for i in validationData], y: [i[1] for i in validationData]})), name='Predicted')
    df_confusion = pd.crosstab(y_actual, y_predicted)
    print(df_confusion)
    plot_confusion_matrix(df_confusion)
    print(y_actual,y_predicted)
    print(confusion_matrix(y_actual, y_predicted))
    #print(actualprediction.eval({x:[i[0] for i in validationData], y:[i[1] for i in validationData]}))
    #print(finalprediction.eval({x:[i[0] for i in validationData], y:[i[1] for i in validationData]}))
                   
def plot_confusion_matrix(df_confusion, title='Confusion matrix', cmap=plt.cm.gray_r):\


  plt.matshow(df_confusion, cmap=cmap)  # imshow  
  plt.title(title)
  plt.colorbar()
  tick_marks = np.arange(len(df_confusion.columns))
  plt.xticks(tick_marks, df_confusion.columns, rotation=45)
  plt.yticks(tick_marks, df_confusion.index)
    
  plt.ylabel(df_confusion.index.name)
  plt.xlabel(df_confusion.columns.name)
  plt.show()

start_time = time.time()     
network(x)

"""Test datası belirlendi ve train datası ile öğrenme gerçekleştirip cancer ya da no cancer etiketi tahmini yapıldı."""

import tensorflow as tf
import pandas as pd
import tflearn
from tflearn.layers.conv import conv_3d, max_pool_3d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import numpy as np
import pandas as pde
import matplotlib.pyplot as plt

imageData = np.load('./Output/fullimages.npy', allow_pickle=True)
trainingData = imageData[1000:]
testData = imageData[-100:]

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
x = tf.placeholder('float')
y = tf.placeholder('float')
size = 50
keep_rate = 0.8
NoSlices = 10


def convolution3d(x, W):
    return tf.nn.conv3d(x, W, strides=[1, 1, 1, 1, 1], padding='SAME')


def maxpooling3d(x):
    return tf.nn.max_pool3d(x, ksize=[1, 2, 2, 2, 1], strides=[1, 2, 2, 2, 1], padding='SAME')


def cnn(x):
    x = tf.reshape(x, shape=[-1, size, size, NoSlices, 1])
    convolution1 = tf.nn.relu(
        convolution3d(x, tf.Variable(tf.random_normal([3, 3, 3, 1, 32]))) + tf.Variable(tf.random_normal([32])))
    convolution1 = maxpooling3d(convolution1)
    convolution2 = tf.nn.relu(
        convolution3d(convolution1, tf.Variable(tf.random_normal([3, 3, 3, 32, 64]))) + tf.Variable(
            tf.random_normal([64])))
    convolution2 = maxpooling3d(convolution2)
    convolution3 = tf.nn.relu(
        convolution3d(convolution2, tf.Variable(tf.random_normal([3, 3, 3, 64, 128]))) + tf.Variable(
            tf.random_normal([128])))
    convolution3 = maxpooling3d(convolution3)
    convolution4 = tf.nn.relu(
        convolution3d(convolution3, tf.Variable(tf.random_normal([3, 3, 3, 128, 256]))) + tf.Variable(
            tf.random_normal([256])))
    convolution4 = maxpooling3d(convolution4)
    convolution5 = tf.nn.relu(
        convolution3d(convolution4, tf.Variable(tf.random_normal([3, 3, 3, 256, 512]))) + tf.Variable(
            tf.random_normal([512])))
    convolution5 = maxpooling3d(convolution4)
    fullyconnected = tf.reshape(convolution5, [-1, 1024])
    fullyconnected = tf.nn.relu(
        tf.matmul(fullyconnected, tf.Variable(tf.random_normal([1024, 1024]))) + tf.Variable(tf.random_normal([1024])))
    fullyconnected = tf.nn.dropout(fullyconnected, keep_rate)
    output = tf.matmul(fullyconnected, tf.Variable(tf.random_normal([1024, 2]))) + tf.Variable(tf.random_normal([2]))
    return output


def network(x):
    prediction = cnn(x)
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y))
    optimizer = tf.train.AdamOptimizer(learning_rate=1e-3).minimize(cost)
    epochs = 10
    with tf.Session() as session:
        session.run(tf.global_variables_initializer())
        for epoch in range(epochs):
            epoch_loss = 0
            for data in trainingData:
                try:
                    X = data[0]
                    Y = data[1]
                    _, c = session.run([optimizer, cost], feed_dict={x: X, y: Y})
                    epoch_loss += c
                except Exception as e:
                    pass

        patients = []
        actual = []
        predicted = []

        finalprediction = tf.argmax(prediction, 1)
        actualprediction = tf.argmax(y, 1)
        for i in range(len(testData)):
            patients.append(testData[i][2])
        for i in finalprediction.eval({x: [i[0] for i in testData], y: [i[1] for i in testData]}):
            if(i==1):
                predicted.append("Cancer")
            else:
                predicted.append("No Cancer")

        for i in range(len(patients)):
            print("Patient: ",patients[i])
            print("Predicted: ", predicted[i])

     
network(x)