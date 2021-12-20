# CCUnet
An end-to-end image translation model with weight-map for color constancy

## 1. Download the dataset (take Colorchecker_recommended dataset as an example)

Place [RCC dataset](http://colorconstancy.com/evaluation/datasets/) in this  directory: 

```
./datasets/ColorChecker_ Recommended
```

![image-20210811123152958](readmepic\image-20210811123152958.png)

Place the mask image data in this directory:

```
./datasets/masks
```

![image-20210811123212246](readmepic\image-20210811123212246.png)

## 2. Install required toolkits

The program needs to use tensorflow and opencv toolkit. It is recommended to install in the **conda environment**.

And here we create a new conda environment as follow:

![image-20210811122116563](readmepic\image-20210811122116563.png)

Install the latest version of `tensorflow-gpu` using the following command:

```
conda install tensorflow-gpu
```

![image-20210811122257651](readmepic\image-20210811122257651.png)

install `opencv`:

```
pip install opencv-python
```

![image-20210811122446660](readmepic\image-20210811122446660.png)

## 3. Training and testing

Enter the folder where CCUnet.py and dataset are located, and use the following command under the created conda environment to start training:

```
python CCUnet.py fold1
```

Here `fold1` means that it is the first fold of the dataset used for this training, and can be replaced by `fold2` or `fold3`, which means the second or the third fold used for training.

![image-20210811123617043](readmepic\image-20210811123617043.png)

After each epoch of training, the testing process is automatically executed.

### 4. Training and testing results

The `train` folder is used to save the image results during the training process.

![image-20210811125431864](readmepic\image-20210811125431864.png)

The `test` folder is used to save the image results during the testing process.

![image-20210811124041686](readmepic\image-20210811124041686.png)

The `model` folder is used to save the network model which achieves the best results.

![image-20210811124254944](readmepic\image-20210811124254944.png)

And `records.txt` is the log file, which records the results of the experiment.

![image-20210811124356113](readmepic\image-20210811124356113.png)

