import zipfile
import urllib
import os
import spacy


class TargetClassifier(object):
    """
    TargetClassifier attempts to classify the input question into one of the topics
    """
    models = {}

    def __init__(self):
        """
        During initialization, spaCy models are loaded and kept ready for classifying a sentence to a topic
        """

        modelInfoFromEnv = os.environ['KATECHEO_NER']
        '''
        Parse the String in the environment variable.
        - Each model information is separated by ','
        - A specific model name and it's NER model location URL is separated by '='
        '''
        modelInfos = [
            sentence.split('=') for sentence in modelInfoFromEnv.split(',')
        ]

        self.models = {}

        # Iterate through each entry with the model information.
        for modelInfo in modelInfos:
            modelName = modelInfo[0]
            modelURL = modelInfo[1]

            # Download the model
            modelRootDirectory = "./" + modelName

            # Check if the model files already exists.
            if modelName not in os.listdir("."):
                urllib.request.urlretrieve(modelURL, modelName + ".zip")
                zipRef = zipfile.ZipFile(modelName + ".zip", 'r')
                zipRef.extractall(modelRootDirectory)
                zipRef.close()

            # Get the internal directory of the NER model.
            modelMainDirectory = os.listdir('./' + modelName)[0]

            # Check if the model directory has been downloaded.
            if modelMainDirectory:

                # Load the spaCy models.
                self.models[modelName] = spacy.load(
                    os.path.join(modelRootDirectory, modelMainDirectory))


    def predict(self, X, feature_names, meta):
        """
        Returns the search string and topic to which it was classified

        Parameters
        ----------
        X : array-like
        feature_names : array of feature names (optional)
        """

        # logic from parent
        if 'tags' in meta and 'proceed' in meta['tags'] and meta['tags']['proceed']:

            topicName = ""
            matchedEntities = []

            # Get the text string that is to be classified.
            messageText = str(X[0])

            # Iterate through all the models
            for topic, model in self.models.items():

                # Get the inference result from the NER model for a question.
                doc = model(messageText)

                # Check if the model has recognised the trained entities in the question.
                if doc.ents:
                    topicName = topic
                    matchedEntities.append(doc.ents)

            # TODO: List out all the topics with a percentage of the match confidence.
            # Currently we would like to return classification result
            # only if it matches a single topic.
            if len(matchedEntities) == 1:
                self.result = {'proceed': True}
                self.result['topic'] = topicName
                return X
            else:
                self.result = {'proceed': False}
                self.result['point_of_failure'] = 'No Matching Topic'
                return X

        else:
            self.result = meta['tags']
            return X

    def tags(self):
        return self.result
