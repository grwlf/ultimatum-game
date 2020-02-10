.DEFAULT_GOAL = all
SRC = $(shell find src -name '*\.py')

.stamp_check: $(SRC) docs/Pylightnix.pmd
	@if ! which pweave >/dev/null 2>&1 ; then \
		echo "pweave not found. Please install it with" ; \
		echo "> sudo -H pip3 install pweave" ; \
		exit 1 ; \
	fi
	touch $@

.PHONY: check
check: .stamp_check

docs/Pylightnix.md: docs/Pylightnix.pmd $(SRC) .stamp_check
	pweave -f markdown $<

docs/Pylightnix.html: docs/Pylightnix.pmd $(SRC) .stamp_check
	pweave -f md2html $<

docs/Pylightnix.py: docs/Pylightnix.pmd $(SRC) .stamp_check
	ptangle $<

.PHONY: demo_pylightnix
demo_pylightnix: docs/Pylightnix.md docs/Pylightnix.py docs/Pylightnix.html


.PHONY: all
all: demo_pylightnix

