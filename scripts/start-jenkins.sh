#!/bin/sh

#: starts the Jenkins server
java -jar jenkins.war > logs/jenkin.std 2> logs/jenkins.err &
