model_name=SenseChat-5-Vision # custom name for model
split=val # choose from [val, test]
mode=descriptive # choose from [reasoning, descriptive]
model_path=SenseChat-5-Vision # path to the model weights
model_api=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyYW5mT09vckloTWZ4eFk3WHM2eFZCdkVHcHciLCJleHAiOjE3MzQ3OTA4MDQsIm5iZiI6MTczMzkyNjc5OX0.ELX3rHqNHqBbKic3HyBXxpzUGKt14orSay-RKFUIm-U

 # API key IFF testing proprietary models

### generate response for open-weight models ###
# python src/generate.py \
#     --model_name $model_name \
#     --split $split \
#     --mode $mode \
#     --model_path $model_path 

### generate response for proprietary models ###
python src/generate.py \
    --model_name $model_name \
    --split $split \
    --mode $mode \
    --model_path $model_path \
    --model_api $model_api
