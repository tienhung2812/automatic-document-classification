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


print("Getting files list...")
#Get file in business
bu = (glob.glob("data/bbc/business/*.txt"))

#Get file in entertainment
en = (glob.glob("data/bbc/entertainment/*.txt"))

#Get file in politics
po = (glob.glob("data/bbc/politics/*.txt"))

#Get file in sport
sp = (glob.glob("data/bbc/sport/*.txt"))

#Get file in tech
te = (glob.glob("data/bbc/tech/*.txt"))
category = []
filename =[]
title = []
content = []

def CreateData(cate):
    #Filter
    
    print("Creating "+cate+" data...")
    if(cate is 'business'):
        field = bu
    if(cate is 'entertainment'):
        field = en
    if(cate is 'politics'):
        field = po
    if(cate is 'sport'):
        field = sp
    if(cate is 'tech'):
        field = te
    for textfile in field:
        try :
            with open(textfile) as f:
                rawcontentarray = f.read().splitlines()
                rawcontent = ""
                title.append(rawcontentarray[0])
                for i in range(2,len(rawcontentarray)):
                    rawcontent+=rawcontentarray[i]
                content.append(rawcontent)
                category.append(cate)
                filename.append(textfile[textfile.rfind('/')+1:])
        except Exception as error:
            print(cate)
            print(rawcontentarray[0])
            print(textfile)
            print(rawcontent)
            print(filename[-1])
            print(title[-1])
            print(content[-1])
            print(error)

#main function
#Creating Data
CreateData("business")
CreateData("entertainment")
CreateData("politics")
CreateData("sport")
CreateData("tech")
print("Cate\tFile\tTitle\tContent")
print(str(len(category))+"\t"+str(len(filename))+"\t"+str(len(title))+"\t"+str(len(content)))

#check Data
if(len(category)==len(filename)==len(title)==len(content)):
    print("Create data successfully")
else:
    print("Number of data is not equal\n"+str(len(category))+"\t"+str(len(filename))+"\t"+str(len(title))+"\t"+str(len(content)))

#Importing data
print("Importing data...")
dataSet = list(zip(category,filename,title,content))
df = pd.DataFrame(data = dataSet, columns=['category', 'filename','title','content'])
print("Exporting data...")
df.to_csv('data.csv',index=False,header=True)
print("Done")

#Process Data
print("Process data...")
df['category_id'] = df['category'].factorize()[0]
category_id_df = df[['category', 'category_id']].drop_duplicates().sort_values('category_id')
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['category_id', 'category']].values)
print("5 sample data")
print(df.sample(5, random_state=0))
print(df.groupby('category').filename.count().plot.bar(ylim=0))
plt.show()

#Explore Data
print("Exploring data...")

##Create feature
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')

features = tfidf.fit_transform(df.content).toarray()
labels = df.category_id
features.shape
print("Doc\tFeatures")
print(str(len(labels))+"\t"+str(len(features)))


N = 3
for category, category_id in sorted(category_to_id.items()):
    features_chi2 = chi2(features, labels == category_id)
    indices = np.argsort(features_chi2[0])
    feature_names = np.array(tfidf.get_feature_names())[indices]
    unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
    bigrams = [v for v in feature_names if len(v.split(' ')) == 2]
    print("# '{}':".format(category))
    print("  . Most correlated unigrams:\n       . {}".format('\n       . '.join(unigrams[-N:])))
    print("  . Most correlated bigrams:\n       . {}".format('\n       . '.join(bigrams[-N:])))

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
plt.show()

print(df[df.title.str.contains('Arsenal')])

#Training

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

sns.boxplot(x='model_name', y='accuracy', data=cv_df)
sns.stripplot(x='model_name', y='accuracy', data=cv_df, 
              size=8, jitter=True, edgecolor="gray", linewidth=2)
sns.show()
print(cv_df.groupby('model_name').accuracy.mean())