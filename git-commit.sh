#!/bin/bash

git add .
git commit -m "$1"

git push origin main
git log --oneline -n 5