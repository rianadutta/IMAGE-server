This preprocessor has been created in order to detect expressions of an individual person. The output generated by a preprocessor would be ```happy, neutral or sad.``` It is to be noted that AI models learn human biases reflected in the datasets, leading to incorrect predictions. For example, when a popular emotion recognition model was used on NBA players, the model detected that African-American players were twice as angry compared to their white counterparts \cite{rhue_2019}. Hence such models should be used with caution as it might lead to offensive results. 


In order to run the API as a docker container use the following commands: 

```docker build -t <image-name>```

```docker run --publish <port>:5000 <image-name>```
