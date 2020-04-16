pipeline {
  agent any
  environment {
    DISABLE_AUTH = 'true'
  }
  stages {
    stage('build') {
      steps {
        sh 'find --version'
      }
    }
    stage('build2') {
      steps {
        sh 'printenv'
      }
    }
  }
}
