pipeline {
  agent {
    docker 'python:3.5.1'
  }
  environment {
    DISABLE_AUTH = 'true'
  }
  stages {
    stage('build') {
      steps {
        sh 'python --version'
      }
    }
    stage('Build') {
      steps {
        sh 'npm install'
      }
    }
    stage('build2') {
      steps {
        sh 'printenv'
      }
    }
  }
}
