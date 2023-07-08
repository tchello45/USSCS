python3 usscs/setup.py sdist bdist_wheel
pip3 install dist/usscs-3.0.0-py3-none-any.whl --force-reinstall
python3 usscs_enc/setup.py sdist bdist_wheel
pip3 install dist/usscs_enc-3.0.0-py3-none-any.whl --force-reinstall
rm -r dist
rm -r build
rm -r usscs.egg-info
rm -r usscs_enc.egg-info