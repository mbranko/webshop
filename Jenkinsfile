#!/usr/bin/groovy
pipeline {
//   agent { label 'master' }
//   agent { docker { image 'python:3.7.7' } }
  stages {
    stage('checkout code') {
      steps {
        git url: 'https://github.com/mbranko/webshop.git'
      }
    }
    stage('create virtual env') {
      steps {
        sh '''
          cd backend
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
          deactivate
        '''
      }
    }
    stage('collect static files') {
      steps {
        sh '''
          cd backend
          source venv/bin/activate
          python manage.py collectstatic --noinput
          deactivate
        '''
      }
    }
    stage('test') {
      steps {
        sh '''
          cd backend
          source venv/bin/activate
          pytest  --junitxml=reports/junit.xml
          deactivate
        '''
        junit 'reports/junit.xml'
      }
    }
  }
}
