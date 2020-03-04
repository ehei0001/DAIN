echo "Need pytorch>=1.0.0"
#source activate pytorch1.0.0

rmdir /S /Q build
rmdir /S /Q correlation_cuda.egg-info
rmdir /S /Q dist
python.exe setup.py install
