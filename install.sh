curl -kL https://raw.github.com/saghul/pythonz/master/pythonz-install | bash

[[ -s $HOME/.pythonz/etc/bashrc ]] && source $HOME/.pythonz/etc/bashrc

pythonz install 2.6.9

curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.4.tar.gz

tar xvfz virtualenv-1.11.4.tar.gz

~/.pythonz/pythons/CPython-2.6.9/bin/python virtualenv-1.11.4/virtualenv.py python2.6.9

source python2.6.9/bin/activate

wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py

python get-pip.py

./python2.6.9/bin/pip install -r requirements.txt

rm -rf virtualenv-1.11.4.tar.gz virtualenv-1.11.4 get-pip.py
