import os
import modal

LOCAL = True

if LOCAL == False:
    stub = modal.Stub()
    hopsworks_image = modal.Image.debian_slim().pip_install(
        ["hopsworks==3.0.4", "joblib", "seaborn", "sklearn", "dataframe-image"])


    @stub.function(image=hopsworks_image, schedule=modal.Period(days=1),
                   secret=modal.Secret.from_name("HOPSWORKS_API_KEY"))
    def f():
        g()


def g():
    import pandas as pd
    import hopsworks
    import joblib
    import datetime
    from PIL import Image
    from datetime import datetime
    import dataframe_image as dfi
    from sklearn.metrics import confusion_matrix
    from matplotlib import pyplot
    import seaborn as sns
    import requests

    project = hopsworks.login()
    fs = project.get_feature_store()

    mr = project.get_model_registry()
    model = mr.get_model("titanic_survival_modal", version=1)
    model_dir = model.download()
    model = joblib.load(model_dir + "/titanic_model.pkl")

    feature_view = fs.get_feature_view(name="titanic_survival_modal", version=1)
    batch_data = feature_view.get_batch_data()

    y_pred = model.predict(batch_data)
    # print(y_pred)
    offset = 1
    person = y_pred[y_pred.size - offset]
    print("Survival predicted: " + person)


    tit_fg = fs.get_feature_group(name="titanic_survival_modal", version=1)
    df = tit_fg.read()
    # print(df)
    label = df.iloc[-offset]["survived"]

    print("Survival actual: " + label)

    monitor_fg = fs.get_or_create_feature_group(name="titanic_predictions",
                                                version=1,
                                                primary_key=["datetime"],
                                                description="Survivals Prediction/Outcome Monitoring"
                                                )

    now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    data = {
        'prediction': [person],
        'label': [label],
        'datetime': [now],
    }
    monitor_df = pd.DataFrame(data)
    monitor_fg.insert(monitor_df, write_options={"wait_for_job": False})

    history_df = monitor_fg.read()
    # Add our prediction to the history, as the history_df won't have it -
    # the insertion was done asynchronously, so it will take ~1 min to land on App
    history_df = pd.concat([history_df, monitor_df])

    df_recent = history_df.tail(4)


   # dfi.export(df_recent, './df_recent.png', table_conversion='matplotlib')
   # dataset_api.upload("./df_recent.png", "Resources/images", overwrite=True)


    predictions = history_df[['prediction']]
    labels = history_df[['label']]

    # Only create the confusion matrix when our iris_predictions feature group has examples of all 3 iris flowers
    print("Number of different people predictions to date: " + str(predictions.value_counts().count()))
    if predictions.value_counts().count() == 3:
        results = confusion_matrix(labels, predictions)

        df_cm = pd.DataFrame(results, ['True Survived', 'True Deceased'],
                             ['Pred Survived', 'Pred Deceased'])

        cm = sns.heatmap(df_cm, annot=True)
      
    else:
        print("You need 3 different flower predictions to create the confusion matrix.")
        print("sb")


if __name__ == "__main__":
    if LOCAL == True:
        g()
    else:
        with stub.run():
            f()