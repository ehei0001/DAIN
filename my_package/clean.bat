echo "Need pytorch>=1.0.0"
REM source activate pytorch1.0.0

cd MinDepthFlowProjection
rmdir /S /Q build
rmdir /S /Q MinDepthFlowProjection_egg-info
rmdir /S /Q dist
REM python setup.py install
cd ..

cd FlowProjection
rmdir /S /Q build
rmdir /S /Q FlowProjection_egg-info
rmdir /S /Q dist
REM python setup.py install
cd ..

cd SeparableConv
rmdir /S /Q build
rmdir /S /Q SeparableConv_egg-info
rmdir /S /Q dist
REM python setup.py install
cd ..

cd InterpolationCh
rmdir /S /Q build
rmdir /S /Q InterpolationCh_egg-info
rmdir /S /Q dist
REM python setup.py install
cd ..

cd DepthFlowProjection
rmdir /S /Q build
rmdir /S /Q DepthFlowProjection_egg-info
rmdir /S /Q dist
REM python setup.py install
cd ..

cd Interpolation
rmdir /S /Q build
rmdir /S /Q Interpolation_egg-info
rmdir /S /Q dist
REM python setup.py install
cd ..

cd SeparableConvFlow
rmdir /S /Q build
rmdir /S /Q SeparableConvFlow_egg-info
rmdir /S /Q dist
REM python setup.py install
cd ..

cd FilterInterpolation
rmdir /S /Q build
rmdir /S /Q FilterInterpolation_egg-info
rmdir /S /Q dist
REM python setup.py install
cd ..

