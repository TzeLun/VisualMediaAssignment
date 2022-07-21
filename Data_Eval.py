from tensorflow.keras.losses import mean_absolute_error
from PIL import Image
import os.path
from tensorflow import image
import numpy as np


# The L1 loss function
def l1_loss(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    loss = mae * len(y_true)
    print("MAE loss :", mae)
    return loss


# Need to rework
def evaluate(model, x_test, y_test):
    avg_loss = 0
    for i, im in enumerate(x_test):
        inputim = []
        output = []
        inputim.append(im)
        output.append(y_test[i])
        print(np.array(inputim).shape)
        print(np.array(output).shape)
        y_pred = model.predict(np.array(inputim))
        avg_loss = avg_loss + l1_loss(np.array(output), y_pred)
    return avg_loss


# 2D PSNR for images
def PSNR(y_pred, y_true, max_val):
    # For array of images, (no. of image, w, h, d), calculate avg psnr
    if len(y_pred.shape) == 4:
        psnr = 0
        for ind in range(len(y_pred)):
            psnr = psnr + image.psnr(y_pred[ind], y_true[ind], max_val=max_val)
        return psnr
    elif len(y_pred.shape) == 3:
        return image.psnr(y_pred, y_true, max_val=max_val)


# re-crop all the images given a size in the folder
# Crop window is always at the center of the image
def crop(path_for_convert, path_to_save, size):
    directory = os.listdir(path_for_convert)
    for item in directory:
        filepath = os.path.join(path_for_convert, item)
        name, _ = os.path.splitext(item)
        if os.path.isfile(filepath):
            im = Image.open(filepath)
            w, h = im.size
            cim = im.crop((w/2-size[0]/2, h/2-size[1]/2, w/2+size[0]/2, h/2+size[1]/2))
            cim.save(path_to_save + name + ".PNG")


# converting image to numpy array. One folder one array
def images_to_array(path_to_dataset):
    img_array = []
    directory = os.listdir(path_to_dataset)
    for item in directory:
        filepath = os.path.join(path_to_dataset, item)
        if os.path.isfile(filepath):
            im = Image.open(filepath).convert('RGB')
            im = np.array(im)
            im = im.astype('float32')
            img_array.append(im)
    return np.array(img_array)


# Umbrella function to process all the dataset into usable numpy array
# The argument "path_list", is the list containing the path to all dataset:
# The order of the path is as follow:
# path first three: x_train, x_test, x_valid
# path last half: y_train, y_test, y_valid
def makeDataset(path_list):
    data = []
    for directory in path_list:
        data.append(images_to_array(directory))
    return data


# Upscaling the LR image to its HR counterpart using bicubic interpolation
def Bicubic_LR_to_HR(path_for_convert, path_to_save, sf=1):
    directory = os.listdir(path_for_convert)
    for item in directory:
        filepath = os.path.join(path_for_convert, item)
        name, _ = os.path.splitext(item)
        if os.path.isfile(filepath):
            im = Image.open(filepath)
            w, h = im.size
            cim = im.resize((w * sf, h * sf), Image.BICUBIC)
            cim.save(path_to_save + name + "Scaledx" + str(sf) + ".PNG")


# Use the model to improve the resolution of the input LR image
# Input type should have the shape (None, h, w, c): [img]
# Can accept batches: [img1, img2, img3, ... ]
def LR_to_HR_transform(model, data):
    output = []
    for img in data:
        im = list()
        im.append(img)
        output.append(model.predict(np.array(im)))
    return np.array(output)


# Restore the image pixels of the normalized image data, returns numpy array of unit8 [0 255]
def restoreIMAGE(data):
    output = []
    for im in data:
        im = im[0]
        im = im.astype(np.uint8)
        output.append(im)
    return np.array(output)


# Save the image tensor into png file in batches
def saveIMAGE(path_to_save, data):
    for i, im in enumerate(data):
        im = im[0]
        im = im.astype(np.uint8)
        img = Image.fromarray(im, 'RGB')
        img.save(path_to_save + "PIL_IMG_" + str(i + 1) + ".PNG")

