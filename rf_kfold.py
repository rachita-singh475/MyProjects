# -*- coding: utf-8 -*-
"""rf+single_image-2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iZsuxqimuB261FXtqykpPkept7ITPcTc
"""


import sys 
import numpy as np
import cv2
import pandas as pd
import os
import tensorflow 
from sklearn.model_selection import cross_validate 
#matplotlib.use('Agg')
DIR=str(sys.argv[1])



#checking that data between mask and image path matches correctly 

train_image_path =  '/data/all_images'
train_mask_path= '/data/all_labels'

check_image_array=[]
check_mask_array= []
for image in sorted(os.listdir(DIR + train_image_path)):
  check_image_array.append(image)
for mask in sorted(os.listdir(DIR+ train_mask_path)): 
  check_mask_array.append(mask)

print (len(check_image_array), len(check_mask_array))
print (check_image_array==check_mask_array)
check_image_array=np.asarray(check_image_array)
check_mask_array=np.asarray(check_mask_array)
print (check_image_array)
print (check_mask_array)

def get_pixel(img, center, x, y):
      
    new_value = 0
      
    try:
        # If local neighbourhood pixel 
        # value is greater than or equal
        # to center pixel values then 
        # set it to 1
        if img[x][y] >= center:
            new_value = 1
              
    except:
        # Exception is required when 
        # neighbourhood value of a center
        # pixel value is null i.e. values
        # present at boundaries.
        pass
      
    return new_value
   
# Function for calculating LBP
def lbp_calculated_pixel(img, x, y):
   
    center = img[x][y]
   
    val_ar = []
      
    # top_left
    val_ar.append(get_pixel(img, center, x-1, y-1))
      
    # top
    val_ar.append(get_pixel(img, center, x-1, y))
      
    # top_right
    val_ar.append(get_pixel(img, center, x-1, y + 1))
      
    # right
    val_ar.append(get_pixel(img, center, x, y + 1))
      
    # bottom_right
    val_ar.append(get_pixel(img, center, x + 1, y + 1))
      
    # bottom
    val_ar.append(get_pixel(img, center, x + 1, y))
      
    # bottom_left
    val_ar.append(get_pixel(img, center, x + 1, y-1))
      
    # left
    val_ar.append(get_pixel(img, center, x, y-1))
       
    # Now, we need to convert binary
    # values to decimal
    power_val = [1, 2, 4, 8, 16, 32, 64, 128]
   
    val = 0
      
    for i in range(len(val_ar)):
        val += val_ar[i] * power_val[i]
          
    return val

def fast_glcm(img, vmin=0, vmax=255, nbit=8, kernel_size=5):
    mi, ma = vmin, vmax
    ks = kernel_size
    h,w = img.shape

    # digitize
    bins = np.linspace(mi, ma+1, nbit+1)
    gl1 = np.digitize(img, bins) - 1
    gl2 = np.append(gl1[:,1:], gl1[:,-1:], axis=1)

    # make glcm
    glcm = np.zeros((nbit, nbit, h, w), dtype=np.uint8)
    for i in range(nbit):
        for j in range(nbit):
            mask = ((gl1==i) & (gl2==j))
            glcm[i,j, mask] = 1

    kernel = np.ones((ks, ks), dtype=np.uint8)
    for i in range(nbit):
        for j in range(nbit):
            glcm[i,j] = cv2.filter2D(glcm[i,j], -1, kernel)

    glcm = glcm.astype(np.float32)
    return glcm

def feature_extraction(img):
    df = pd.DataFrame()
    pixel_values = img.reshape(-1)
    df['Pixel_Value'] = pixel_values
    df['Image_Name'] = image  


# #Generate Gabor features
    num = 1  #To count numbers up in order to give Gabor features a lable in the data frame
    kernels = []
    for theta in range(2):   #Define number of thetas
        theta = theta / 4. * np.pi
        for sigma in (1, 3):  #Sigma with 1 and 3
            for lamda in np.arange(0, np.pi, np.pi / 4):   #Range of wavelengths
                for gamma in (0.05, 0.5):   #Gamma values of 0.05 and 0.5
                    gabor_label = 'Gabor' + str(num)  #Label Gabor columns as Gabor1, Gabor2, etc.
#                print(gabor_label)
                    ksize=9
                    kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta, lamda, gamma, 0, ktype=cv2.CV_32F)    
                    kernels.append(kernel)
                  #Now filter the image and add values to a new column 
                    fimg = cv2.filter2D(img, cv2.CV_8UC3, kernel)
                    filtered_img = fimg.reshape(-1)
                    df[gabor_label] = filtered_img  #Labels columns as Gabor1, Gabor2, etc.
                  #print(gabor_label, ': theta=', theta, ': sigma=', sigma, ': lamda=', lamda, ': gamma=', gamma)
                    num += 1  #Increment for gabor column label                
#CANNY EDGE
    edges = cv2.Canny(img, 100,200)   #Image, min and max values
    edges1 = edges.reshape(-1)
    df['Canny Edge'] = edges1 #Add column to original dataframe

    from skimage.filters import roberts, sobel, scharr, prewitt

#ROBERTS EDGE
    edge_roberts = roberts(img)
    edge_roberts1 = edge_roberts.reshape(-1)
    df['Roberts'] = edge_roberts1

#SOBEL
    edge_sobel = sobel(img)
    edge_sobel1 = edge_sobel.reshape(-1)
    df['Sobel'] = edge_sobel1

#SCHARR
    edge_scharr = scharr(img)
    edge_scharr1 = edge_scharr.reshape(-1)
    df['Scharr'] = edge_scharr1

#PREWITT
    edge_prewitt = prewitt(img)
    edge_prewitt1 = edge_prewitt.reshape(-1)
    df['Prewitt'] = edge_prewitt1

#GAUSSIAN with sigma=3
    from scipy import ndimage as nd
    gaussian_img = nd.gaussian_filter(img, sigma=3)
    gaussian_img1 = gaussian_img.reshape(-1)
    df['Gaussian s3'] = gaussian_img1

#GAUSSIAN with sigma=7
    gaussian_img2 = nd.gaussian_filter(img, sigma=7)
    gaussian_img3 = gaussian_img2.reshape(-1)
    df['Gaussian s7'] = gaussian_img3

#MEDIAN with sigma=3
    median_img = nd.median_filter(img, size=3)
    median_img1 = median_img.reshape(-1)
    df['Median s3'] = median_img1

#LBP  
    from skimage.feature import local_binary_pattern
    METHOD= 'uniform'
    radius = 3
    n_points = 8 * radius
    img_lbp = np.zeros((256, 256),np.uint8)
    #for i in range(0, 256):
        #for j in range(0, 256):
          #img_lbp[i, j] = lbp_calculated_pixel(img, i, j)
    lb = local_binary_pattern(img, n_points, radius, METHOD)
    img_lbp= lb.ravel()
    df['Local Binary Pattern'] = img_lbp

    return df

image_dataset = pd.DataFrame()  #Dataframe to capture image features
print (image_dataset)
for image in sorted (os.listdir(DIR + train_image_path)):
  single_train_image_path = (os.path.join(DIR+ train_image_path,image))
  img = cv2.imread(single_train_image_path)
  img = cv2.resize(img, (256,256),interpolation = cv2.INTER_NEAREST)
  img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  
  # #Call the feature extraction function.
  df_train_images = feature_extraction(img)
  image_dataset = image_dataset.append(df_train_images)

print (image_dataset)
#
mask_dataset = pd.DataFrame() 
for mask in sorted (os.listdir(DIR + train_mask_path)):
    single_train_mask_path = (os.path.join(DIR + train_mask_path,mask))
    df2 = pd.DataFrame()
    label = cv2.imread(single_train_mask_path) 
    label = cv2.resize(label, (256,256),interpolation = cv2.INTER_NEAREST)
    label = cv2.cvtColor(label,cv2.COLOR_BGR2GRAY)

#  #Add pixel values to the data frame
    label_values = label.reshape(-1)
    df2['Label_Value'] = label_values
    df2['Mask_Name'] = mask  
    mask_dataset = mask_dataset.append(df2)  #Update mask dataframe with all the info from each mask

print (image_dataset)
print (mask_dataset)
dataset = pd.concat([image_dataset, mask_dataset], axis=1)    #Concatenate both image and mask datasets

#If you expect image and mask names to be the same this is where we can perform sanity check
dataset['Image_Name'].equals(dataset['Mask_Name'])   
##


#Assign training features to X and labels to Y
#Drop columns that are not relevant for training (non-features)
X = dataset.drop(labels = ["Image_Name", "Mask_Name", "Label_Value"], axis=1) 


print (X)

#Assign label values to Y (our prediction)
Y = dataset["Label_Value"]
print(Y.value_counts()) #prints counts 
Y=Y.values

 #Encode Y values to 0, 1, 2, 3, .... (NOt necessary but makes it easy to use other tools like ROC plots)
from sklearn.preprocessing import LabelEncoder
Y = LabelEncoder().fit_transform(Y)
print (np.unique(Y))
Y= pd.DataFrame(Y,columns=["Label_Value"])
print (Y)


## Instantiate model with n number of decision trees
#model = BalancedRandomForestClassifier(n_estimators = 100, criterion= 'entropy', max_features= 0.4, random_state=42)

#model = RandomForestClassifier(n_estimators = 1200,min_samples_split=2,min_samples_leaf=4,max_features='auto',max_depth=100,bootstrap=True,  n_jobs=-1, criterion= 'entropy', random_state=42)

from sklearn.model_selection import RandomizedSearchCV
# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}

#forest = RandomForestClassifier()
#rf_random = RandomizedSearchCV(estimator = forest , param_distributions = random_grid, n_iter = 10, cv = 3, verbose=2, random_state=42, n_jobs = -1)
#rf_random.fit(X,Y)
#print(rf_random.best_params_)

#hyperF = dict(n_estimators = n_estimators, max_depth = max_depth,  
#              min_samples_split = min_samples_split, 
#             min_samples_leaf = min_samples_leaf)
#
#from sklearn.model_selection import GridSearchCV
#forest= RandomForestClassifier()
#gridF = GridSearchCV(forest, hyperF, cv = 3, verbose = 1, 
#                      n_jobs = -1)
#bestF = gridF.fit(X, Y)
#print (bestF)
#
#
#model.fit(X, Y)

## Train the model on training data

#feature_list = list(X.columns)
#feature_imp = pd.Series(model.feature_importances_,index=feature_list).sort_values(ascending=False)
#print(feature_imp)

import pickle
from sklearn.metrics import confusion_matrix
from sklearn.metrics import jaccard_score
from imblearn.over_sampling import SMOTE, ADASYN
X_for_RF_ADASYN_kfold, Y_for_RF_ADASYN_kfold = ADASYN(random_state=42).fit_resample(X, Y)
X_for_RF_ADASYN_kfold.to_pickle('X_for_RF_ADASYN_kfold.pkl')    #to save the dataframe, df to 123.pkl
Y_for_RF_ADASYN_kfold.to_pickle('Y_for_RF_ADASYN_kfold.pkl')
X_for_RF_ADASYN= pd.read_pickle('X_for_RF_ADASYN_kfold.pkl')
Y_for_RF_ADASYN= pd.read_pickle('Y_for_RF_ADASYN_kfold.pkl')
X_for_RF_ADASYN = np.asarray(X_for_RF_ADASYN)
Y_for_RF_ADASYN = np.asarray(Y_for_RF_ADASYN)

from tensorflow.keras.metrics import MeanIoU
from sklearn.model_selection import StratifiedKFold
num_classes = 3
kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=123) 
for train_index,test_index in kf.split(X_for_RF_ADASYN, Y_for_RF_ADASYN):
    print ("train index is:", train_index)
    print ("test index is:", test_index)
    X_train, X_test = X_for_RF_ADASYN[train_index], X_for_RF_ADASYN[test_index]
    print ("X train shape is:", X_train.shape)
    y_train, y_test = Y_for_RF_ADASYN[train_index], Y_for_RF_ADASYN[test_index]
    print ("Y train shape is:", y_train.shape)
    assert X_train != X_test
    RF_ADASYN_model = RandomForestClassifier(n_estimators = 1200,min_samples_split=2,min_samples_leaf=6,max_features='auto',max_depth=75,bootstrap=True,  n_jobs=-1, criterion= 'entropy', random_state=42)
    RF_ADASYN_model.fit(X_train, y_train)
    result = RF_ADASYN_model.predict(X_test)
    ADASYN_jaccard=jaccard_score(y_test, result, average = 'macro')
    print("ADASYN jaccard: ", ADASYN_jaccard)
    IOU_ADASYN = tensorflow.keras.metrics.MeanIoU(num_classes=num_classes)
    IOU_ADASYN.update_state(y_test, result)
    print(IOU_ADASYN.result().numpy())
    values = np.array(IOU_ADASYN.get_weights()).reshape(num_classes, num_classes)
    print(values)
    class1_IoU = values[0,0]/(values[0,0] + values[0,1] + values[0,2]  + values[1,0]+ values[2,0])
    class2_IoU = values[1,1]/(values[1,1] + values[1,0] + values[1,2]  + values[0,1]+ values[2,1])
    class3_IoU = values[2,2]/(values[2,2] + values[2,0] + values[2,1] + values[0,2]+ values[1,2])
    print("IoU for class 0 is: ", class1_IoU)
    print("IoU for class 1 is: ", class2_IoU)
    print("IoU for class 2 is: ", class3_IoU)


# -*- coding: utf-8 -*-
