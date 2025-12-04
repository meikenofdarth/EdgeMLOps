// Jenkinsfile (Final, Robust Version)
pipeline {
    // This 'agent' block is the key change.
    agent {
        // It tells Jenkins to build a temporary agent from a Dockerfile.
        dockerfile {
            filename 'Dockerfile.jenkins' // Use the build environment we just defined
            // This is crucial: it passes the Docker socket from the Jenkins server
            // into our temporary build agent, allowing it to run docker commands.
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        // --- YOUR DOCKER HUB USERNAME ---
        DOCKERHUB_USERNAME = 'smoothlake67'
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
                // We are already in a container with Python installed.
                sh 'pip install -r requirements.txt'
                sh 'python3 -m unittest discover tests'
            }
        }

        stage('Build Docker Image') {
            steps {
                // Standard docker build command.
                sh "docker build -t ${IMAGE_NAME} ."
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