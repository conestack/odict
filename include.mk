##############################################################################
# codict - Cython extension
##############################################################################

CODICT_TARGET:=$(SENTINEL_FOLDER)/codict.sentinel
$(CODICT_TARGET): $(PACKAGES_TARGET)
	@echo "Building Cython codict extension"
	@hatch build
	@touch $(CODICT_TARGET)

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

INSTALL_TARGETS+=$(CODICT_TARGET)
DIRTY_TARGETS+=codict-dirty
CLEAN_TARGETS+=codict-clean
