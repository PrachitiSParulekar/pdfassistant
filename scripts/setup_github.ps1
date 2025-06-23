# GitHub Setup Script for PDF Assistant
# Run this after creating your GitHub repository

# Step 1: Add your GitHub repository as remote
Write-Host "Setting up GitHub remote..." -ForegroundColor Green
$username = "PrachitiSParulekar"
$reponame = "pdfassistant"

git remote add origin "https://github.com/$username/$reponame.git"

# Step 2: Rename branch to main (GitHub's default)
Write-Host "Renaming branch to main..." -ForegroundColor Green
git branch -M main

# Step 3: Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Green
git push -u origin main

Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "Your repository is now available at: https://github.com/$username/$reponame" -ForegroundColor Cyan
