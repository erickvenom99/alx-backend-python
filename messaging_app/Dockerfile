# Use the specified base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
# This is done first to leverage Docker's build cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
# This copies everything from the messaging_app directory into /usr/src/app
COPY . .

# Expose the port your Django app runs on (default is 8000)
EXPOSE 8000

# Set the default command to run the Django development server
# Replace 'your_project_name' with the actual name of your Django project folder 
# (e.g., if you have manage.py and an inner 'myproject' folder, use 'myproject')
# You may need to adjust the runserver binding to 0.0.0.0 for container access.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]