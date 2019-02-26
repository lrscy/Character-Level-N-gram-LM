# Character Level N-gram LM

A Character-Level N-gram Language Model implemented by Python 3.

## Environment

[Python 3](https://www.python.org/downloads/)

## Usage

It can run in shell or command line by inputing "python lm.py". Detailed usage can be seen in shell or command line by inputing "python lm.py -h".

If you want to call functions in this code, parameters description and notes in code are all good reference.

### Note

In linear interplotation smoothing function, it rebuilds its own language model since it needs to do grid search based on training data.

Sample training data, test data, pre-trained language model data are all included in corresponding folders.

## Parameters

The following is about parameters of each function. If you want to call them in python code, you can find details here.

To build a character-level language model:

```python
buildLM( trainDataPath, encoding, savePath, ratio )
```
* trainDataPath: the path contains all train data. Default is "./train".
* encoding: the encoding of files in traindDataPath. Default is "Latin-1".
* savePath: the path to save language model. Default is "./lm".
* ratio: the propotion of real train files in trainingDataPath, others would be used as held-out data. Default value is 1.0, which means all files in trainDataPath would be used as real train data.

To apply linear interplotation smoothing function on language model:
```python
interplotationPPW( trainDataPath, encoding, savePath, testDataPath, ratio )
```
* trainDataPath: the path contains all train data. Default is "./train".
* encoding: the encoding of files in traindDataPath. Default is "Latin-1".
* savePath: the path to save language model. Default is "./save".
* testDataPath: the path contains all test data. Default is "./test".
* ratio: the propotion of real train files in trainDataPath, others would be used as held-out data. Default is 1.

To apply add-lambda smoothing function on language model:
```python
addLambdaPPW( lmPath, encoding, savePath, testDataPath )
```
* lmPath: the path contains all language model data. Default is "./lm".
* encoding: the encoding of files in lmPath. Default is "Latin-1".
* savePath: the path to save language model. Default is "./save".
* testDataPath: the path contains all test data. Default is "./test".

## Contributor

**Ruosen Li** | Master student | College of Engineering | Northeastern University
