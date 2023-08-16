from django.shortcuts import render
from django.db import connections
from rest_framework.decorators import api_view
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from post.models import Post
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import tensorflow as tf
from tkinter import Tk, filedialog
from ultralytics import YOLO
from PIL import Image, ImageDraw
import os

current_file_path = os.path.dirname(os.path.abspath(__file__))
best_file_path = os.path.join(current_file_path, 'best.pt')
# # best_file_path_in_aws = 'https://2023-lamba-bucket.s3.ap-southeast-1.amazonaws.com/best.pt'
inception_file_path = os.path.join(current_file_path, 'Inception.h5')

model = YOLO(best_file_path)
model_detect = load_model(inception_file_path)

def detect_objects_on_image(buf, model, output_folder):
    """
    Function receives an image,
    passes it through YOLOv8 neural network
    and returns an array of detected objects
    and their bounding boxes.
    It also crops and saves each detected object
    to the output_folder.

    :param buf: Input image file stream
    :param model: YOLOv8 model
    :param output_folder: Folder to save cropped images
    :return: Array of bounding boxes in format
    [[x1,y1,x2,y2,object_type,probability],..]
    """
    temp_image = Image.open(buf)
    model = model
    results = model.predict(temp_image)
    result = results[0]
    output = []
    for box in result.boxes:
        x1, y1, x2, y2 = [
            round(x) for x in box.xyxy[0].tolist()
        ]
        class_id = box.cls[0].item()
        prob = round(box.conf[0].item(), 2)
        output.append([
            x1, y1, x2, y2, result.names[class_id], prob
        ])

        # Crop and save the detected object
        cropped_image = temp_image.crop((x1, y1, x2, y2))
        cropped_image.save(f"{output_folder}/{result.names[class_id]}_{prob}.jpg")

    # Draw bounding boxes on the original image
    image = Image.open(buf)
    draw = ImageDraw.Draw(image)
    for box in output:
        x1, y1, x2, y2, _, _ = box
        draw.rectangle([x1, y1, x2, y2], outline='red', width=2) # type: ignore

    return output, image

def detect_images_folder(folder_path, model):

    labels = ['Gray Leaf Spot', 'Common Rust', 'Healthy', 'Blight']
    detected = []

    for leaf in os.listdir(folder_path):
        img = image.load_img(os.path.join(folder_path, leaf), target_size=(180, 180))
        x = image.img_to_array(img)
        x = x / 255.0
        x = tf.expand_dims(x, axis=0)
        prediction = model.predict(x)

        predicted_class_index = tf.argmax(prediction, axis=1).numpy()[0]
        confidence = prediction[0][predicted_class_index]
        print(confidence)
        if confidence >= 0.5:
            detected_label = labels[predicted_class_index]
            detected.append(detected_label)
        else:
            detected.append("Unknown")  # If confidence < 0.5, label as "Unknown"

    return detected

@api_view(['GET'])
def test_module(request):
    print(model)
    return Response({'message': f'File uploaded successfully! {model}'})
    

@api_view(['POST'])
def multi_leaves_classification(request: HttpRequest):
    input_image = None
    # step 1 upload an image with multiple leaves
    if request.method == 'POST':
        input_image = request.FILES.get('file')

        output_folder = "stats/test_folder"
        detected_objects, annotated_image = detect_objects_on_image(input_image, model, output_folder)
        # detect_images_folder(output_folder, model_detect)


        for f in os.listdir(output_folder):
            os.remove(os.path.join(output_folder, f))
    return Response({'message': f'File uploaded successfully! {model} {input_image}'})



@api_view(["GET"])
def get_all_stats(request, user_id):
    blight_count = (
        Post.objects.filter(blight=True, author=user_id)
        .annotate(total=Count("id"))
        .count()
    )
    rust_count = Post.objects.filter(rust=True, author=user_id).count()
    gray_leaf_spot_count = Post.objects.filter(
        gray_leaf_spot=True, author=user_id
    ).count()
    healthy_count = Post.objects.filter(healthy=True, author=user_id).count()
    other_count = Post.objects.filter(other=True, author=user_id).count()
    return Response(
        {
            "blight_count": blight_count,
            "rust_count": rust_count,
            "gray_leaf_spot_count": gray_leaf_spot_count,
            "healthy_count": healthy_count,
            "other_count": other_count,
        }
    )


@api_view(["GET"])
def get_stats_per_day(request, user_id, date):
    blight_count = Post.objects.filter(
        blight=True, author=user_id, date_posted=date
    ).count()
    rust_count = (
        Post.objects.filter(rust=True, author=user_id, date_posted=date)
        .annotate(total=Count("id"))
        .count()
    )
    gray_leaf_spot_count = (
        Post.objects.filter(gray_leaf_spot=True, author=user_id, date_posted=date)
        .annotate(total=Count("id"))
        .count()
    )
    healthy_count = (
        Post.objects.filter(healthy=True, author=user_id, date_posted=date)
        .annotate(total=Count("id"))
        .count()
    )
    other_count = (
        Post.objects.filter(other=True, author=user_id, date_posted=date)
        .annotate(total=Count("id"))
        .count()
    )
    return Response(
        {
            "blight_count": blight_count,
            "rust_count": rust_count,
            "gray_leaf_spot_count": gray_leaf_spot_count,
            "healthy_count": healthy_count,
            "other_count": other_count,
        }
    )


@api_view(["GET"])
def get_farmer_all_stats(request, user_id):
    blight_count = (
        Post.objects.filter(blight=True, author=user_id, is_classification=True)
        .annotate(total=Count("id"))
        .count()
    )
    rust_count = Post.objects.filter(
        rust=True, author=user_id, is_classification=True
    ).count()
    gray_leaf_spot_count = Post.objects.filter(
        gray_leaf_spot=True, author=user_id, is_classification=True
    ).count()
    healthy_count = Post.objects.filter(
        healthy=True, author=user_id, is_classification=True
    ).count()
    other_count = Post.objects.filter(
        other=True, author=user_id, is_classification=True
    ).count()
    return Response(
        {
            "blight_count": blight_count,
            "rust_count": rust_count,
            "gray_leaf_spot_count": gray_leaf_spot_count,
            "healthy_count": healthy_count,
            "other_count": other_count,
        }
    )


@api_view(["GET"])
def get_farmer_stats_per_day(request, user_id, date):
    blight_count = Post.objects.filter(
        blight=True, author=user_id, date_posted=date, is_classification=True
    ).count()
    rust_count = (
        Post.objects.filter(
            rust=True, author=user_id, date_posted=date, is_classification=True
        )
        .annotate(total=Count("id"))
        .count()
    )
    gray_leaf_spot_count = (
        Post.objects.filter(
            gray_leaf_spot=True,
            author=user_id,
            date_posted=date,
            is_classification=True,
        )
        .annotate(total=Count("id"))
        .count()
    )
    healthy_count = (
        Post.objects.filter(
            healthy=True, author=user_id, date_posted=date, is_classification=True
        )
        .annotate(total=Count("id"))
        .count()
    )
    other_count = (
        Post.objects.filter(
            other=True, author=user_id, date_posted=date, is_classification=True
        )
        .annotate(total=Count("id"))
        .count()
    )
    return Response(
        {
            "blight_count": blight_count,
            "rust_count": rust_count,
            "gray_leaf_spot_count": gray_leaf_spot_count,
            "healthy_count": healthy_count,
            "other_count": other_count,
        }
    )
