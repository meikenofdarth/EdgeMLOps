// Jenkinsfile (Final Version with Workspace Fix)
pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME = 'smoothlake67'
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/edge-mlops-mini"
    }

    stages {
        // --- THIS IS THE NEW, CRITICAL STAGE ---
        stage('Prepare Workspace') {
            steps {
                // The checkout happens as root, so we give ownership back to the 'jenkins' user
                // so that all subsequent plugin steps work correctly.
                sh 'chown -R jenkins:jenkins .'
            }
        }
        // ------------------------------------------

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
                        // The 'push()' method is cleaner and more reliable
                        customImage.push('latest')
                    }
                }
            }
        }
    }
}