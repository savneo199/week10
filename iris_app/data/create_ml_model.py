from pathlib import Path
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import pickle


def create_model(df, alg, pickle_file):
    """Creates a model using the algorithm provided. Output serialised using pickle.

    To make a prediction with the model:
    prediction = model.predict(
        [[sepal_length, sepal_width, petal_length, petal_width]])
    e.g. p = model.predict([[5.1,3.5,1.4,0.2]])
    To access the prediction value use p[0]

    Args:
    df:DataFrame DataFrame containing the iris data
    alg:skickit-learn model object
    pickle_file:output file name and location

    Returns:
    .pkl Pickled model

    """

    # Convert categorical data to numeric
    le = LabelEncoder()
    df["species"] = le.fit_transform(df["species"])

    # X = feature values (case sepal length, sepal width, petal length, petal width)
    X = df.iloc[:, 0:-1]
    X = X.values
    # y = target values, last column of the data frame
    y = df.iloc[:, -1]

    # Split the data into 80% training and 20% testing (type of iris)
    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Initialize the model
    model = alg
    # Train the model
    model.fit(x_train, y_train)

    print("Accuracy: ", model.score(x_test, y_test) * 100)

    # Test the model
    # Call the .predict() function of the model and feed in the testing data
    predictions = model.predict(x_test)
    print(classification_report(y_test, predictions))
    print(accuracy_score(y_test, predictions))

    # Pickle the model and save to the data folder
    pickle.dump(model, open(pickle_file, "wb"))


def main():
    """Create the models and serialise them."""
    iris_file = Path(__file__).parent.joinpath("iris.csv")
    iris_data = pd.read_csv(iris_file)

    model_dt = DecisionTreeClassifier()
    model_lr = LogisticRegression()

    pickle_file_dt = Path(__file__).parent.joinpath("model_dt.pkl")
    pickle_file_lr = Path(__file__).parent.joinpath("model_lr.pkl")

    create_model(iris_data, model_dt, pickle_file_dt)
    create_model(iris_data, model_lr, pickle_file_lr)


if __name__ == "__main__":
    main()
