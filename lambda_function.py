import boto3
import os
import urllib.parse
from PIL import Image
import io

s3 = boto3.client('s3')

#bucket where the resized image will be saved
dest_bucket = os.environ['DESTINATION_BUCKET']

#only process files with these extensions
allowed_extension = ['.jpg', '.jpeg', '.png']

def lambda_handler(event, context):
	#get bucket name and file name from the event that triggered this
	bucket_name = event['Records'][0]['s3']['bucket']['name']

	#get file name
	raw_file_name = event['Records'][0]['s3']['object']['key']
	#fix space prob
	file_name = urllib.parse.unquote_plus(raw_file_name)

	print("New File Uploaded: ", file_name)

	#check file extension before doing anything
	ext = os.path.splitext(file_name)[1].lower()
	if ext not in allowed_extension:
		print("Skipping non-image file: ", file_name)
		return

	try:
		#download the image from s3
		file_obj= s3.get_object(Bucket=bucket_name, Key=file_name)
		img_data = file_obj['Body'].read()

		#open image
		img = Image.open(io.BytesIO(img_data))

		#resize image to a fixed width, keeping ratio same
		new_width = 800
		ratio = new_width/img.width
		new_height = int(img.height * ratio)
		resized_img = img.resize((new_width, new_height))

		#save resized image into memory
		buffer = io.BytesIO()
		img_format = img.format if img.format else 'JPEG'
		resized_img.save(buffer, format=img_format, quality=70)
		buffer.seek(0)

		#upload the resized image to the destination bucket
		s3.put_object(Bucket=dest_bucket, Key=file_name, Body=buffer)

		print("Image processed and uploaded successfully: ", file_name)

	except Exception as e:
		print("Something went wrong: ", e)


