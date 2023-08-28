from io import BytesIO
from django.shortcuts import render
from django.db import connections
from rest_framework.decorators import api_view
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from post.models import Post
from stats.serializers import ImageSerializer
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import tensorflow as tf
from tkinter import Tk, filedialog
from ultralytics import YOLO
from PIL import Image, ImageDraw
import os
import boto3
from boto3.s3.transfer import TransferConfig
from uuid import uuid4

bucket_name = '2023-lamba-bucket'
folder_name = 'test_folder/'

current_file_path = os.path.dirname(os.path.abspath(__file__))
best_file_path = os.path.join(current_file_path, 'best.pt')
# # best_file_path_in_aws = 'https://2023-lamba-bucket.s3.ap-southeast-1.amazonaws.com/best.pt'
# inception_file_path = os.path.join(current_file_path, 'Inception.h5')

model = YOLO(best_file_path)
# model_detect = load_model(inception_file_path)

def detect_objects_on_image(buf, model, output_folder):
    s3 = boto3.client('s3')
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
        cropped_image.save(f"{output_folder}/{result.names[class_id]}_{prob}.jpeg")
        # print(type(cropped_image))
        


    # Draw bounding boxes on the original image
    image = Image.open(buf)
    draw = ImageDraw.Draw(image)
    for box in output:
        x1, y1, x2, y2, _, _ = box
        draw.rectangle([x1, y1, x2, y2], outline='red', width=2) # type: ignore
    image.save(f'{output_folder}/annotated_image.jpeg')
    return output, image


@api_view(['GET'])
def test_module(request):
    print(model)
    return Response({'message': f'File uploaded successfully! {model}'})


def read_images_from_folder(folder_path):
    s3_client = boto3.client(
        's3', 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    image_list = []
    for filename in os.listdir(folder_path):
        random_uuid = uuid4()
        s3_file_path = f'test_folder/{random_uuid}{filename}'
        s3_address = f'https://2023-lamba-bucket.s3.ap-southeast-1.amazonaws.com/{s3_file_path}'

        if filename.endswith(".jpeg"):  # You can adjust the file extension
            image_path = os.path.join(folder_path, filename)
            with open(image_path,  "rb") as image_file:
                image_data = image_file.read()
                s3_client.upload_fileobj(image_file, bucket_name, s3_file_path)
            image_list.append(s3_address)
    return image_list


@api_view(['POST'])
def multi_leaves_classification(request):
    input_image = None
    # step 1 upload an image with multiple leaves
    if request.method == 'POST':
        input_image = request.FILES.get('file')

        output_folder = "stats/test_folder"
        detected_objects, annotated_image = detect_objects_on_image(input_image, model, output_folder)
        images = read_images_from_folder(output_folder)
        
        return Response({
            'message': 'files uploaded to s3',
            'files': images
            }
        )
        
        # upload image to s3

        # return the list of images and mark as annotated or cropped
    
    return Response({'message': f'{request.method} method not valid. Try to use POST '})


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
