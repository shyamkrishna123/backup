pipeline {
  agent any
  stages {
    stage('build') {
      parallel {
        stage('build') {
          steps {
            echo 'ho man'
          }
        }

        stage('dbuild') {
          steps {
            echo 'ho2'
          }
        }

      }
    }

    stage('test') {
      parallel {
        stage('test') {
          steps {
            echo 'test'
          }
        }

        stage('unit test') {
          steps {
            echo 'mole'
          }
        }

      }
    }

  }
}