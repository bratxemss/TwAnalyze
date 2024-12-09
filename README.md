**The application will not work on closed and protected profiles -> https://github.com/JustAnotherArchivist/snscrape/issues/996**

Required python 3.12

**HOW TO USE IN LINUX**

**1)Create venv and activate**

* python -m venv venv

* source venv/bin/activate

**2)Install poetry and install requirements.**

* pip install poetry

* poetry install

**3)Init database**

* make init_db

**4)run project**

* make run

**HOW TO USE IN WINDOWS**

**1)Create venv and activate
**
* python -m venv venv

* .\venv\Scripts\activate

**2)Install poetry and install requirements.**

* pip install poetry

* poetry install

**3)Init database**

* python -m Main -init_db

**4) run project**

* python -m Main -run
