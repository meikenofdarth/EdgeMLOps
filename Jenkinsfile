// Jenkinsfile
pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME = 'smoothlake67' // <--- CHANGE THIS
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/edge-mlops-mini"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

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

        stage('Build Docker Image') {
            steps {
                script {
                    // We need to pass the Dockerfile's location to the build command
                    def customImage = docker.build(IMAGE_NAME, '.')
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh "echo ${PASS} | docker login -u ${USER} --password-stdin"
                    sh "docker push ${IMAGE_NAME}:latest"
                    sh "docker logout"
                }
            }
        }
    }
}