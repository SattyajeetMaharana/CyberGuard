"""
CyberGuard — Account Takeover Model Hyperparameters

Selected v1 configuration based on controlled evaluation.
"""

MODEL_NAME = "account-takeover-xgboost"
MODEL_VERSION = "account-takeover-xgboost-v1"

RANDOM_STATE = 42

XGBOOST_PARAMS = {
    "n_estimators": 300,
    "max_depth": 3,
    "learning_rate": 0.03,
    "subsample": 0.80,
    "colsample_bytree": 0.80,
    "min_child_weight": 5,
    "gamma": 0.10,
    "reg_alpha": 0.10,
    "reg_lambda": 2.0,
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
    "tree_method": "hist",
}