import glob
from pandas import DataFrame, read_csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2
from sklearn.manifold import TSNE
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import sys
from datetime import datetime






class ADC:
    def CreateData(self,cate):
        #Filter
        print("Creating "+cate+" data...")
        if(cate is 'business'):
            field = self.bu
        if(cate is 'entertainment'):
            field = self.en
        if(cate is 'politics'):
            field = self.po
        if(cate is 'sport'):
            field = self.sp
        if(cate is 'tech'):
            field = self.te
        for textfile in field:
            try :
                with open(textfile) as f:
                    rawcontentarray = f.read().splitlines()
                    rawcontent = ""
                    self.title.append(rawcontentarray[0])
                    for i in range(2,len(rawcontentarray)):
                        rawcontent+=rawcontentarray[i]
                    self.content.append(rawcontent)
                    self.category.append(cate)
                    self.filename.append(textfile[textfile.rfind('/')+1:])
            except Exception as error:
                print(error)

    def __init__(self):
        start = datetime.now()
        
        import pandas as pd
        import glob
        print("Getting files list...")
        #Get file in business
        self.bu = (glob.glob("data/bbc/business/*.txt"))

        #Get file in entertainment
        self.en = (glob.glob("data/bbc/entertainment/*.txt"))

        #Get file in politics
        self.po = (glob.glob("data/bbc/politics/*.txt"))

        #Get file in sport
        self.sp = (glob.glob("data/bbc/sport/*.txt"))

        #Get file in tech
        self.te = (glob.glob("data/bbc/tech/*.txt"))
        self.category = []
        self.filename =[]
        self.title = []
        self.content = []
        # category = []
        # filename =[]
        # title = []
        # content = []

        

        #main function
        #Creating Data
        self.CreateData("business")
        self.CreateData("entertainment")
        self.CreateData("politics")
        self.CreateData("sport")
        self.CreateData("tech")
        print("Cate\tFile\tTitle\tContent")
        print(str(len(self.category))+"\t"+str(len(self.filename))+"\t"+str(len(self.title))+"\t"+str(len(self.content)))

        #check Data
        if(len(self.category)==len(self.filename)==len(self.title)==len(self.content)):
            print("Create data successfully")
        else:
            print("Number of data is not equal\n"+str(len(self.category))+"\t"+str(len(self.filename))+"\t"+str(len(self.title))+"\t"+str(len(self.content)))

        #Importing data
        print("Importing data...")
        dataSet = list(zip(self.category,self.filename,self.title,self.content))
        df = pd.DataFrame(data = dataSet, columns=['category', 'filename','title','content'])
        print("Exporting data...")
        df.to_csv('data.csv',index=False,header=True)
        print("Done")

        createdatatime = datetime.now()-start

        df['category_id'] = df['category'].factorize()[0]

        category_id_df = df[['category', 'category_id']].drop_duplicates().sort_values('category_id')
        category_to_id = dict(category_id_df.values)
        self.id_to_category = dict(category_id_df[['category_id', 'category']].values)

        df.sample(5, random_state=0)

        df.groupby('category').filename.count().plot.bar(ylim=0)


        from sklearn.feature_extraction.text import TfidfVectorizer

        self.tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')

        features = self.tfidf.fit_transform(df.content).toarray()
        labels = df.category_id
        features.shape


        from sklearn.feature_selection import chi2
        import numpy as np

        N = 3
        for category, category_id in sorted(category_to_id.items()):
            features_chi2 = chi2(features, labels == category_id)
            indices = np.argsort(features_chi2[0])
            feature_names = np.array(self.tfidf.get_feature_names())[indices]
            unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
            bigrams = [v for v in feature_names if len(v.split(' ')) == 2]
            print("# '{}':".format(category))
            print("  . Most correlated unigrams:\n       . {}".format('\n       . '.join(unigrams[-N:])))
            print("  . Most correlated bigrams:\n       . {}".format('\n       . '.join(bigrams[-N:])))


        from sklearn.manifold import TSNE
        import matplotlib.pyplot as plt
        # Sampling a subset of our dataset because t-SNE is computationally expensive
        SAMPLE_SIZE = int(len(features) * 0.3)
        np.random.seed(0)
        indices = np.random.choice(range(len(features)), size=SAMPLE_SIZE, replace=False)
        projected_features = TSNE(n_components=2, random_state=0).fit_transform(features[indices])
        colors = ['pink', 'green', 'midnightblue', 'orange', 'darkgrey']
        for category, category_id in sorted(category_to_id.items()):
            points = projected_features[(labels[indices] == category_id).values]
            plt.scatter(points[:, 0], points[:, 1], s=30, c=colors[category_id], label=category)
        plt.title("tf-idf feature vector for each article, projected on 2 dimensions.",
                fontdict=dict(fontsize=15))
        plt.legend()


        df[df.title.str.contains('Arsenal')]

        dataexplorationtime = datetime.now()- createdatatime -start
        

        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.naive_bayes import MultinomialNB

        from sklearn.model_selection import cross_val_score


        models = [
            RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
            MultinomialNB(),
            LogisticRegression(random_state=0),
        ]
        CV = 5
        cv_df = pd.DataFrame(index=range(CV * len(models)))
        entries = []
        for model in models:
            model_name = model.__class__.__name__
            accuracies = cross_val_score(model, features, labels, scoring='accuracy', cv=CV)
        for fold_idx, accuracy in enumerate(accuracies):
            entries.append((model_name, fold_idx, accuracy))
        cv_df = pd.DataFrame(entries, columns=['model_name', 'fold_idx', 'accuracy'])

        import seaborn as sns
        sns.boxplot(x='model_name', y='accuracy', data=cv_df)
        sns.stripplot(x='model_name', y='accuracy', data=cv_df, 
                    size=8, jitter=True, edgecolor="gray", linewidth=2)

        cv_df.groupby('model_name').accuracy.mean()


        from sklearn.model_selection import train_test_split

        self.model = LogisticRegression(random_state=0)

        X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(features, labels, df.index, test_size=0.33, random_state=0)
        self.model.fit(X_train, y_train)
        y_pred_proba = self.model.predict_proba(X_test)
        y_pred = self.model.predict(X_test)

        from sklearn.metrics import confusion_matrix
        import seaborn as sns

        conf_mat = confusion_matrix(y_test, y_pred)
        sns.heatmap(conf_mat, annot=True, fmt='d',
                    xticklabels=category_id_df.category.values, yticklabels=category_id_df.category.values)
        plt.ylabel('Actual')
        plt.xlabel('Predicted')

        from IPython.display import display

        for predicted in category_id_df.category_id:
            for actual in category_id_df.category_id:
                if predicted != actual and conf_mat[actual, predicted] >= 2:
                    print("'{}' predicted as '{}' : {} examples.".format(self.id_to_category[actual], self.id_to_category[predicted], conf_mat[actual, predicted]))
                    display(df.loc[indices_test[(y_test == actual) & (y_pred == predicted)]][['title', 'content']])
                    print('')

        

        self.model.fit(features, labels)

        from sklearn.feature_selection import chi2

        N = 5
        for category, category_id in sorted(category_to_id.items()):
            indices = np.argsort(self.model.coef_[category_id])
            feature_names = np.array(self.tfidf.get_feature_names())[indices]
            unigrams = [v for v in reversed(feature_names) if len(v.split(' ')) == 1][:N]
            bigrams = [v for v in reversed(feature_names) if len(v.split(' ')) == 2][:N]
            print("# '{}':".format(category))
            print("  . Top unigrams:\n       . {}".format('\n       . '.join(unigrams)))
            print("  . Top bigrams:\n       . {}".format('\n       . '.join(bigrams)))

        
        trainingtime = datetime.now()-createdatatime-dataexplorationtime-start
        df[df.content.str.lower().str.contains('news website')].category.value_counts()

        
    def Predict(self,raw_text):
        given_text=[raw_text]
        text_features = self.tfidf.transform(given_text)
        predictions = self.model.predict(text_features)
        for text, predicted in zip(given_text, predictions):
            # print('"{}"'.format(text))
            # print("  - Predicted as: '{}'".format(self.id_to_category[predicted]))
            # print("")
            return self.id_to_category[predicted]
    