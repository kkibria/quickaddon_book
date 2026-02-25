mdbook build
Set-Location gh-pages
git add .
git commit -m "deploy"
git push origin gh-pages
Set-Location ..