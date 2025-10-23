##############################################################################
# codict - Cython extension
##############################################################################

# Flag whether to build Cython extensions
# Default: true
BUILD_CODICT?=true

CODICT_TARGET:=$(SENTINEL_FOLDER)/codict.sentinel
$(CODICT_TARGET): $(PACKAGES_TARGET)
ifeq ("$(BUILD_CODICT)", "true")
	@echo "Building Cython codict extension"
	@$(MXENV_PYTHON) setup.py build_ext --inplace
	@touch $(CODICT_TARGET)
else
	@echo "Skipping Cython codict extension build"
	@touch $(CODICT_TARGET)
endif

.PHONY: codict
codict: $(CODICT_TARGET)

.PHONY: codict-dirty
codict-dirty:
	@rm -f $(CODICT_TARGET)

.PHONY: codict-clean
codict-clean: codict-dirty
	@echo "Cleaning Cython build artifacts"
	@rm -f src/odict/codict.c
	@rm -f src/odict/*.so
	@rm -f src/odict/*.pyd
	@rm -rf build/
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

INSTALL_TARGETS+=$(CODICT_TARGET)
DIRTY_TARGETS+=codict-dirty
CLEAN_TARGETS+=codict-clean
