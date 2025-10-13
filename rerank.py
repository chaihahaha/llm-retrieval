import requests
import json

URL = "http://127.0.0.1:5678"

payload = {
    "model": "M",
    "query": "What is the recipe to make bread ?",
    "return_text": True,
    "top_n": 6,
    "documents": [
        "voici la recette pour faire du pain, il faut de la farine de l eau et du levain et du sel",
        "it is a bear",
        "bread recipe : floor, water, yest, salt",
        "The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.",
        "here is the ingedients to bake bread : 500g floor, 350g water, 120g fresh refresh yest, 15g salt",
        "recipe to make cookies : floor, eggs, water, chocolat",
        "here is the recipe to make bread : 500g floor, 350g water, 120g fresh refresh yest, 15g salt",
        "il fait tres beau aujourd hui",
        "je n ai pas faim, je ne veux pas manger",
        "je suis a paris"
    ]
}

response = requests.post(
    f"{URL}/v1/rerank",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)

# 打印响应内容
print(response.text)

