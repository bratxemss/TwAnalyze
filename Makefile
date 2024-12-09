VIRTUAL_ENV     ?= venv
PROJECT         ?= Main

all: $(VIRTUAL_ENV)

.PHONY: run
run: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python -m $(PROJECT) -run

.PHONY: init_db
init_db: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python -m $(PROJECT) -init_db