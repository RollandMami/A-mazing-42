ENV = env/
ifeq ($(OS),Windows_NT)
    PYTHON = python
    BIN = $(ENV)/Scripts
    RM = rd /s /q
    MKDIR = mkdir
    SEP = \\
	activation:
		$(BIN)/activate
else
    PYTHON = python3
    BIN = $(ENV)/bin
    RM = rm -rf
    MKDIR = mkdir -p
    SEP = /
	activation:
		source $(BIN)/activate
endif
CFG = config.txt
MAIN = a_maze_ing.py
LFLAGES = --warn-return-any\
		  --warn-unused-ignores\
		  --ignore-missing-imports\
		  --disallow-untyped-defs\
		  --check-untyped-defs
STRICT =  --strict

$(ENV):
	$(PYTHON) -m env $(ENV)
	$(BIN)/$(PYTHON) -m pip install 

install: $(ENV)
	$(PIP) install -r requirements.txt

run: install
	$(BIN)/$(PYTHON)  $(MAIN) $(CFG)

debug:
	$(BIN)/$(PYTHON) -m pdb $(MAIN) $(CFG) 

clean:
	$(RM) *__pycache__/*
	$(RM) -rf *.mypy_cache/*

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(LFLAGES)

lint-strict:
	$(PYTHON) -m flake8 . $(STRICT)
	$(PYTHON) -m mypy . $(STRICT)
