ENV = env/
PYTHON = python3
BIN = $(ENV)/bin
RM = rm -rf
MKDIR = mkdir -p

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
	$(RM) .mypy_cache/ .pytest_cache/
	find . -type d -name "__pycache__" -exec $(RM) {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(LFLAGES)

lint-strict:
	$(PYTHON) -m flake8 . $(STRICT)
	$(PYTHON) -m mypy . $(STRICT)

.PHONY: all install run test clean fclean lint
