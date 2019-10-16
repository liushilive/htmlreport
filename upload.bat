python setup.py sdist bdist_wheel

twine upload dist/*

pause

rmdir /S /Q build
rmdir /S /Q dist
rmdir /S /Q HTMLReport.egg-info
