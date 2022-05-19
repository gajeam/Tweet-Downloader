# Getting Started

1) In order to run this program, you're going to ned Python 3.10.4. You can download this from the [Python website](https://www.python.org/downloads/release/python-3104/), or if you ever need to run multiple versions of Python, you can use **pyenv**. (You can find a good setup guide for Mac [here.](https://opensource.com/article/19/5/python-3-default-mac))

2) You'll need the Python package installer **pip** for this to work too. [Get that.](https://pip.pypa.io/en/stable/installation/)

3) The last thing you'll need to install is **pipenv**. This lets you manage the different packages, which are listed in `Pipfile`.

4) Once you have all these, from this directory, run `pipenv shell`. This should install all the packages you need and create a virtual environment from which you can run the program. You can exit out of this with the command `exit`

5) In the same directory, you're going to want to create a file called `bearer_token.txt`. This is where you will paste your [Twitter bearer token.](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens) You will need access to the Twitter Academic API for this program to work.

6) You're all set! Run the program with `python dwld_profile_URL_media.py` All the data generated will appear in the `data/` directory.