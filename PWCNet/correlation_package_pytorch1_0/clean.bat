echo "Need pytorch>=1.0.0"
ECHO source activate pytorch1.0.0

rmdir /S /Q build
rmdir /S /Q correlation_cuda.egg-info
rmdir /S /Q dist
REM python setup.py install
