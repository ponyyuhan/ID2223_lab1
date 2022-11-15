import os
import modal

LOCAL=False

if LOCAL == False:
   stub = modal.Stub()
   image = modal.Image.debian_slim().pip_install(["hopsworks==3.0.4"]) 

   @stub.function(image=image, schedule=modal.Period(days=1), 
                  secret=modal.Secret.from_name("HOPSWORKS_API_KEY"))
   def f():
       g()


def generate_titanic(survived, pclass_num_min, pclass_num_max, sex_male, sex_female, 
                    age_max, age_min, sibsp_min, sibsp_max,parch_min,parch_max,embarked_min,
                     embarked_max,fare_per_customer_max,fare_per_customer_min,cabin_none,cabin_one):
    """
    Returns a single iris flower as a single row in a DataFrame
    """
    import pandas as pd
    import random

    df = pd.DataFrame({ "pclass": [random.randint(pclass_num_min, pclass_num_max)],
                       "sex": [random.randint(sex_male, sex_female)],
                       "age": [random.uniform(age_max, age_min)],
                       "sibsp": [random.randint(sibsp_min, sibsp_max)],
                       "parch":[random.randint(parch_min,parch_max)],
                       "embarked":[random.randint(embarked_min,embarked_max)],
                       "fare_per_customer":[random.uniform(fare_per_customer_max,fare_per_customer_min)],
                       "cabin":[random.randint(cabin_none,cabin_one)]
                      })
    df['survived'] = survived
    return df


def get_random_titanic():
    """
    Returns a DataFrame containing one random iris flower
    """
    import pandas as pd
    import random

    survived_df = generate_titanic("S", 1, 4, 1, 2, 30, 0, 0, 5,0,6,1,4,0,200,1,2)
    deceased_df = generate_titanic("D", 1, 4, 0, 1, 80, 50, 0, 5,0,6,1,4,0,200,0,1)

    pick_random = random.uniform(0,2)
    if pick_random >= 1:
        titanic_df = survived_df
        print("Survived added")
    else:
        titanic_df = deceased_df
        print("Deceased added")

    return titanic_df


def g():
    import hopsworks
    import pandas as pd

    project = hopsworks.login()
    fs = project.get_feature_store()

    titanic_df = get_random_titanic()

    titanic_fg = fs.get_feature_group(name="titanic_survival_modal",version=1)
    titanic_fg.insert(titanic_df, write_options={"wait_for_job" : False})

if __name__ == "__main__":
    if LOCAL == True :
        g()
    else:
        with stub.run():
            f()
