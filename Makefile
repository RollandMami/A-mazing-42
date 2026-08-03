ENV = venv
BIN = $(ENV)/bin
PYTHON = $(BIN)/python3
PIP = $(BIN)/pip
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
	@python3 -m venv $(ENV)
	@$(PIP) install --upgrade -q pip
	@echo venv created successfully...

install: $(ENV)
	@echo installing packages...
	@$(PIP) install --find-links=. -q -r requirements.txt
	@$(PIP) install -q -e src/
	@echo Packages installed...

run: install
	@echo A maze is runing...
	@$(PYTHON) $(MAIN) $(CFG)

debug:
	@$(PYTHON) -m pdb $(MAIN) $(CFG)

clean:
	@$(RM) .mypy_cache/ .pytest_cache/
	@find . -type d -name "__pycache__" -exec $(RM) {} +
	@find . -type f -name "*.pyc" -delete
	@echo clean up successful

lint:
	@$(BIN)/flake8 . --exclude=$(ENV)
	@$(BIN)/mypy . $(LFLAGES) --exclude '^$(ENV)/'

lint-strict:
	@$(BIN)/flake8 . --exclude=$(ENV)
	@$(BIN)/mypy . $(LFLAGES) $(STRICT) --exclude '^$(ENV)/'

.PHONY: all install run test clean fclean lint
