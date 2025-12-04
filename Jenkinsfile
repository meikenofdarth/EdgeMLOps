// Jenkinsfile (Simplified and Final Version)
pipeline {
    // We can go back to 'agent any' because the agent now has all the tools we need.
    agent any

    environment {
        DOCKERHUB_USERNAME = 'smoothlake67'
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/edge-mlops-mini"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // We need to install Python dependencies, but Python is not in the new image.
        // Let's keep the test stage inside a Python container for cleanliness.
        stage('Run Automated Tests') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh 'pip install -r requirements.txt'
                        sh 'python -m unittest discover tests'
                    }
                }
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    // Build the application image
                    def customImage = docker.build(IMAGE_NAME, '.')
                    
                    // Push the image using the credentials
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        customImage.push()
                    }
                }
            }
        }
    }
}