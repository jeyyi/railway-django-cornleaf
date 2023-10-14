from rest_framework.decorators import api_view
from django.db.models import Count
from rest_framework.response import Response
from post.models import Post

from ultralytics import YOLO
from PIL import Image, ImageDraw
import os
import boto3
from uuid import uuid4
from io import BytesIO

bucket_name = '2023-lamba-bucket'
folder_name = 'test_folder/'

current_file_path = os.path.dirname(os.path.abspath(__file__))
best_file_path = os.path.join(current_file_path, 'best.pt')

model = YOLO(best_file_path)

def detect_objects_on_image(buf, model, output_folder):
    random_uuid = uuid4()
    s3_client = boto3.client(
        's3', 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    s3_resource = boto3.resource('s3')
    temp_image = Image.open(buf)
    model = model
    results = model.predict(temp_image)
    result = results[0]
    output = []

    image_list = []

    s3_bucket_name = '2023-lamba-bucket'
    s3_url = 'https://2023-lamba-bucket.s3.ap-southeast-1.amazonaws.com/'

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

        in_mem_file_leaf = BytesIO()
        if cropped_image.mode == 'RGBA':
            cropped_image = cropped_image.convert('RGB')
        cropped_image.save(in_mem_file_leaf, format='JPEG')
        image_buffer_body_leaf = in_mem_file_leaf.getvalue()
        in_mem_file_leaf.seek(0)
        key_name = f"{output_folder}/{result.names[class_id]}_{prob}-{random_uuid}.jpeg"
        s3_resource.Bucket(s3_bucket_name).put_object(Key=key_name, Body=image_buffer_body_leaf)
        image_list.append(s3_url+key_name)

    # Draw bounding boxes on the original image
    image = Image.open(buf)
    draw = ImageDraw.Draw(image)
    for box in output:
        x1, y1, x2, y2, _, _ = box
        draw.rectangle([x1, y1, x2, y2], outline='red', width=2) # type: ignore
    

    in_mem_file = BytesIO()
    image.save(in_mem_file, format=image.format)
    image_buffer_body = in_mem_file.getvalue()
    in_mem_file.seek(0)
    key_name = f'{output_folder}/annotated_image-{random_uuid}.jpeg'
    s3_resource.Bucket(s3_bucket_name).put_object(Key=f'{output_folder}/annotated_image-{random_uuid}.jpeg', Body=image_buffer_body)
    image_list.append(s3_url+key_name)

    return output, image, image_list


def read_images_from_folder(folder_path, random_uuid):
    s3_client = boto3.client(
        's3', 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    image_list = []
    for filename in os.listdir(folder_path):
        
        s3_file_path = f'test_folder/{filename}'
        s3_address = f'https://2023-lamba-bucket.s3.ap-southeast-1.amazonaws.com/{s3_file_path}'

        if filename.endswith(f"{random_uuid}.jpeg"):  # You can adjust the file extension
            image_path = os.path.join(folder_path, filename)
            with open(image_path,  "rb") as image_file:
                image_data = image_file.read()
                # s3_client.upload_fileobj(image_file, bucket_name, s3_file_path)
            image_list.append(s3_address)
    return image_list


@api_view(['POST'])
def multi_leaves_classification(request):
    input_image = None
    # step 1 upload an image with multiple leaves
    if request.method == 'POST':
        input_image = request.FILES.get('file')

        output_folder = "test_folder"
        _, _, images = detect_objects_on_image(input_image, model, output_folder)

        # read images from s3
        # images = read_images_from_folder(output_folder, random_uuid)
        # images = []
        
        return Response({
            'message': 'files uploaded to s3',
            'files': images
            }
        )
        
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
