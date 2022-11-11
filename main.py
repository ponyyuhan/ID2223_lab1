import gradio as gr
import numpy as np
from PIL import Image
import requests

import hopsworks
import joblib

project = hopsworks.login()
fs = project.get_feature_store()

mr = project.get_model_registry()
model = mr.get_model("titanic_modal_more_specs_grad_boosted", version=1)
model_dir = model.download()
model = joblib.load(model_dir + "/titanic_model.pkl")


def titanic(pclass,sex,age,sibsp,parch,embarked,fare_per_customer,embarked_remapped,cabin_remapped):
    input_list = []
    input_list.append(pclass)
    input_list.append(sex)
    input_list.append(age)
    input_list.append(sibsp)
    input_list.append(parch)
    input_list.append(embarked)
    input_list.append(fare_per_customer)
    input_list.append(embarked_remapped)
    input_list.append(cabin_remapped)
    # 'res' is a list of predictions returned as the label.
    res = model.predict(np.asarray(input_list).reshape(1, -1))
    # We add '[0]' to the result of the transformed 'res', because 'res' is a list, and we only want
    # the first element.

demo = gr.Interface(
    fn=titanic,
    title="Titanic Predictive Analytics",
    description="Predict survivals.",
    allow_flagging="never",
    inputs=[
        gr.inputs.Number(default=1.0, label="pclass"),
        gr.inputs.Number(default=1.0, label="gender(male=0, female=1)"),
        gr.inputs.Number(default=1.0, label="age"),
        gr.inputs.Number(default=1.0, label="sibsp"),
        gr.inputs.Number(default=1.0, label="parch"),
        gr.inputs.Number(default=1.0, label="embarked(C=1,S=2,Q=3)"),
        gr.inputs.Number(default=1.0, label="fare_per_customer"),
        gr.inputs.Number(default=1.0, label="cabin_remapped(if the passanger has one cabin =1, else =0)"),

    ],
    outputs=gr.Image(type="pil"))

demo.launch()